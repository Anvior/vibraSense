import pandas as pd
from sklearn.svm import OneClassSVM
import pickle

# Cargar el CSV de entrenamiento
df = pd.read_csv("datos.csv")

# Seleccionamos solo las columnas útiles
X = df[["mic", "accel_x", "accel_y", "accel_z"]]

# Entrenar modelo One-Class SVM
modelo = OneClassSVM(kernel="rbf", gamma="auto", nu=0.5)  # Puedes bajar nu para que sea menos sensible
modelo.fit(X)

# Guardar modelo entrenado
with open("modelo.pkl", "wb") as f:
    pickle.dump(modelo, f)

print("✅ Modelo One-Class SVM entrenado y guardado como modelo.pkl")
