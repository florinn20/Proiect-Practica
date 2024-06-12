from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torchvision import datasets
from torch.utils.data import DataLoader
from PIL import Image
import cv2
import time
import os
import socket

# initializing MTCNN and InceptionResnetV1
mtcnn0 = MTCNN(image_size=240, margin=0, keep_all=False, min_face_size=40)  # keep_all=False
mtcnn = MTCNN(image_size=240, margin=0, keep_all=True, min_face_size=40)  # keep_all=True
resnet = InceptionResnetV1(pretrained='vggface2').eval()

# Read data from folder
dataset = datasets.ImageFolder("photos")  # photos folder path
idx_to_class = {i: c for c, i in dataset.class_to_idx.items()}  # accessing names of peoples from folder names

def collate_fn(x):
    return x[0]

count = 1
a1 = 0
a2 = 0
loader = DataLoader(dataset, collate_fn=collate_fn)

name_list = []  # list of names corrospoing to cropped photos
embedding_list = []  # list of embeding matrix after conversion from cropped faces to embedding matrix using resnet

for img, idx in loader:
    face, prob = mtcnn0(img, return_prob=True)
    if face is not None and prob > 0.92:
        emb = resnet(face.unsqueeze(0))
        embedding_list.append(emb.detach())
        name_list.append(idx_to_class[idx])

# save data
data = [embedding_list, name_list]
torch.save(data, 'data.pt')  # saving data.pt file
# Using webcam recognize face

# loading data.pt file
load_data = torch.load('data.pt')
embedding_list = load_data[0]
name_list = load_data[1]

cam = cv2.VideoCapture(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    HOST = '192.168.137.38'
    PORT = 65321
    s.connect((HOST, PORT))
    start_time = time.time()
    while True:
        current_time = time.time()
        if current_time - start_time > 1:
            start_time = current_time

        while True:
            ret, frame = cam.read()
            if not ret:
                print("fail to grab frame, try again")
                break

            img = Image.fromarray(frame)
            img_cropped_list, prob_list = mtcnn(img, return_prob=True)

            xmax = 0
            ymax = 0
            xmin = 0
            ymin = 0

            if img_cropped_list is not None:
                boxes, _ = mtcnn.detect(img)

                for i, prob in enumerate(prob_list):
                    if prob > 0.90:
                        emb = resnet(img_cropped_list[i].unsqueeze(0)).detach()
                        dist_list = []  # list of matched distances, minimum distance is used to identify the person

                        for idx, emb_db in enumerate(embedding_list):
                            dist = torch.dist(emb, emb_db).item()
                            dist_list.append(dist)

                        min_dist = min(dist_list)  # get minumum dist value
                        min_dist_idx = dist_list.index(min_dist)  # get minumum dist index
                        name = name_list[min_dist_idx]  # get name corrosponding to minimum dist
                        box = boxes[i]
                        original_frame = frame.copy()  # storing copy of frame before drawing on it

                        if min_dist < 0.90:
                            frame = cv2.putText(frame, name + ' ' + str(min_dist), (int(box[0]), int(box[1])),
                                                cv2.FONT_HERSHEY_SIMPLEX,
                                                1, (0, 255, 0), 1, cv2.LINE_AA)

                        frame = cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])),
                                              (255, 0, 0), 1)

                        if (int(box[2]) - int(box[0])) * (int(box[3]) - int(box[1])) > (xmax - xmin)*(ymax - ymin):
                            xmax = int(box[2])
                            xmin = int(box[0])
                            ymax = int(box[1])
                            ymin = int(box[3])
                        print(xmax," ",ymax)
            if count % 11 == 1:
                a1 = 320 - (xmax + xmin) / 2
                a2 = 240 - (ymax + ymin) / 2
                coded_transfer = "{},{}".format(a1, a2)
                my_transfer = coded_transfer.encode('utf-8')
                s.sendall(my_transfer)

            cv2.imshow("IMG", frame)
            cv2.resize(frame, (1280, 720))
            count+=1

            k = cv2.waitKey(1)
            if k % 256 == 27:  # ESC
                print('Esc pressed, closing...')
                break

            elif k % 256 == 32:  # space to save image
                print('Enter your name :')
                name = input()

                # create directory if not exists
                if not os.path.exists('photos/' + name):
                    os.mkdir('photos/' + name)

                img_name = "photos/{}/{}.jpg".format(name, int(time.time()))
                cv2.imwrite(img_name, original_frame)
                print(" saved: {}".format(img_name))

        cam.release()
        cv2.destroyAllWindows()
        break
