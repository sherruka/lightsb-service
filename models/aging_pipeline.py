import ast
import os.path
import subprocess

from head_detection import head_detector
from ultralytics import YOLO

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def execute_process(command, cwd):
    p = subprocess.Popen(
        command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    p.wait()
    stdout, stderr = p.communicate()
    return stdout


def aging_pipeline(
    filenames, output_path=f"{SCRIPT_PATH}/result", result_count=5, delta=-4
):
    if type(filenames) == str:
        filenames = [filenames]

    filenames = [os.path.abspath(filename) for filename in filenames]

    model = YOLO("yolov11n_weights.pt")
    hd_model = head_detector(model)
    detected_heads = hd_model.predict(filenames)

    output_path = os.path.abspath(output_path)

    aged_people = execute_process(
        f"python ./generator.py --filenames {' '.join(detected_heads)} --output {output_path} --num {result_count} --delta {delta}",
        f"{SCRIPT_PATH}/LightSB/ALAE",
    )
    aged_people = aged_people.decode().split("\n")[-2]
    aged_people = ast.literal_eval(aged_people)
    return aged_people
