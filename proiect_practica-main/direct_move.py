import cv2
import os
import time
import socket
import torch
import numpy as np
from facenet_pytorch import MTCNN

cascPath = os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
a1 = 0
a2 = 0
probability = 0
xmin = 0
ymin = 0
xmax = 0
ymax = 0
number = 0


class FaceDetector(object):
    def __init__(self, mtcnn):
        self.mtcnn = mtcnn

    def draw(self, frame, boxes, probs, landmarks):
        global probability, xmin, ymin, xmax, ymax, a1, a2, number
        probability = 0
        xmin = 0
        ymin = 0
        xmax = 0
        ymax = 0
        number = 0

        try:
            for box, prob, ld in zip(boxes, probs, landmarks):
                # Draw rectangle on frame
                box = box.astype('int')
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)
                print("x:", box[0], " ", box[1], "y:", box[2], " ", box[3], "\n")
                # Show probability
                cv2.putText(frame, str(round(prob, 4)), (((box[0] + box[2]) >> 1) - 20, box[1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                # Draw landmarks
                ld = ld.astype('int')
                number += 1
                # cv2.circle(frame, tuple(ld[0]), 5, (0, 0, 255), -1)
                # cv2.circle(frame, tuple(ld[1]), 5, (0, 0, 255), -1)
                #cv2.circle(frame, tuple(ld[2]), 5, (0, 0, 255), -1)
                #cv2.line(frame, (320, 235), (320, 245), (0, 0, 0), 1)
                #cv2.line(frame, (315, 240), (325, 240), (0, 0, 0), 1)
                # cv2.circle(frame, tuple(ld[3]), 5, (0, 0, 255), -1)
                # cv2.circle(frame, tuple(ld[4]), 5, (0, 0, 255), -1)
                # print(tuple(ld[0]), " ", tuple(ld[1]), " ", tuple(ld[2]), " ", tuple(ld[3]), " ", tuple(ld[4]), " ")
                if (box[2] - box[0]) * (box[3] - box[1]) > (xmax - xmin) * (ymax - ymin):
                    xmax = box[2]
                    xmin = box[0]
                    ymin = box[1]
                    ymax = box[3]
                    a1, a2 = tuple(ld[2])

                for x in probs:
                    if x >= 0.9755:
                        probability = x

                print(probability)
        except Exception as e:
            print(e)
            pass

    def run(self):
        cap = cv2.VideoCapture(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            HOST = '192.168.137.38'
            PORT = 65321
            s.connect((HOST, PORT))
            start_time = time.time()
            while True:
                current_time = time.time()
                if current_time - start_time > 1:
                    start_time = current_time
                    count = 1
                    while True:
                        # Capture frame-by-frame
                        ret, frame = cap.read()
                        frame = cv2.flip(frame, 1)
                        try:
                            # Detect face box, probability and landmarks
                            boxes, probs, landmarks = self.mtcnn.detect(
                                frame, landmarks=True)
                            # Draw on frame
                            self.draw(frame, boxes, probs, landmarks)
                            # Show the frame
                            frame = cv2.resize(frame, (1280, 720))
                            # cv2.flip(frame,1)
                            cv2.imshow('Face Detection', frame)

                            if count % 30 == 1:
                                x = 320
                                y = 240
                                global probability, number
                                if number == 0:
                                    print("No face detected")
                                else:
                                    if probability >= 0.9755:
                                        global a1
                                        global a2
                                        x = a1 - x
                                        y = y - a2
                                        print(a1, " ", a2, '\n')
                                print(x, " ", y, '\n')
                                coded_transfer = "{},{}".format(x, y)
                                my_transfer = coded_transfer.encode('utf-8')
                                s.sendall(my_transfer)

                        except Exception as e:
                            print(e)
                            pass

                        if cv2.waitKey(1) == ord('q'):
                            break
                        count += 1

            cap.release()
            cv2.destroyAllWindows()

mtcnn = MTCNN()
fd = FaceDetector(mtcnn)
fd.run()
