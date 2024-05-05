#!/usr/bin/python3
import signal
import sys
import depthai as dai
from mjpeg_streamer import MjpegServer, Stream
from http.server import HTTPServer, BaseHTTPRequestHandler


resX=1920
resY=1080
qual=100
fps=30

port=8080

stream = Stream("oak_camera", size=(resX, resY), quality=qual, fps=fps)

server = MjpegServer("0.0.0.0", port)
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
with dai.Device(pipeline) as device:
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    while True:
        frame = qRgb.get().getFrame()
        stream.set_frame(frame)


