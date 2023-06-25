#!/usr/bin/env python3

import json
import cv2
import math
import sys
import getopt
import numpy as np



def createObjects(humans_cur_pos: tuple[int, int]):
    global track_id
    global tracked_humans_dict
    # associate a unique id for each object and his position
    for  (cx, cy, w, h) in humans_cur_pos:
    
        tracked_humans_dict[track_id] = {"pos": (cx, cy), "size": (w, h)}
        track_id += 1

    return tracked_humans_dict


def refreshObjects(center_pts_cur: tuple[int, int], tracked_humans_dict: dict):
    global track_id

    for id, data in tracked_humans_dict.copy().items():
        prev_pt = data['pos']
        objectExist = False
        for cx, cy, w, h in center_pts_cur.copy():
            cur_pt = (cx, cy)
            distance = math.hypot(
                (prev_pt[0] - cur_pt[0]), (prev_pt[1] - cur_pt[1]))
            # if a point in dictconary is close enough to a new point resfresh his position
            if (distance < 20):
                
                tracked_humans_dict[id] = {"pos": cur_pt, 'size': (w, h)}
                objectExist = True
                center_pts_cur.remove((cx, cy, w, h))
                continue
        # if object is out of the image or lost tracking
        if not objectExist:
            tracked_humans_dict.pop(id)
    # add to dictonary new object who appear on the current frame
    createObjects(center_pts_cur)
    return tracked_humans_dict


def draw_objects(tracked_humans_dict: dict, cur_frame, pt1Line: int, pt2Line: int):

    for track_id, data in tracked_humans_dict.items():
        pt = data['pos']
        w, h = data['size']

        # draw the line to cross
        cv2.line(cur_frame, pt1=pt1Line, pt2=pt2Line, color=(
            255, 0, 0), thickness=3, lineType=8, shift=0)
        # draw the line to cross
        cv2.putText(cur_frame, "count : " + str(counter),
                    (50, 50), 0, 1, (255, 255, 255), 2)


def getVideo(json_data):
    if (len(json_data['path']) <= 0):
        print('''Error: video path is bad
\nTips: Read documentation for more details''')
        exit(84)

    capture = cv2.VideoCapture(json_data['path'])

    if (capture.isOpened() == False):
        print("Error opening video stream or file")
        exit(84)
    return capture


def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect


def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def hasCrossedLine(pt1Line, pt2Line, prev_tracked_humans_dict:  tuple[int, int], cur_tracked_humans_dict: dict, frame):
    global counter
    global crossed_person
    for id, data in prev_tracked_humans_dict.items():
        prev_cx, prev_cy = data['pos']
        _, prev_h = data['size']
        
      
        if not id in cur_tracked_humans_dict:
            continue
        
        # get top of box for cur and prev 
        prev_topY = int(prev_cy - (prev_h /2))
        cur_cx, cur_cy = cur_tracked_humans_dict[id]['pos']
        _, cur_h = cur_tracked_humans_dict[id]['size']
        cur_topY =int(cur_cy - (cur_h /2)) 
        
        # get average height between prev and cur frame
        av_h = (prev_h + cur_h) / 2
        ecart =  int(av_h / 4)
        
        # draw 5 point on person and check intersection between the line and the prev_pos/cur_pos
        for i in range(5):
                cv2.circle(frame, (prev_cx, prev_topY), 3, (0, 255, 0), -1)
                cv2.circle(frame, (cur_cx, cur_topY), 3, (255, 0, 0), -1)
                if intersect((cur_cx, cur_topY), (prev_cx, prev_topY), pt1Line, pt2Line):
                    if id not in crossed_person:
                        crossed_person.append(id)
                        counter += 1
                prev_topY += ecart
                cur_topY += ecart

    



def getArgs(argvs):
    usage = '''usage: people_tracking.py [-h] [--file TEXT]
                  
optional arguments:
      --file FILE.json Specify the path to the video file in JSON format.
      -h to get help'''
    opts, args = getopt.getopt(argvs, "hf:", ["file="])
    for opt, arg in opts:
        if len(opts) == 1 and len(args) == 0 and opt == '-h':
            print(usage)
            sys.exit()
        if len(opts) == 1 and arg != None and opt == '--file':
            return arg
    print(usage)
    sys.exit()

def getObjects(outs, width, height, classes, frame):
    class_ids = []
    confidences = []
    boxes = []
    humansPos = []
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
                
    # take confiendences score of each box a get more accruate boxes
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            #if object defected is a person
            if label == "person":
                cx = int(x + (w / 2))
                cy = int(y + (h / 2))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) 
                humansPos.append((cx, cy, w, h))
                
    return humansPos
          

def main(argvs):
    global humans_prev_pos
    global track_id
    global tracked_humans_dict
    global counter

    
    path = getArgs(argvs)
    with open(path) as f:
        json_data = json.load(f)
    capture = getVideo(json_data)
    if len(json_data['line']) != 4:
        print('''Error: line is null or bad format, it should be line: [x1, y1, x2, y2]
\nTips: Read documentation for more details''')
        sys.exit()

    # setup yoloV3
    net = cv2.dnn.readNet("./yolov3.weights", "./yolov3.cfg")
    
    # get classes names
    classes = []
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    
    layer_names = net.getLayerNames()
    #Determine the output layer names from the YOLO model 
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    
    line = json_data["line"]
    pt1Line = (line[0], line[1])
    pt2Line = (line[2], line[3])

    # while video is playing
    while (capture.isOpened()):
        # get each video frame
        ret, frame = capture.read()
        if ret == True:
            
            # resize video to be more accurate
            frame = cv2.resize(frame, None, fx=0.4, fy=0.4)
            height, width, channels = frame.shape
            blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
            swapRB=True, crop=False)
            
            # detect objects
            net.setInput(blob)
            outs = net.forward(output_layers)
            
            humans_cur_pos =  getObjects(outs, width, height, classes, frame)
            
            if track_id == 0:
                tracked_humans_dict = createObjects(humans_cur_pos)
            else:
                prev_tracked_humain_dict = tracked_humans_dict.copy()
                tracked_humans_dict = refreshObjects(
                    humans_cur_pos, tracked_humans_dict)
                hasCrossedLine(pt1Line, pt2Line,
                               prev_tracked_humain_dict, tracked_humans_dict, frame)

            draw_objects(tracked_humans_dict, frame, pt1Line, pt2Line)

            cv2.imshow('Frame', frame)
            humans_cur_pos = humans_cur_pos.copy()

            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            break

    capture.release()
    cv2.destroyAllWindows()

humans_prev_pos = []

track_id = 0
tracked_humans_dict = {}

counter = 0
crossed_person = []


if __name__ == "__main__":
    main(sys.argv[1:])
