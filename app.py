from flask import Flask, render_template, send_file, request, redirect, url_for, session
from fpdf import FPDF
from flask_socketio import SocketIO, emit
import joblib
import pandas as pd
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import smtplib
from email.message import EmailMessage
import matplotlib
from collections import deque
from datetime import datetime, timedelta

anomalías_recientes = deque()
ultimo_envio_alerta = None

matplotlib.use('Agg')

# === SETUP ===
app = Flask(__name__)
app.secret_key = 'clave_muy_segura_123'

socketio = SocketIO(app, cors_allowed_origins="*")
modelo = joblib.load("modelo.pkl")

usuarios = {
    "admin": "123",
}

datos_recibidos = []

@app.route('/', methods=['GET'])
def inicio():
    if 'usuario' in session:
        return render_template('dashboard.html', usuario=session['usuario'])
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user = request.form['usuario']
    pwd = request.form['password']
    if user in usuarios and usuarios[user] == pwd:
        session['usuario'] = user
        return redirect(url_for('inicio'))
    return "❌ Usuario o contraseña incorrectos", 401

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('inicio'))

@app.route('/')
def index():
    return render_template('index.html')
@socketio.on('nuevo_dato')
def manejar_dato(data):
    global ultimo_envio_alerta

    entrada = pd.DataFrame([{
        'mic': data['mic'],
        'accel_x': data['accel_x'],
        'accel_y': data['accel_y'],
        'accel_z': data['accel_z']
    }])

    pred = modelo.predict(entrada)[0]
    data['anomalía'] = bool(pred == -1)

    if data['anomalía']:
        if datos_recibidos:
            df_hist = pd.DataFrame(datos_recibidos)
            desviaciones = {
                'mic': abs(data['mic'] - df_hist['mic'].mean()),
                'accel_x': abs(data['accel_x'] - df_hist['accel_x'].mean()),
                'accel_y': abs(data['accel_y'] - df_hist['accel_y'].mean()),
                'accel_z': abs(data['accel_z'] - df_hist['accel_z'].mean()),
            }
            data['anomalia_en'] = max(desviaciones, key=desviaciones.get)
        else:
            data['anomalia_en'] = 'mic'  # por defecto si es el primer dato
    else:
        data['anomalia_en'] = None


        ahora = datetime.now()
        anomalías_recientes.append(ahora)

        # Limpiar anomalías de hace más de 60 segundos
        hace_un_minuto = ahora - timedelta(seconds=60)
        while anomalías_recientes and anomalías_recientes[0] < hace_un_minuto:
            anomalías_recientes.popleft()

        if len(anomalías_recientes) > 5:
            if not ultimo_envio_alerta or (ahora - ultimo_envio_alerta).total_seconds() > 20:
                enviar_alerta_critica(len(anomalías_recientes))
                ultimo_envio_alerta = ahora

    datos_recibidos.append({**data, 'timestamp': datetime.now().strftime('%H:%M:%S')})
    emit('dato_analizado', data, broadcast=True)


@app.route('/exportar', methods=['POST'])
def exportar():
    os.makedirs('export', exist_ok=True)

    csv_path = 'export/datos.csv'
    campos = ['timestamp', 'mic', 'accel_x', 'accel_y', 'accel_z', 'anomalía', 'anomalia_en']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(datos_recibidos)

    df = pd.DataFrame(datos_recibidos)
    colores = {'mic': 'blue', 'accel_x': 'green', 'accel_y': 'orange', 'accel_z': 'purple'}

    def guardar_grafico(col, color):
        fig, ax = plt.subplots()

        normales = df[(df['anomalía'] == False)]
        anomalias = df[(df['anomalía'] == True) & (df['anomalia_en'] == col)]

        ax.plot(df['timestamp'], df[col], label=col.capitalize(), color=color)
        ax.scatter(anomalias['timestamp'], anomalias[col], color='red', label='Anomalía', zorder=5)

        ax.set_title(f'{col.capitalize()} en el tiempo')
        ax.set_xticks(df['timestamp'][::max(1, len(df)//5)])
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True)
        ax.legend()
        fig.tight_layout()
        fig.savefig(f'export/{col}.png')
        plt.close()


    for col, color in colores.items():
        guardar_grafico(col, color)

    pdf_path = 'export/Informe_Vibraciones_IA.pdf'
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Informe de Vibraciones y Detección de Anomalías', ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, """
Este informe ha sido generado automáticamente a partir de los datos recogidos por los sensores en tiempo real, utilizando un sistema de detección de anomalías basado en aprendizaje automático.

El sistema analiza constantemente los valores capturados por el micrófono y el acelerómetro, y los compara con patrones normales de comportamiento. Para ello, utiliza un modelo llamado Isolation Forest, que es especialmente útil para detectar desviaciones en grandes volúmenes de datos sin necesidad de etiquetar previamente lo que es normal o no.

Una predicción de -1 significa que el sistema ha marcado ese punto como anómalo.
Una predicción de 1 indica que el punto es normal.

En los gráficos se puede observar la evolución temporal de las variables medidas. Los puntos marcados en rojo representan posibles anomalías detectadas por el sistema, mientras que los puntos negros indican lecturas dentro de lo esperado.
""")

    for col in colores:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f'Gráfico de {col}', ln=True)
        pdf.image(f'export/{col}.png', w=180)

    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, 'Análisis de Resultados', ln=True)
    pdf.set_font("Arial", '', 12)

    total = len(df)
    pdf.multi_cell(0, 10, f"Total de señales analizadas: {total}\n")

    for col in colores:
        media = df[col].mean()
        std = df[col].std()
        umbral_sup = media + 2 * std
        umbral_inf = media - 2 * std

        outliers = df[(df['anomalía'] == True) & (df['anomalia_en'] == col)]

        porcentaje = 100 * len(outliers) / total

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f" Análisis de {col}", ln=True)
        pdf.set_font("Arial", '', 12)

        pdf.multi_cell(0, 10, f"""
Valores anómalos de mic corresponden a los detectados por el modelo de IA como anómalos, y específicamente cuando el modelo identifica esa variable como fuente probable de la anomalía.
- Media: {media:.2f}
- Desviación estándar: {std:.2f}
- Umbral inferior: {umbral_inf:.2f}
- Umbral superior: {umbral_sup:.2f}
- Anomalías detectadas: {len(outliers)} ({porcentaje:.1f}% del total)

Esto indica que {porcentaje:.1f}% de las lecturas de {col} presentan un comportamiento fuera de lo esperado.
""")

    pdf.output(pdf_path)
    enviar_correo(['anartz2001@gmail.com'], csv_path, pdf_path)
    return 'Exportado y enviado', 200

def enviar_correo(destinatarios, csv_path, pdf_path):
    msg = EmailMessage()
    msg['Subject'] = '📊 Reporte de Vibraciones'
    msg['From'] = 'anartz2001@gmail.com'
    msg['To'] = ', '.join(destinatarios)
    msg.set_content('Adjunto el CSV con los datos y la gráfica PDF generada.')

    with open(csv_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='text', subtype='csv', filename='datos.csv')
    with open(pdf_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='Informe_Vibraciones_IA.pdf')

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('anartz2001@gmail.com', 'bhhs iluo suhs utft')  # ⚠️ Cámbialo en producción
        smtp.send_message(msg)

def enviar_alerta_critica(total):
    msg = EmailMessage()
    msg['Subject'] = '⚠️ ALERTA CRÍTICA: Múltiples anomalías detectadas'
    msg['From'] = 'anartz2001@gmail.com'
    msg['To'] = 'anartz2001@gmail.com'
    msg.set_content(f"""
Se han detectado {total} anomalías en el último minuto.

Adjuntamos los datos recopilados (CSV) y el informe generado (PDF) para su revisión inmediata.
    """)

    # Asegurar que los archivos existen
    csv_path = 'export/datos.csv'
    pdf_path = 'export/Informe_Vibraciones_IA.pdf'

    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'rb') as f:
                msg.add_attachment(f.read(), maintype='text', subtype='csv', filename='datos.csv')
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='Informe_Vibraciones_IA.pdf')

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('anartz2001@gmail.com', 'bhhs iluo suhs utft')  # ⚠️ cámbialo por variable segura
            smtp.send_message(msg)

        print(f"📧 Alerta crítica enviada con {total} anomalías y archivos adjuntos.")
    except Exception as e:
        print(f"❌ Error al enviar alerta crítica: {e}")


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
