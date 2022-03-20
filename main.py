import sys

import servo_control
import rfid_controls
import MQTT_Subscriber
import threading

# below are imports for the camera
from flask import Flask, render_template, Response, request
from camera import VideoCamera
import time
import os

# Flask stuff
app = Flask(__name__)

# Route to main page, index.html
@app.route('/', methods=['GET', 'POST'])
def move():
    result = ""
    if request.method == 'POST':
        
        return render_template('index.html', res_str=result)
                        
    return render_template('index.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Video feed route
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    print("Web server establishing...")
    MQTTSub = MQTT_Subscriber.MQTTSubscriber('has/system-controller')
    RFIDRead = rfid_controls.RFIDReader()
    servo_control = servo_control.GroveServo(int(sys.argv[1]))
    MQTT_Thread = threading.Thread(target=MQTTSub.run, args=(servo_control,), daemon=True)
    RFID_Thread = threading.Thread(target=RFIDRead.run, args=(), daemon=True)
    MQTT_Thread.start()
    RFID_Thread.start()
    app.run(host='0.0.0.0', debug=True, threaded=True)
    print("Exiting")
