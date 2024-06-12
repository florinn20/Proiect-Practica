import cv2
import os
import time
import socket

cascPath=os.path.dirname(cv2.__file__)+"/data/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
video_capture = cv2.VideoCapture(1)

count=1
a1=0
a2=0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    HOST = '192.168.137.38'
    PORT = 65324
    s.connect((HOST,PORT))
    start_time=time.time()
    while True:
        current_time=time.time()
        if current_time-start_time>1:
            start_time=current_time

            while True:
                # Capture frame-by-frame
                ret, frames = video_capture.read()
                gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)
                x_max=0; y_max=0; h_max=0; w_max=0

                faces = faceCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )

                cv2.circle(frames, (320, 240), 1, (0, 0, 255), -2)
                cv2.line(frames, (320, 235), (320, 245), (0, 0, 0), 1)
                cv2.line(frames, (315, 240), (325, 240), (0, 0, 0), 1)

                # Draw a rectangle around the faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frames, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    print(x, " ", y)
                    q, e, _ = frames.shape
                    xc = (int)(x + (w / 2));    yc = (int)(y + (h / 2))

                    if (x+w>x_max+w_max and y_max+h_max) or ((x+w)*(y+h) > (x_max+w_max)*(y_max+h_max)):
                        x_max=x
                        w_max=w
                        y_max=y
                        h_max=h

                    print(q / 2 - xc + w / 2, " ", yc - e / 2 + h / 2, "\n")
                    cv2.circle(frames, (xc, yc), 1, (4, 54, 206), -1)

                if count%20==1:
                    a1=320-(int)(x_max+(w_max/2))
                    a2=240-(int)(y_max+(h_max/2))
                    coded_transfer = "{},{}".format(a1, a2)
                    my_transfer = coded_transfer.encode('utf-8')
                    s.sendall(my_transfer)

                # Display the resulting frame
                frames=cv2.resize(frames, (1280,720))
                cv2.imshow('Video', frames)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                count+=1

            video_capture.release()
            cv2.destroyAllWindows()