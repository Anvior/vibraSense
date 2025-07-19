# VibraSense – AI-Enhanced Vibration & Sound Monitoring System  
Real-time anomaly detection for electric motors using sensor data, embedded intelligence and machine learning.

VIDEO: https://drive.google.com/file/d/1FYJcLvd5IdcW8n7_DGq1phXYoEPvjXAr/view



---

## 🚀 Overview

VibraSense is a modular edge-to-cloud system designed to monitor small electric motors by capturing vibration and acoustic signals. It integrates real-time sensor acquisition, autoencoder-based anomaly detection, and PDF/CSV reporting—all optimized for reliability and educational/industrial use.

The project was built as a full-stack IoT + AI solution, with a focus on interpretability, automation, and data-driven maintenance.

---

## 🧠 Key Features

🎙️ Real-time data acquisition from accelerometer (3 axes) and microphone  
📊 Statistical processing: means, deviations and multivariate correlation  
🤖 AI-based detection with a trained autoencoder (TensorFlow/Keras)  
📉 Dynamic thresholding and alert logic based on reconstruction error  
📬 Automatic email alerts when anomalies are detected (SMTP integration)  
📎 Manual trigger for exporting full reports (CSV, PNGs, PDF summary)  
🖥️ Minimal Flask dashboard for local review

---

## 📦 Tech Stack

| Layer     | Technologies |
|-----------|--------------|
| Firmware  | Arduino UNO |
| Backend   | Python, Flask, NumPy, Matplotlib, Scikit-learn, TensorFlow |
| Alerts    | smtplib, MIME (Python standard library) |
| Exports   | CSV, PNG, PDF (ReportLab/Matplotlib) |
| AI Model  | Autoencoder (unsupervised anomaly detection) |

---

## 🏗️ Architecture

The system is structured into modular components:

vibraSense/
├── app3.py # Main entry point
├── entrenar_autoencoder.py
├── guardar2.py # Data acquisition logic
├── simulador.py # Manual data injector
├── templates/ # Flask frontend (basic)
├── export/ # PNGs, PDFs, CSV reports
├── modelo.pkl # Saved AI model
├── scaler.pkl # StandardScaler object
├── umbrales_variables.npy

---

## 🔧 How to Run

1. Clone the repo:
```bash
git clone https://github.com/Anvior/vibraSense.git
cd vibraSense
Install dependencies:


pip install -r requirements.txt

Run the app:

python app3.py
python guardar2.py

🌍 Project Value
VibraSense is more than a technical showcase.

It is:

Applicable to predictive maintenance in industrial settings

Adaptable to educational environments

Designed with Swiss-grade modularity and clarity

Built with autonomy, reliability, and scalable intent

👨‍💻 Author
Anartz Azumendi Abaroa
🎓 Dual Bachelor in Computer Engineering & Industrial Electronics
📍 Based in Spain, available for relocation to Zürich or elsewhere in Switzerland
📧 anartz2001@gmail.com

Ready to further develop, adapt or deploy VibraSense in industrial environments.  



