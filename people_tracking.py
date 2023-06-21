#!/usr/bin/env python3

import json
import cv2
import math
import sys
import getopt


def detectHumans(hog, cur_frame) -> tuple[int, int]:
    humansPos = []
    # detect people function
    humans, _ = hog.detectMultiScale(
        cur_frame, winStride=(2, 2), padding=(10, 10), scale=1)
    for (x, y, w, h) in humans:
        # draw rectangle 
        pad_w, pad_h = int(0.15 * w), int(0.01 * h)
        cv2.rectangle(cur_frame, (x + pad_w, y + pad_h),
                      (x + w - pad_w, y + h - pad_h), (0, 255, 0), 2)
        cx = int(x + (w / 2))
        cy = int(y + (h / 2))
        # add cur postion in array
        humansPos.append((cx, cy))
    return humansPos


def createObjects(humans_cur_pos: tuple[int, int]):
    global track_id
    global tracked_humans_dict
    # associate a unique id for each object and his position
    for cur_pt in humans_cur_pos:
        tracked_humans_dict[track_id] = cur_pt
        track_id += 1

    return tracked_humans_dict


def refreshObjects(center_pts_cur: tuple[int, int], tracked_humans_dict: dict):
    global track_id

    for id, prev_pt in tracked_humans_dict.copy().items():
        objectExist = False
        for cur_pt in center_pts_cur.copy():
            distance = math.hypot(
                (prev_pt[0] - cur_pt[0]), (prev_pt[1] - cur_pt[1]))
            # if a point in dictconary is close enough to a new point resfresh his position
            if (distance < 40):
                tracked_humans_dict[id] = cur_pt
                objectExist = True
                center_pts_cur.remove(cur_pt)
                continue
        # if object is out of the image or lost tracking
        if not objectExist:
            tracked_humans_dict.pop(id)
    # add to dictonary new object who appear on the current frame
    createObjects(center_pts_cur)
    return tracked_humans_dict


def draw_objects(tracked_humans_dict: dict, cur_frame, pt1Line: int, pt2Line: int):

    for track_id, pt in tracked_humans_dict.items():
        
        # draw red circle on people
        cv2.circle(cur_frame, pt, 5, (0, 0, 255), -1)
        
        # draw coordonate on people
        cv2.putText(cur_frame, str(track_id), pt, 0, 1, (0, 0, 255), 2)
        cv2.putText(cur_frame, str(pt),
                    (pt[0], pt[1] + 25), 0, 0.5, (0, 0, 255), 2)
        
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



def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def hasCrossedLine(pt1Line, pt2Line, prev_tracked_humans_dict:  tuple[int, int], cur_tracked_humans_dict: dict):
    global counter
    for id, prev_pt in prev_tracked_humans_dict.items():    
        
        if not id in cur_tracked_humans_dict:
            continue
        if intersect(cur_tracked_humans_dict[id], prev_pt, pt1Line, pt2Line):
            counter +=1
            

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
    
    line = json_data["line"]
    pt1Line = (line[0], line[1])
    pt2Line = (line[2], line[3])
  
    # set tracking settings
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # while video is playing
    while (capture.isOpened()):
        # get each video frame
        ret, frame = capture.read()
        if ret == True:
            humans_cur_pos = detectHumans(hog, frame)
            
            if track_id == 0:
                tracked_humans_dict = createObjects(humans_cur_pos)
            else:
                prev_tracked_humain_dict = tracked_humans_dict.copy()
                tracked_humans_dict = refreshObjects(
                    humans_cur_pos, tracked_humans_dict)
                hasCrossedLine(pt1Line, pt2Line, prev_tracked_humain_dict, tracked_humans_dict)
            
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

if __name__ == "__main__":
    main(sys.argv[1:])
