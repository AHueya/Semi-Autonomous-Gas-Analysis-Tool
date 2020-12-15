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

# Library declaration
from flask import Flask, jsonify, render_template, Response, request
from flask_socketio import SocketIO, emit
import io
import time
import serial 
import csv
from threading import Thread, Event
import picamera
from base_camera import BaseCamera
from decimal import *
from subprocess import call

def find(str, ch):
        for i, ltr in enumerate(str):
            if ltr == ch:
                yield i

port = serial.Serial('/dev/ttyUSB1', baudrate = 115200, timeout = 1)

port.write('AT'+'\r\n')
rcv = port.read(100)
#print rcv
time.sleep(.1)

port.write('AT+CGNSPWR=1'+'\r\n')       #to power the GPS
rcv = port.read(100)
#print rcv
time.sleep(.1)

port.write('AT+CGNSIPR=115200'+'\r\n')  #set the baud rate of GPS
rcv = port.read(100)
#print rcv
time.sleep(.1)

port.write('AT+CGNSTST=1'+'\r\n')       #send data received to UART
rcv = port.read(100)
#print rcv
time.sleep(.1)

port.write('AT+CGNSINF'+'\r\n')         #print the GPS information
rcv = port.read(200)
#print rcv
time.sleep(.1)
        
app = Flask(__name__)

# turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

# Threads for data update
thread = Thread()
thread_stop_event = Event()

# Define serial port
serialard = serial.Serial('/dev/ttyUSB0', 9600)

# Default Resolution and frame rate
var_resolution = '480x320'
var_framerate = 24

# Camera initialization
class Camera(BaseCamera):
    @staticmethod
    def frames():
        prev_resolution = var_resolution
        prev_framerate = var_framerate
        
        # Video Graphics Array Resolution
        with picamera.PiCamera(resolution=var_resolution, framerate=var_framerate) as camera:
            # Rotate camera 180 degrees
            camera.rotation=180
            
            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                
                # return current frame
                stream.seek(0)
                yield stream.read()

                # If resolution was modified
                if prev_resolution != var_resolution or prev_framerate != var_framerate:
                    print("Resolution/frame rate modified, restarting camera")
                    return

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

# CSV file creation and initialization
with open('data.csv','wb') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
    # CSV file row 1
    filewriter.writerow(['Latitude', 'Longitude', 'Temperature', 'Humidity', 'Oxygen', 'Carbon Dioxide',
                         'Carbon Monoxide', 'Liquefied Petroleum Gas'])

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
        fd = port.read(200)     #read the GPS data from UART
        #print fd
        time.sleep(.5)
        if '$GNRMC' in fd:      #to extract lattitude and longitude
                ps=fd.find('$GNRMC')
                dif = len(fd)-ps
                if dif > 50:
                        data = fd[ps:(ps+50)]
                        #print data
                        ds = data.find('A')     #check GPS is valid
                        if ds > 0 and ds < 20:
                                p=list(find(data, ","))
                                lati=data[(p[2]+1):p[3]]
                                longi=data[(p[4]+1):p[5]]
#GPS data calculation
                                lat=lati[2:len(lati)]
                                lat = Decimal(lat)
                                lat = lat/60
                                s11=int(lati[0:2])
                                lat = s11+lat

                                long = longi[3:len(longi)]
                                long = Decimal(long)
                                long = long/60
                                s22 = int(longi[0:3])
                                long = s22+long
                                
        line = serialard.readline()
       # linegps = port.readline()
       # lat, long = linegps.split()
        temp, humi, oxyg, cadi, camo, lpg = line.split()
        
        #Write data to CSV file
        with open('data.csv', 'a') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
            filewriter.writerow([lat, long, temp, humi, oxyg, cadi, camo, lpg])

        #Send data to web GUI
        socketio.emit('newdata', {'temp':temp, 'humi':humi,
                                  'oxyg':oxyg, 'cadi':cadi,
                                  'camo':camo, 'lpg' :lpg}, namespace='/test')
        socketio.sleep(.5)
##### END Update Function ##########################################

# Send HTML to web GUI
@app.route('/')
def index():
    return render_template('index.html')

# On connect with client...
@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    print('Client connected')
    
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(UpdateData)

# On disconnect with client...
@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

# Define camera
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Send "video" feed to web GUI
@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Enable socket
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
