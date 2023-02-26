# Librerias para stream 
from fastapi import FastAPI, Response
from time import sleep
# Librerías de manejo de imagenes
from picamera import PiCamera
from io import BytesIO
import numpy as np
from scipy.fftpack import fft2, fftshift
import cv2

app = FastAPI()

# Configuramos la resolución de la cámara
camera = PiCamera()
camera.resolution = (640, 480)

# Función para aplicar la transformada de Fourier a una imagen
def apply_fourier_transform(frame):
    # Convertimos la imagen a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplicamos la transformada de Fourier
    f = fft2(gray)
    fshift = fftshift(f)
    magnitude_spectrum = 20*np.log(np.abs(fshift))
    
    # Convertimos la imagen de vuelta a color
    magnitude_spectrum = cv2.cvtColor(magnitude_spectrum, cv2.COLOR_GRAY2BGR)
    
    return magnitude_spectrum

# Ruta para obtener el stream de video con la transformada de Fourier
@app.get("/video_feed")
async def video_feed(response: Response):
    response.headers["Content-Type"] = "multipart/x-mixed-replace; boundary=frame"

    # Configuramos la cámara para obtener un stream continuo de video
    camera.framerate = 24
    camera.start_preview()
    sleep(2) # Esperamos a que la cámara se estabilice

    # Generamos el stream de video
    while True:
        # Capturamos una imagen de la cámara
        stream = BytesIO()
        camera.capture(stream, format='jpeg', use_video_port=True)
        frame = cv2.imdecode(np.frombuffer(stream.getvalue(), dtype=np.uint8), -1)

        # Aplicamos la transformada de Fourier a la imagen
        frame = apply_fourier_transform(frame)

        # Enviamos la imagen como parte del stream de video
        response_body = b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tostring() + b'\r\n'
        try:
            await response.write(response_body)
        except:
            break

    # Paramos la cámara al terminar el stream de video
    camera.stop_preview()
