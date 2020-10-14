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
from flask import Flask, jsonify, render_template, Response, request
from camera_pi import Camera
import RPi.GPIO as GPIO
import time
import threading

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#define pin
gpioTest1 = 26
gpioTestStatus1 = 0
GPIO.setup(gpioTest1, GPIO.IN)

gpioTest2 = 13
gpioTestStatus2 = 0
GPIO.setup(gpioTest2, GPIO.IN)

gpioTest3 = 6
gpioTestStatus3 = 0
GPIO.setup(gpioTest3, GPIO.IN)


@app.route('/update', methods=['POST'])
def update():
    #read GPIO Status
    gpioTestStatus1 = GPIO.input(gpioTest1)
    gpioTestStatus2 = GPIO.input(gpioTest2)
    gpioTestStatus3 = GPIO.input(gpioTest3)
    return jsonify({
        'gpioTestStatus1': gpioTestStatus1,
        'gpioTestStatus2': gpioTestStatus2,
        'gpioTestStatus3': gpioTestStatus3,
    })

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
