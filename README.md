# peopleTracking


## Presentation
A python3 script that count the number of person crossing a line <br />
Using OpenCV lib: https://pypi.org/project/opencv-python/

## Usage

1. Create a json file or use the one included in the repository. <br />

    Here his the json file needed format: <br /> <br />
    > { <br />
          "path": "path to a video" <br />
          "line": [x1, y1, x2, y2] <br />
     }<br /><br /> 

     ### Arguments
     **path:** is the path to a video <br>
     **line:** are the coordonates of the line people can cross.
3. Start the project with **python3 people_tracking.py --file [path to the json file]**



