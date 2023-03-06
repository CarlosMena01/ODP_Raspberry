from flask import Flask
from flask import render_template
from flask import Response

import numpy as np
from scipy.fftpack import fft2, fftshift
import cv2

# Función para aplicar la transformada de Fourier a una imagen
def apply_fourier_transform(frame):
    # Convertimos la imagen a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplicamos la transformada de Fourier
    f = fft2(gray)
    fshift = fftshift(f)
    magnitude_spectrum = 20*np.log(np.abs(fshift))
    
    
    return magnitude_spectrum

def generate():
    cap = cv2.VideoCapture(0)
    # Verificar si la cámara se ha abierto correctamente
    if not cap.isOpened():
        print("Error al abrir la cámara")
        exit()
    while True:
        ret, frame = cap.read()

        while not ret:
            print("La cámará no se pudo abrir, re intentado ...")
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        (flag, encodedImage) = cv2.imencode(".jpg", gray)
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')

app = Flask(__name__)


@app.route("/")
def index():
     return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=False)

cap.release()