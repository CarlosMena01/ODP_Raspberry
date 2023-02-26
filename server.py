from fastapi import FastAPI, Response
from picamera import PiCamera
from io import BytesIO
import numpy as np
from scipy.fftpack import fft2, fftshift
from time import sleep
from PIL import Image

app = FastAPI()

# Configuramos la resolución de la cámara
camera = PiCamera()
camera.resolution = (640, 480)

# Función para aplicar la transformada de Fourier a una imagen
def apply_fourier_transform(frame):
    # Convertir la imagen a escala de grises
    gray = np.dot(frame[...,:3], [0.2989, 0.5870, 0.1140])

    # Aplica la FFT a la imagen en escala de grises
    f = fft2(gray)
    fshift = fftshift(f)
    magnitude_spectrum = np.log(np.abs(fshift))
    
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
        frame = Image.open(BytesIO(stream.getvalue()))
        frame = np.array(frame)

        # Aplicamos la transformada de Fourier a la imagen
        frame = apply_fourier_transform(frame)

        # Enviamos la imagen como parte del stream de video

        # Convertir el frame a formato de imagen
        img = Image.fromarray(frame)

        # Codificar la imagen en formato JPEG
        with BytesIO() as output:
            img.save(output, format='JPEG')
            encoded_img = output.getvalue()

        response_body = b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + encoded_img[1].tostring() + b'\r\n'
        try:
            await response.write(response_body)
        except:
            break

    # Paramos la cámara al terminar el stream de video
    camera.stop_preview()
