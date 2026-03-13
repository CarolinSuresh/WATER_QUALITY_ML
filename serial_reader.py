import serial
import requests

PORT = "COM5"
BAUD = 115200

ser = serial.Serial(PORT, BAUD)

print("Reading LoRa data...")

while True:

    line = ser.readline().decode().strip()

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

        res = requests.post(
            "http://127.0.0.1:5000/predict",
            json=payload
        )

        print(res.json())