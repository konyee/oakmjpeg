#!/usr/bin/python3
from aiohttp import web
import signal
import cv2
import sys
import depthai as dai
from mjpeg_streamer import MjpegServer, Stream

resX=1920
resY=1080
qual=100
fps=10

port=8080

server = MjpegServer("0.0.0.0", port)


lastFrame=None

async def snapshot_handler(request):
    ret, jpeg = cv2.imencode('.jpg', lastFrame)
    jpg = jpeg.tobytes()
    return web.Response(body=jpg, content_type='image/jpeg')

stream = Stream("stream", size=(resX, resY), quality=qual, fps=fps)

server._app.router.add_get('/snapshot', snapshot_handler)
server.add_stream(stream);
server.start();

def signal_handler(signal, frame):
  server.stop();
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Create pipeline
pipeline = dai.Pipeline()
cam = pipeline.create(dai.node.ColorCamera)
cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
cam.setPreviewSize(1920,1080)

xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("rgb")

cam.preview.link(xout.input)

# Connect to device and start pipeline
def set_frame(frame):
    global lastFrame
    lastFrame = frame;
    stream.set_frame(frame);
    
with dai.Device(pipeline) as device:
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    while True:
        set_frame(qRgb.get().getFrame())


