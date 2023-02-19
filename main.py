# Importamos todas las librerías
import cv2
import numpy as np
from scipy.fftpack import fft2, fftshift
from matplotlib import pyplot as plt

# Crea una instancia de la clase VideoCapture para acceder a la cámara
cap = cv2.VideoCapture(0)

# Captura una imagen de la cámara y conviértela a escala de grises
ret, img = cap.read()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

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

# Libera la cámara y cierra las ventanas de la imagen
cap.release()
cv2.destroyAllWindows()
