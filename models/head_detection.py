import cv2
from importlib_resources.readers import remove_duplicates
from ultralytics.utils.ops import non_max_suppression
from ultralytics.utils.plotting import Annotator, colors


class head_detector:
    def __init__(self, model) -> None:
        self.model = model
        self.names = model.names

    def __call__(self, images):
        return self.predict(images)

    def remove_duplicates(self, results):
        return non_max_suppression(results, conf_thres=0.4, iou_thres=0.5)[0]

    def predict(self, images) -> list:
        cropped_images = list()
        if not isinstance(images, list):
            images = [images]
        for image_path in images:
            image = cv2.imread(image_path)
            results = self.model(image)
            results = remove_duplicates(results)
            idx = 0
            for i, result in enumerate(results):
                annotator = Annotator(image, line_width=2, example=self.names)
                boxes = result.boxes.xyxy.cpu().tolist()
                classes = result.boxes.cls.cpu().tolist()
                if boxes is not None:
                    for box, cls in zip(boxes, classes):
                        annotator.box_label(
                            box,
                            color=colors(int(cls), True),
                            label=self.names[int(cls)],
                        )
                        crop_obj = image[
                            int(box[1]) : int(box[3]), int(box[0]) : int(box[2])
                        ]
                        cropped_image_path = (
                            ".".join(image_path.split(".")[:-1])
                            + "_"
                            + str(idx)
                            + ".png"
                        )
                        cv2.imwrite(cropped_image_path, crop_obj)
                        cropped_images.append(cropped_image_path)
                        idx += 1
        return cropped_images
