import cv2 as cv
import time


def facial_box(net, frames, conf_threshold=0.7):
    frame_opencv = frames.copy()
    frame_height = frame_opencv.shape[0]
    frame_width = frame_opencv.shape[1]
    something = cv.dnn.blobFromImage(frame_opencv, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(something)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frame_width)
            y1 = int(detections[0, 0, i, 4] * frame_height)
            x2 = int(detections[0, 0, i, 5] * frame_width)
            y2 = int(detections[0, 0, i, 6] * frame_height)
            bboxes.append([x1, y1, x2, y2])
            cv.rectangle(frame_opencv, (x1, y1), (x2, y2), (0, 255, 0), int(round(frame_height / 150)), 8)
    return frame_opencv, bboxes


faceProto = "opencv_face_detector.pbtxt"
faceModel = "opencv_face_detector_uint8.pb"

ageProto = "age_deploy.prototxt"
ageModel = "age_net.caffemodel"

genderProto = "gender_deploy.prototxt"
genderModel = "gender_net.caffemodel"

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(20-25)', '(30-40)', '(40-55)', '(60-100)']
genderList = ['Male', 'Female']

# Load network
ageNet = cv.dnn.readNet(ageModel, ageProto)
genderNet = cv.dnn.readNet(genderModel, genderProto)
faceNet = cv.dnn.readNet(faceModel, faceProto)
cap = cv.VideoCapture(0)
padding = 20
while cv.waitKey(1) < 0:
    t = time.time()
    hasFrame, frame = cap.read()
    if not hasFrame:
        cv.waitKey()
        break
    frameFace, bboxes = facial_box(faceNet, frame)
    if not bboxes:
        print("No face Detected, Checking next frame")
        continue
    for bbox in bboxes:
        face = frame[max(0, bbox[1] - padding):min(bbox[3] + padding, frame.shape[0] - 1),
               max(0, bbox[0] - padding):min(bbox[2] + padding, frame.shape[1] - 1)]

        blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
        genderNet.setInput(blob)
        genderPreds = genderNet.forward()
        gender = genderList[genderPreds[0].argmax()]
        print("Gender : {}, conf = {:.3f}".format(gender, genderPreds[0].max()))
        ageNet.setInput(blob)
        agePreds = ageNet.forward()
        age = ageList[agePreds[0].argmax()]
        print("Age Output : {}".format(agePreds))
        print("Age : {}, conf = {:.3f}".format(age, agePreds[0].max()))
        label = "{},{}".format(gender, age)
        cv.putText(frameFace, label, (bbox[0], bbox[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2,
                   cv.LINE_AA)
        cv.imshow("Age Gender Demo", frameFace)
    print("time : {:.3f}".format(time.time() - t))
