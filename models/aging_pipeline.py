import os.path

from ultralytics import YOLO

from models.generator import generate
from models.head_detection import head_detector

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def aging_pipeline(
    filenames, output_path=f"{SCRIPT_PATH}/result", result_count=5, delta=-4
):
    if type(filenames) == str:
        filenames = [filenames]

    filenames = [os.path.abspath(filename) for filename in filenames]
    output_path = os.path.abspath(output_path)
    checkpoint_path = f"{SCRIPT_PATH}/yolov11n_weights.pt"

    model = YOLO(checkpoint_path)
    hd_model = head_detector(model)
    detected_heads = hd_model.predict(filenames)
    if len(detected_heads) == 0:
        print("no heads was detected on given image")
        return ["no heads was detected on given image"]
    aged_people = generate(detected_heads, output_path, result_count, delta)
    return aged_people


if __name__ == "__main__":
    # for testing purposes
    ret = aging_pipeline("./dataset_samples/faces/realign1024x1024/00152.png")
    print(ret)
