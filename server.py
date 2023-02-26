import io
import logging
from threading import Condition
from fastapi import FastAPI, Response

app = FastAPI()

PAGE = """\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
<p>FPS: <span id="fps"></span></p>
<script>
var fps_span = document.getElementById("fps");
var fps = 0;
setInterval(function() {
    fps_span.innerHTML = fps.toFixed(1);
    fps = 0;
}, 1000);
var img = new Image();
img.onload = function() {
    fps += 1;
};
img.src = "stream.mjpg";
</script>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

output = StreamingOutput()

@app.get("/")
async def root():
    return Response(content=PAGE, media_type="text/html")

@app.get("/stream.mjpg")
async def stream():
    headers = {
        'Age': '0',
        'Cache-Control': 'no-cache, private',
        'Pragma': 'no-cache',
        'Content-Type': 'multipart/x-mixed-replace; boundary=FRAME',
    }
    return Response(content=stream_generator(), headers=headers)

def stream_generator():
    try:
        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
            yield b'--FRAME\r\n'
            yield b'Content-Type: image/jpeg\r\n'
            yield b'Content-Length: ' + str(len(frame)).encode() + b'\r\n'
            yield b'\r\n'
            yield frame
            yield b'\r\n'
    except Exception as e:
        logging.warning(
            'Removed streaming client %s: %s',
            self.client_address, str(e))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='FastAPI MJPEG streaming demo')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', default=8000, help='Port number')
    args = parser.parse_args()

    import signal
    import sys

    def signal_handler(signal, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    from picamera import PiCamera
    camera = PiCamera(resolution='640x480', framerate=24)
    camera.start_recording(output, format='mjpeg')
    try:
        import uvicorn
        uvicorn.run(app, host=args.host, port=args.port)
    finally:
        camera.stop_recording()
