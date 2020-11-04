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
import serial
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

#Define serial port
serial = serial.Serial('/dev/ttyUSB0', 9600)

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
            #Rotate camera 180 degrees
            camera.rotation=180
            #let camera warm up
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

##### START Data Update Function ###################################
def UpdateData(): 
    while not thread_stop_event.isSet():
        line = serial.readline()
        temp, humi, oxyg, cadi, camo, lpg = line.split()

        socketio.emit('newdata', {'temp':temp, 'humi':humi,
                                  'oxyg':oxyg, 'cadi':cadi,
                                  'camo':camo, 'lpg' :lpg}, namespace='/test')
        socketio.sleep(2)
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
        thread = socketio.start_background_task(UpdateData)

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