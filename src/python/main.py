import cv2
import mediapipe as mp
import serial
import time

# --- CONFIGURAÇÃO DA SERIAL ---
arduino = serial.Serial('/dev/ttyACM0', 9600)  # Troque pela sua porta
time.sleep(2)  # tempo para inicializar a comunicação

# --- CONFIGURAÇÃO DO MEDIAPIPE ---
camera = cv2.VideoCapture(0)
mao = mp.solutions.hands
hands = mao.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.9)
hand_drawing = mp.solutions.drawing_utils

# IDs das pontas dos dedos
dedos_ids = [4, 8, 12, 16, 20]

while True:
    _, frame = camera.read()
    
    imagem_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = hands.process(imagem_rgb)

    if resultados.multi_hand_landmarks and resultados.multi_handedness:
        for juntas, mao_info in zip(resultados.multi_hand_landmarks, resultados.multi_handedness):
            label = mao_info.classification[0].label  # "Left" ou "Right"
            hand_drawing.draw_landmarks(frame, juntas, mao.HAND_CONNECTIONS)

            # Pegar coordenadas
            pontos = []
            for lm in juntas.landmark:
                h, w, _ = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                pontos.append((cx, cy))

            dedos_levantados = []

            # --- Lógica para o polegar ---
            if label == "Right":  # mão direita
                if pontos[dedos_ids[0]][0] > pontos[dedos_ids[0] - 1][0]:
                    dedos_levantados.append(0)
                else:
                    dedos_levantados.append(1)
            else:  # mão esquerda
                if pontos[dedos_ids[0]][0] < pontos[dedos_ids[0] - 1][0]:
                    dedos_levantados.append(0)
                else:
                    dedos_levantados.append(1)

            # --- Lógica para outros dedos ---
            for id in range(1, 5):
                if pontos[dedos_ids[id]][1] < pontos[dedos_ids[id] - 2][1]:
                    dedos_levantados.append(1)
                else:
                    dedos_levantados.append(0)

            # Enviar pela serial
            arduino.write(("".join(map(str, dedos_levantados)) + "\n").encode())

            # Mostrar no vídeo
            texto = f"{label}: {dedos_levantados}"
            cv2.putText(frame, texto, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        # Nenhuma mão detectada → envia 00000
        arduino.write(b"00000\n")

    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

arduino.close()
camera.release()
cv2.destroyAllWindows()
