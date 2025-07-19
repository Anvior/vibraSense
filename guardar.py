import serial
import csv
from datetime import datetime
import socketio

# Configuración
puerto = "COM3"
baudios = 700
nombre_archivo = f"datos_micro_motor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Conexión a la app con Socket.IO
sio = socketio.Client()
try:
    sio.connect("http://localhost:5000")
    print("✅ Conectado al servidor Socket.IO")
except Exception as e:
    print("❌ No se pudo conectar al servidor:", e)

# Abrimos puerto serie y archivo CSV
with serial.Serial(puerto, baudios, timeout=1) as arduino:
    print(f"📡 Conectado a {puerto} — guardando en {nombre_archivo}")
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        encabezado_leido = False

        try:
            while True:
                linea = arduino.readline().decode('utf-8', errors='ignore').strip()
                if not linea:
                    continue

                print("📨", linea)
                campos = linea.split(",")

                # Escritura en CSV solo si es válida (5 campos numéricos)
                if encabezado_leido and len(campos) == 5:
                    try:
                        escritor.writerow(campos)
                        data = {
                            "timestamp": campos[0],
                            "mic": float(campos[1]),
                            "accel_x": float(campos[2]),
                            "accel_y": float(campos[3]),
                            "accel_z": float(campos[4]),
                            "anomalia_en": None
                        }
                        if sio.connected:
                            sio.emit("nuevo_dato", data)
                    except ValueError:
                        print("⚠️ Datos no numéricos. Línea ignorada.")
                elif not encabezado_leido and "timestamp" in linea:
                    escritor.writerow(campos)
                    encabezado_leido = True
                else:
                    print("⏭️ Línea ignorada: formato inesperado")

        except KeyboardInterrupt:
            print("🛑 Grabación finalizada por el usuario.")
