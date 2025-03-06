from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import cv2


class head_detector():
    def __init__(self, model) -> None:
        self.model = model
        self.names = model.names

    def __call__(self, images) -> None:
        return self.predict(images)

    def predict(self, images) -> list:
        cropped_images = list()
        if not isinstance(images, list):
            images = list(images)
        for image_path in images:
            image = cv2.imread(image_path)
            results = self.model(image)
            idx = 0
            for i, result in enumerate(results):
                annotator = Annotator(image, line_width=2, example=self.names)
                boxes = result.boxes.xyxy.cpu().tolist()  # Boxes object for bounding box outputs
                classes = result.boxes.cls.cpu().tolist()
                if boxes is not None:
                    for box, cls in zip(boxes, classes):
                        annotator.box_label(box, color=colors(int(cls), True), label=self.names[int(cls)])
                        crop_obj = image[int(box[1]) : int(box[3]), int(box[0]) : int(box[2])]
                        cropped_image_path = ('.').join(image_path.split('.')[:-1]) + "_" + str(idx) + ".png"
                        # cv2.imshow('Cropped Object', crop_obj)
                        # cv2.waitKey(0)
                        # cv2.destroyAllWindows()
                        cv2.imwrite(cropped_image_path, crop_obj)
                        cropped_images.append(cropped_image_path)
                        idx+=1
        return cropped_images
