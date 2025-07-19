import pandas as pd
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError
from sklearn.preprocessing import MinMaxScaler
import joblib

# 1. Cargar y escalar los datos (8 columnas relevantes)
df = pd.read_csv("datos2.csv")  # Asegúrate que existe y tiene las columnas adecuadas
X = df[[ 
    "media_mic", "std_mic",
    "media_ax", "std_ax",
    "media_ay", "std_ay",
    "media_az", "std_az"
]].values

# 2. Normalización
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, "scaler.pkl")

# 3. Definir Autoencoder (8→4→2→4→8)
input_layer = Input(shape=(8,))
encoded = Dense(4, activation='relu')(input_layer)
bottleneck = Dense(2, activation='relu')(encoded)
decoded = Dense(4, activation='relu')(bottleneck)
output_layer = Dense(8, activation='linear')(decoded)

autoencoder = Model(inputs=input_layer, outputs=output_layer)
autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss=MeanSquaredError())

# 4. Entrenamiento
autoencoder.fit(X_scaled, X_scaled, epochs=100, batch_size=16, verbose=1)

# 5. Guardado
autoencoder.save("autoencoder_model.h5")

# 6. Evaluación del error
preds = autoencoder.predict(X_scaled)
errores_globales = np.mean(np.square(X_scaled - preds), axis=1)
errores_por_variable = np.abs(X_scaled - preds)  # sin reducir

# 7. Guardado de errores
np.save("errores_entrenamiento.npy", errores_globales)

# Umbral por variable (percentil 99 por columna)
umbrales_variable = np.percentile(errores_por_variable, 99, axis=0)
np.save("umbrales_variables.npy", umbrales_variable)

# 8. Estadísticas
print("Errores de reconstrucción global:")
print("Media:", errores_globales.mean())
print("Percentil 95:", np.percentile(errores_globales, 95))
print("Percentil 99:", np.percentile(errores_globales, 99))
print("Máximo:", errores_globales.max())

print("\nUmbrales por variable (percentil 99):")
for i, umbral in enumerate(umbrales_variable):
    print(f"Variable {i}: {umbral:.5f}")

print("✅ Autoencoder entrenado, escalador y umbrales guardados.")
