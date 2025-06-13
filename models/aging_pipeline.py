import os.path

from generator import generate
from head_detection import head_detector
from ultralytics import YOLO

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def aging_pipeline(
    filenames, output_path=f"{SCRIPT_PATH}/result", result_count=5, delta=-4
):
    if type(filenames) == str:
        filenames = [filenames]

    filenames = [os.path.abspath(filename) for filename in filenames]
    output_path = os.path.abspath(output_path)
    checkpoint_path = f"{SCRIPT_PATH}/yolo11s_weights.pt"

    model = YOLO(checkpoint_path)
    hd_model = head_detector(model)
    detected_heads = hd_model.predict(filenames)

    aged_people = generate(detected_heads, output_path, result_count, delta)

    detected__heads_files = os.scandir(f"{SCRIPT_PATH}/head_detection_results/")
    for file in detected__heads_files:

        if file.is_file() and os.path.exists(file):
            os.remove(file)

    return aged_people


if __name__ == "__main__":
    # for testing purposes
    files = os.scandir("./models/dataset_samples/faces/realign1024x1024")
    for entry in files:
        if entry.is_file() and entry.name.endswith("png"):
            ret = aging_pipeline(entry.path)
            # print(ret)
    # aging_pipeline([file.path for file in files])
