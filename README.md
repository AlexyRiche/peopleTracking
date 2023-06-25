# peopleTracking


## Presentation
A python3 script that count the number of person crossing a line <br />
Using OpenCV lib: https://pypi.org/project/opencv-python/ <br />
Using YoloV3 algo : https://pjreddie.com/darknet/yolo/

## Prerequisite
 1. Got installed Python3
    
 3. Got installed OpenCV

## Usage

1. Clone this repository on your computer.

2. Download the weight files on this link (it's needed by YoloV3) : https://pjreddie.com/media/files/yolov3.weights <br />

3. Add it to the root folder of project

4. Create a json file or use the one included in the repository. <br />

    Here his the json file needed format: <br /> <br />
    > { <br />
          "path": "path to a video" <br />
          "line": [x1, y1, x2, y2] <br />
     }<br /><br /> 

     ### Arguments
     **path:** is the path to a video <br>
     **line:** are the coordonates of the line people can cross.<br />
     **The window size is 400x400 be sure to draw a line between this coordonates**
5. Start the project with **python3 people_tracking.py --file [path to the json file]**



