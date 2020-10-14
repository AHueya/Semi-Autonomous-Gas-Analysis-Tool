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
import RPi.GPIO as GPIO
from flask import Flask, jsonify, render_template, Response, request
from camera_pi import Camera

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#define pin
gpioTest = 26
gpioTestStatus = 0
GPIO.setup(gpioTest, GPIO.IN)


@app.route('/')
def index():
    #read GPIO Status
    gpioTestStatus = GPIO.input(gpioTest)
    templateData = {
        'gpioTest' : gpioTestStatus,
    }
    return render_template('index.html', **templateData)

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
