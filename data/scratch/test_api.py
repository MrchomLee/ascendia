import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("No hay API KEY")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

payload = {
    "contents": [{"parts": [{"text": "Hola, di 'Conexion exitosa' si me escuchas."}]}]
}

print("Enviando petición a la API...")
start = time.time()
try:
    response = requests.post(url, json=payload, timeout=15)
    print(f"Código de estado HTTP: {response.status_code}")
    print(f"Respuesta de la API:\n{response.text[:200]}")
    if response.status_code == 429:
        print("\n¡ERROR 429! Sí, se te han acabado los tokens/cuota (Quota Exceeded).")
except requests.exceptions.Timeout:
    print("\n¡TIMEOUT! La conexión se quedó congelada y nunca respondió.")
except requests.exceptions.ConnectionError as e:
    print(f"\n¡ERROR DE CONEXIÓN! {e}")
finally:
    print(f"Tiempo transcurrido: {time.time() - start:.2f} segundos")
