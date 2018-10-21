from flask import Flask, Response
from flask_socketio import SocketIO, send, emit
from os.path import dirname, abspath
from queue import Queue
import base64
import cv2
import numpy as np
from PIL import Image
import io
import time
from object_inception import detect_object
from scipy.misc import imsave
import uuid

location = '/opt/lampp/htdocs/img/zoo-hackathon'
d = dirname(dirname(abspath(__file__)))

app = Flask(__name__)
app.queue = Queue()
socketio = SocketIO(app)

critically_endangered = [50,366,367]
endangered = [386,146,276,147,364,296,30,355,295,283,293,368,38,95,149,345,38,347,107,341]
threatened = [387,294,289,290,297]

@socketio.on('connect', namespace='/live')
def test_connect():
    print('Client wants to connect.')
    emit('response', {'data': 'OK'},broadcast=True)

@socketio.on('disconnect', namespace='/live')
def test_disconnect():
    print('Client disconnected')

@socketio.on('event', namespace='/live')
def test_message(message):
    emit('response',{'data': message['data']})
    print(message['data'])

@socketio.on('livevideo', namespace='/live')
def test_live(message):
    app.queue.put(message['data'])
    img_bytes = base64.b64decode(app.queue.get())
    img_np = np.array(Image.open(io.BytesIO(img_bytes)))
    label,index = detect_object(img_np)
    if index in critically_endangered:
        attribute = 'critically endangered'
    elif index in endangered:
        attribute = 'endangered'
    elif index in threatened:
        attribute = 'threatened'
    else:
        attribute = 'normal'
    if attribute is not 'normal':
        new_id = uuid.uuid4()
        new_location = '%s/%s.jpg'%(location,new_id)
        imsave(new_location, img_np)
        emit('camera_update', {'location': new_location, 'class': attribute, 'label':label},broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host = '0.0.0.0', port = 8020,debug=True)
