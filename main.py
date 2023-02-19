# Importamos todas las librerías
import picamera
import numpy as np
from scipy.fftpack import fft2, fftshift
from matplotlib import pyplot as plt

# Inicializar la cámara
camera = picamera.PiCamera()

# Capturar una imagen
image = np.empty((camera.resolution[1], camera.resolution[0], 3), dtype=np.uint8)
camera.capture(image, 'rgb')

# Convertir la imagen a escala de grises
gray = np.dot(image[...,:3], [0.2989, 0.5870, 0.1140])

# Aplica la FFT a la imagen en escala de grises
f = fft2(gray)
fshift = fftshift(f)
magnitude_spectrum = np.log(np.abs(fshift))

# Muestra la imagen original y su espectro de Fourier
plt.subplot(121),plt.imshow(gray, cmap = 'gray')
plt.title('Input Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(magnitude_spectrum, cmap = 'gray')
plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
plt.show()

