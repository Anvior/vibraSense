import socketio
import time
import random

sio = socketio.Client()
sio.connect("http://localhost:5000")

while True:
    # Elegir aleatoriamente una variable para que sea anómala (o ninguna)
    posibles = ['mic', 'accel_x', 'accel_y', 'accel_z', None]
    anomalia_en = random.choices(posibles, weights=[1, 1, 1, 1, 10])[0]

    def generar_valor(var):
        if var == 'mic':
            return round(random.uniform(75, 90), 1) if anomalia_en == 'mic' else round(random.uniform(40, 60), 1)
        elif var == 'accel_x':
            return round(random.uniform(4.0, 6.0), 3) if anomalia_en == 'accel_x' else round(random.uniform(-1.5, 1.5), 3)
        elif var == 'accel_y':
            return round(random.uniform(4.0, 6.0), 3) if anomalia_en == 'accel_y' else round(random.uniform(-1.5, 1.5), 3)
        elif var == 'accel_z':
            return round(random.uniform(4.0, 6.0), 3) if anomalia_en == 'accel_z' else round(random.uniform(-1.5, 1.5), 3)

    data = {
        'mic': generar_valor('mic'),
        'accel_x': generar_valor('accel_x'),
        'accel_y': generar_valor('accel_y'),
        'accel_z': generar_valor('accel_z'),
        'anomalia_en': anomalia_en  # 🔴 aquí se indica la variable anómala
    }

    sio.emit("nuevo_dato", data)
    print("📡 Enviado:", data)
    time.sleep(1)
