import cv2

# Abrir la cámara
cap = cv2.VideoCapture(0)

# Verificar si la cámara se ha abierto correctamente
if not cap.isOpened():
    print("Error al abrir la cámara")
    exit()

# Ciclo infinito para mostrar la imagen de la cámara
while True:
    # Leer un fotograma de la cámara
    ret, frame = cap.read()

    # Verificar si se ha leído correctamente el fotograma
    if not ret:
        print("Error al leer el fotograma")
        break

    # Mostrar el fotograma en una ventana
    cv2.imshow("Camara", frame)

    # Esperar la tecla 'q' para salir
    if cv2.waitKey(1) == ord('q'):
        break

# Liberar la cámara y cerrar la ventana
cap.release()
cv2.destroyAllWindows()
