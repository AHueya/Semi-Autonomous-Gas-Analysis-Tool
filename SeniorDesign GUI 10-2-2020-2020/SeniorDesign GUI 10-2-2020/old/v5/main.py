#############################################################################
#                                                                           #
#       Senior Design Project Spring 2020 - Fall 2020                       #
#                                                                           #
#       Semi-Autonomous Robotic Assist Tool Web Based GUI                   #
#                                                                           #
#                                                                           #
#       Original Source Code:                                               #
#       https://blog.miguelgrinberg.com/post/video-streaming-with-flask     #
#                                                                           #
#############################################################################
#
# Current bugs: no camera setting values results in errors
#
from flask import Flask, jsonify, render_template, Response, request
import RPi.GPIO as GPIO
import io
import time
import threading
import picamera
from base_camera import BaseCamera

app = Flask(__name__)

#Default Resolution and frame rate
var_resolution = '480x320'
var_framerate = 24

class Camera(BaseCamera):
    @staticmethod
    def frames():
        prev_resolution = var_resolution
        prev_framerate = var_framerate
        
        #Video Graphics Array Resolution
        with picamera.PiCamera(resolution=var_resolution, framerate=var_framerate) as camera:
            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                #If resolution was modified
                if prev_resolution != var_resolution or prev_framerate != var_framerate:
                    print("Resolution/frame rate modified, restarting camera")
                    return

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

##### START Define Pin #############################################
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

gpioTest1 = 26
gpioTestStatus1 = 0
GPIO.setup(gpioTest1, GPIO.IN)

gpioTest2 = 13
gpioTestStatus2 = 0
GPIO.setup(gpioTest2, GPIO.IN)

gpioTest3 = 6
gpioTestStatus3 = 0
GPIO.setup(gpioTest3, GPIO.IN)
##### END Define Pin ###############################################

##### START Update Function ########################################
#
# GET: Client requests data (sensor values) from server 
#
# POST: Client sends data (camera settings) to server
#
####################################################################
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'GET':
        #read GPIO Status
        gpioTestStatus1 = GPIO.input(gpioTest1)
        gpioTestStatus2 = GPIO.input(gpioTest2)
        gpioTestStatus3 = GPIO.input(gpioTest3)
        return jsonify({
            'gpioTestStatus1': gpioTestStatus1,
            'gpioTestStatus2': gpioTestStatus2,
            'gpioTestStatus3': gpioTestStatus3,
        })
    elif request.method == 'POST':
        global var_resolution
        var_resolution = request.form['res']
        global var_framerate
        var_framerate = int(request.form['fps'])
        print(var_resolution)
        print(var_framerate)
        return render_template('index.html')
##### END Update Function ##########################################

@app.route('/')
def index():
    return render_template('index.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
