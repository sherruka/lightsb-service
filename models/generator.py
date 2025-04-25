import argparse
import inspect
import logging
import multiprocessing
import os
import sys

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

sys.path.append(f"{SCRIPT_PATH}/LightSB/ALAE")

import lreq
import torchvision
from checkpointer import Checkpointer
from defaults import get_cfg_defaults
from dlutils.pytorch import count_parameters
from model import Model
from net import *
from PIL import Image

lreq.use_implicit_lreq.set(True)

indices = [4]

labels = ["young"]


def sample(cfg, logger, filenames, result_path, delta, result_num, device):
    model = Model(
        startf=cfg.MODEL.START_CHANNEL_COUNT,
        layer_count=cfg.MODEL.LAYER_COUNT,
        maxf=cfg.MODEL.MAX_CHANNEL_COUNT,
        latent_size=cfg.MODEL.LATENT_SPACE_SIZE,
        truncation_psi=cfg.MODEL.TRUNCATIOM_PSI,
        truncation_cutoff=cfg.MODEL.TRUNCATIOM_CUTOFF,
        mapping_layers=cfg.MODEL.MAPPING_LAYERS,
        channels=cfg.MODEL.CHANNELS,
        generator=cfg.MODEL.GENERATOR,
        encoder=cfg.MODEL.ENCODER,
    )
    model.to(device)
    model.eval()
    model.requires_grad_(False)

    decoder = model.decoder
    encoder = model.encoder
    mapping_tl = model.mapping_d
    mapping_fl = model.mapping_f
    dlatent_avg = model.dlatent_avg

    logger.info("Trainable parameters generator:")
    count_parameters(decoder)

    logger.info("Trainable parameters discriminator:")
    count_parameters(encoder)

    arguments = dict()
    arguments["iteration"] = 0

    model_dict = {
        "discriminator_s": encoder,
        "generator_s": decoder,
        "mapping_tl_s": mapping_tl,
        "mapping_fl_s": mapping_fl,
        "dlatent_avg": dlatent_avg,
    }

    checkpointer = Checkpointer(cfg, model_dict, {}, logger=logger, save=False)

    checkpointer.load()

    model.eval()

    layer_count = cfg.MODEL.LAYER_COUNT

    def encode(x):
        Z, _ = model.encode(x, layer_count - 1, 1)
        Z = Z.repeat(1, model.mapping_f.num_layers, 1)
        return Z

    def decode(x):
        layer_idx = torch.arange(2 * layer_count)[np.newaxis, :, np.newaxis]
        ones = torch.ones(layer_idx.shape, dtype=torch.float32)
        coefs = torch.where(layer_idx < model.truncation_cutoff, ones, ones)
        x = torch.lerp(model.dlatent_avg.buff.data, x, coefs)
        return model.decoder(x, layer_count - 1, 1, noise=True)

    attribute_values = [0.0 for i in indices]
    if result_path == "":
        print("Error: result_path not set")

    W = [
        torch.tensor(
            np.load(
                f"{SCRIPT_PATH}/LightSB/ALAE/principal_directions/direction_%d.npy" % i
            ),
            dtype=torch.float32,
        )
        for i in indices
    ]

    rnd = np.random.RandomState(5)

    def loadImage(filename):
        img = np.asarray(Image.open(filename))

        if img.shape[2] == 4:
            img = img[:, :, :3]
        im = img.transpose((2, 0, 1))
        x = (
            torch.tensor(
                np.asarray(im, dtype=np.float32), device="cpu", requires_grad=True
            ).to(device)
            / 127.5
            - 1.0
        )
        if x.shape[0] == 4:
            x = x[:3]

        needed_resolution = model.decoder.layer_to_resolution[-1]
        while x.shape[2] > needed_resolution:
            x = F.avg_pool2d(x, 2, 2)
        if x.shape[2] != needed_resolution:
            x = F.adaptive_avg_pool2d(x, (needed_resolution, needed_resolution))

        img_src = (
            ((x * 0.5 + 0.5) * 255)
            .type(torch.long)
            .clamp(0, 255)
            .cpu()
            .type(torch.uint8)
            .transpose(0, 2)
            .transpose(0, 1)
            .numpy()
        )

        latents_original = encode(x[None, ...].to(device))
        latents = latents_original[0, 0].clone()
        latents -= model.dlatent_avg.buff.data[0]
        for v, w in zip(attribute_values, W):
            v = (latents * w).sum()

        for v, w in zip(attribute_values, W):
            latents = latents - v * w

        return latents, latents_original, img_src

    def update_image(w, latents_original):
        with torch.no_grad():
            w = w + model.dlatent_avg.buff.data[0]
            w = w[None, None, ...].repeat(1, model.mapping_f.num_layers, 1)

            layer_idx = torch.arange(model.mapping_f.num_layers)[
                np.newaxis, :, np.newaxis
            ]
            cur_layers = (7 + 1) * 2
            mixing_cutoff = cur_layers
            styles = torch.where(layer_idx < mixing_cutoff, w, latents_original)

            x_rec = decode(styles)
            resultsample = ((x_rec * 0.5 + 0.5) * 255).type(torch.long).clamp(0, 255)
            resultsample = resultsample.cpu()[0, :, :, :]
            return resultsample.type(torch.uint8).transpose(0, 2).transpose(0, 1)

    result = []
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for filename in filenames:
        latents, latents_original, img_src = loadImage(filename)

        im_size = 2 ** (cfg.MODEL.LAYER_COUNT + 1)
        im = update_image(latents, latents_original)

        for i in range(result_num):
            for x in range(len(attribute_values)):
                attribute_values[x] += delta
            new_latents = latents + sum([v * w for v, w in zip(attribute_values, W)])

            im = update_image(new_latents, latents_original)

            new_im = torchvision.transforms.functional.to_pil_image(im.permute(2, 0, 1))

            new_im.save(
                f"{result_path}/{'.'.join(filename.split('/')[-1].split('.')[:-1])}_var{i}.png"
            )
            result.append(
                f"{result_path}/{'.'.join(filename.split('/')[-1].split('.')[:-1])}_var{i}.png"
            )
    return result


def generate(filenames, output="", result_count=5, delta=-4):

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device == torch.device("cuda"):
        torch.set_default_tensor_type("torch.cuda.FloatTensor")
    cfg = get_cfg_defaults()
    config_file = f"{SCRIPT_PATH}/LightSB/ALAE/configs/ffhq.yaml"
    if len(os.path.splitext(config_file)[1]) == 0:
        config_file += ".yaml"
    if not os.path.exists(config_file) and os.path.exists(
        os.path.join(f"{SCRIPT_PATH}/LightSB/ALAE/configs", config_file)
    ):
        config_file = os.path.join(f"{SCRIPT_PATH}LightSB/ALAE/configs", config_file)
    cfg.merge_from_file(config_file)
    cfg.freeze()

    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    output_dir = cfg.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info("Loaded configuration file {}".format(config_file))
    with open(config_file, "r") as cf:
        config_str = "\n" + cf.read()
        logger.info(config_str)
    logger.info("Running with config:\n{}".format(cfg))

    args_to_pass = dict(
        cfg=cfg,
        logger=logger,
        filenames=filenames,
        result_path=output,
        delta=delta,
        result_num=result_count,
        device=device,
    )
    signature = inspect.signature(sample)
    matching_args = {}
    for key in args_to_pass.keys():
        if key in signature.parameters.keys():
            matching_args[key] = args_to_pass[key]
    return sample(**matching_args)
