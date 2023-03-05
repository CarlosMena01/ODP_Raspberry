# Librerias para stream 
from fastapi import FastAPI, Response
from starlette.responses import StreamingResponse
# Librerías de manejo de imagenes
import numpy as np
from scipy.fftpack import fft2, fftshift
import cv2

app = FastAPI()

# Configuramos la cámara
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Función para aplicar la transformada de Fourier a una imagen
def apply_fourier_transform(frame):
    # Convertimos la imagen a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplicamos la transformada de Fourier
    f = fft2(gray)
    fshift = fftshift(f)
    magnitude_spectrum = 20*np.log(np.abs(fshift))
    
    
    return frame

def generate():
     while True:
          ret, frame = cap.read()
          if ret:
                frame = apply_fourier_transform(frame)
                (flag, encodedImage) = cv2.imencode(".jpg", frame)
                if not flag:
                   continue
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
@app.get("/")
def index():
    with open("./templates/index.html") as fh:
        data = fh.read()
    return Response(content=data, media_type="text/html")

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace;boundary=frame")


cap.release()
