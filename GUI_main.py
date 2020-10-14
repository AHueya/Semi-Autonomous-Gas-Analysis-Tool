#############################################################################
#                                                                           #
#       Senior Design Project Spring 2020 - Fall 2020                       #
#                                                                           #
#       Semi-Autonomous Robotic Assist Tool Web Based GUI                   #
#                                                                           #
#                                                                           #
#       Original Source Code:                                               #
#       https://blog.miguelgrinberg.com/post/video-streaming-with-flask     #
#       https://github.com/shanealynn/async_flask                           #
#                                                                           #
#############################################################################
#
# Current bugs:
# - no camera setting values results in errors
# - Not really a bug, but webpage must be refreshed after modifying camera
#
from flask import Flask, jsonify, render_template, Response, request
from flask_socketio import SocketIO, emit
import RPi.GPIO as GPIO
import io
import time
from threading import Thread, Event
import picamera
from base_camera import BaseCamera

from random import random

app = Flask(__name__)

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#Threads for data update
thread = Thread()
thread_stop_event = Event()

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

##### START Camera Update Function #################################
#
# GET: Client requests data (sensor values) from server
#
# POST: Client sends data (camera settings) to server
#
####################################################################
@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        global var_resolution
        var_resolution = request.form['res']
        global var_framerate
        var_framerate = int(request.form['fps'])
        print(var_resolution)
        print(var_framerate)
        return render_template('index.html')
##### END Update Function ##########################################

##### START Simulated Values #######################################
def randomNumberGenerator():
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers
    print("Making random numbers")
    while not thread_stop_event.isSet():
        gpioTestStatus3 = round(random()*1000)
        gpioTestStatus4 = round(random()*1000)
        gpioTestStatus5 = round(random()*1000)
        gpioTestStatus6 = round(random()*1000)
        gpioTestStatus7 = round(random()*1000)
        gpioTestStatus8 = round(random()*1000)
        socketio.emit('newdata', {'temp':gpioTestStatus1, 'humi':gpioTestStatus2,
                                  'camo':gpioTestStatus3, 'cadi':gpioTestStatus4,
                                  'oxyg':gpioTestStatus5, 'meth':gpioTestStatus6,
                                  'buta':gpioTestStatus7, 'prop':gpioTestStatus8}, namespace='/test')
        socketio.sleep(10)
##### END Simulated Values #########################################

##### START Data Update Function ###################################
def updateData():
    print("Sending data")
    while not thread_stop_event.isSet():
        gpioTestStatus1 = GPIO.input(gpioTest1)
        gpioTestStatus2 = GPIO.input(gpioTest2)
        gpioTestStatus3 = GPIO.input(gpioTest3)
        socketio.emit('newdata', {'temp':gpioTestStatus1, 'humi':gpioTestStatus2,
                                  'camo':gpioTestStatus3, 'cadi':gpioTestStatus4,
                                  'oxyg':gpioTestStatus5, 'meth':gpioTestStatus6,
                                  'buta':gpioTestStatus7, 'prop':gpioTestStatus8}, namespace='/test')
        socketio.sleep(1)
##### END Update Function ##########################################

@app.route('/')
def index():
    return render_template('index.html')

#On connect with client...
@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    print('Client connected')

    if not thread.isAlive():
        print("Starting Thread")
        #thread = socketio.start_background_task(updateData)
        thread = socketio.start_background_task(randomNumberGenerator)

#On disconnect with client...
@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

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
    socketio.run(app, host='0.0.0.0', debug=True)
