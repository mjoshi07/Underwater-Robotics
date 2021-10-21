import cv2
import os
import numpy as np


def detect(net, img, conf_thresh=0.4, nms_thresh=0.4):
    (H, W) = img.shape[:2]
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    boxes = []
    confidences = []
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > conf_thresh:
                # scale the bounding box coordinates back relative to the
                # size of the image, keeping in mind that YOLO actually
                # returns the center (x, y)-coordinates of the bounding
                # box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                # update our list of bounding box coordinates, confidences,
                # and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, conf_thresh, nms_thresh)

    # ensure at least one detection exists
    if len(idxs) > 0:
        # loop over the indexes we are keeping
        for i in idxs.flatten():
            # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            # draw a bounding box rectangle and label on the image
            color = (255, 0, 0)
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

    return img


def detect_img(weights_path, config_path, img_path):
    """
    Perform detection, provided an img path, displays bounding boxes on the objects
    :param weights_path:
    :param config_path:
    :param img_path:
    :return:
    """
    net = cv2.dnn.readNet(weights_path, config_path)
    cv2.namedWindow("detection", cv2.WINDOW_FREERATIO)
    img = cv2.imread(img_path)
    img = detect(net, img)
    cv2.imshow("detection", img)
    cv2.waitKey(0)


def detect_objects(weights_path, config_path, img_dir):
    """
    Perform detection, provided an img dir path, displays bounding boxes on the objects
    :param weights_path:
    :param config_path:
    :param img_dir:
    :return:
    """
    net = cv2.dnn.readNet(weights_path, config_path)
    cv2.namedWindow("detection", cv2.WINDOW_FREERATIO)

    for root, dirs, files in os.walk(img_dir):
        for file in files:
            img_name = os.path.join(root, file)
            img = cv2.imread(img_name)
            img = detect(net, img)
            cv2.imshow("detection", img)
            key = cv2.waitKey(0)
            if key == ord('q'):
            	return
    pass


if __name__ == "__main__":

    weights_path = "../data/model/yolov4-tiny-custom_last.weights"
    config_path = "../data/model/yolov4-tiny-custom.cfg"

    img_path = "../data/test/test1.jpg"
    detect_img(weights_path, config_path, img_path)
