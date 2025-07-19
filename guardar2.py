import serial
import csv
from datetime import datetime
import socketio

# Configuración
puerto = "COM3"
baudios = 700
nombre_archivo = f"stats_motor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Conexión a la app con Socket.IO
sio = socketio.Client()
try:
    sio.connect("http://localhost:5000")
    print("✅ Conectado al servidor Socket.IO")
except Exception as e:
    print("❌ No se pudo conectar al servidor:", e)

# Abrimos puerto serie y archivo CSV
with serial.Serial(puerto, baudios, timeout=1) as arduino:
    print(f" Conectado a {puerto} — guardando en {nombre_archivo}")
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        encabezado_leido = False

        try:
            while True:
                linea = arduino.readline().decode('utf-8', errors='ignore').strip()
                if not linea:
                    continue

                print("", linea)
                campos = linea.split(",")

                # Validar que hay 9 columnas (timestamp + 8 valores)
                if encabezado_leido and len(campos) == 9:
                    try:
                        escritor.writerow(campos)
                        data = {
                            "timestamp": campos[0],
                            "media_mic": float(campos[1]),
                            "std_mic": float(campos[2]),
                            "media_ax": float(campos[3]),
                            "std_ax": float(campos[4]),
                            "media_ay": float(campos[5]),
                            "std_ay": float(campos[6]),
                            "media_az": float(campos[7]),
                            "std_az": float(campos[8]),
                        }
                        if sio.connected:
                            sio.emit("nuevo_dato", data)
                    except ValueError:
                        print("Datos no numéricos. Línea ignorada.")
                elif not encabezado_leido and "timestamp" in linea:
                    escritor.writerow(campos)
                    encabezado_leido = True
                else:
                     print("Línea ignorada: formato inesperado")

        except KeyboardInterrupt:
            print("Grabación finalizada por el usuario.")
