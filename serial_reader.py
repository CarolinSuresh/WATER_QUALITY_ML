import serial
import requests
import time

PORT = "COM5"   # change if your ESP32 uses another port
BAUD = 115200

print("Connecting to ESP32...")

ser = serial.Serial(PORT, BAUD, timeout=1)

time.sleep(2)

print("Connected. Reading data...\n")

while True:

    try:
        line = ser.readline().decode().strip()

        if not line:
            continue

        print("Serial:", line)

        if "MLDATA:" in line:

            data = line.split("MLDATA:")[1]

            values = data.split(",")

            ph = float(values[0])
            turb = float(values[1])
            temp = float(values[2])
            do = float(values[3])
            bod = float(values[4])

            payload = {
                "pH": ph,
                "Turbidity (NTU)": turb,
                "Temperature (°C)": temp,
                "DO (mg/L)": do,
                "BOD (mg/L)": bod
            }

            response = requests.post(
                "http://127.0.0.1:5000/predict",
                json=payload
            )

            print("ML Prediction:", response.json())
            print("--------------------------------")

    except Exception as e:
        print("Error:", e)
