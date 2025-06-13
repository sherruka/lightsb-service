import os

import cv2

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
RESULT_PATH = SCRIPT_PATH + "/head_detection_results/"
BATCH_SIZE = 32


class head_detector:
    def __init__(self, model) -> None:
        self.model = model
        self.names = model.names

    def __call__(self, images):
        return self.predict(images)

    def crop_image_by_bbox(self, image, bbox, offset_scale=0.1):
        x_min, y_min, x_max, y_max = bbox
        offset_x = int(offset_scale * (x_max - x_min))
        offset_y = int(offset_scale * (y_max - y_min))
        h, w, _ = image.shape
        x_min = max(0, x_min - offset_x)
        y_min = max(0, y_min - offset_y)
        x_max = min(h, x_max + offset_x)
        y_max = min(w, y_max + offset_y)
        return image[
            int(y_min) : int(y_max),
            int(x_min) : int(x_max),
        ]

    def predict(self, images_paths) -> list:
        result_images = list()
        if not isinstance(images_paths, list):
            images_paths = [images_paths]
        for j in range(0, len(images_paths), BATCH_SIZE):
            batch_images_paths = images_paths[j : j + BATCH_SIZE]

            images = [cv2.imread(image_path) for image_path in batch_images_paths]
            results = self.model.predict(images, iou=0.2, conf=0.6)

            for i, result in enumerate(results):
                boxes = result.boxes.xyxy.cpu().tolist()
                classes = result.boxes.cls.cpu().tolist()
                if len(boxes):
                    idx = 0
                    for box, cls in zip(boxes, classes):

                        crop_obj = self.crop_image_by_bbox(result.orig_img, box)

                        image_name = batch_images_paths[i].split("/")[-1]
                        cropped_image_path = (
                            RESULT_PATH
                            + ".".join(image_name.split(".")[:-1])
                            + "_"
                            + str(idx)
                            + ".png"
                        )
                        if not os.path.exists(RESULT_PATH):
                            os.mkdir(RESULT_PATH)
                        cv2.imwrite(cropped_image_path, crop_obj)
                        result_images.append(cropped_image_path)
                        idx += 1
                else:
                    print(
                        "no heads was detected on given image, may lead to improper result"
                    )
                    image_name = batch_images_paths[i].split("/")[-1]
                    image_path = (
                        RESULT_PATH + ".".join(image_name.split(".")[:-1]) + ".png"
                    )
                    if not os.path.exists(RESULT_PATH):
                        os.mkdir(RESULT_PATH)
                    cv2.imwrite(image_path, result.orig_img)
                    result_images.append(image_path)
        return result_images
