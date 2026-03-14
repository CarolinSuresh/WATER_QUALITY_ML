import serial
import requests

PORT = "COM5"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

print("Reading LoRa data...\n")

while True:

    try:
        line = ser.readline().decode(errors='ignore').strip()

        if line:
            print("SERIAL:", line)

        # -------- READ MACHINE DATA FROM RX --------
        if "MLDATA:" in line:

            data = line.split("MLDATA:")[1].strip()
            values = data.split(",")

            if len(values) >= 5:

                ph = float(values[0])
                turb = float(values[1])
                temp = float(values[2])
                do = float(values[3])   # MQ ammonia used as DO input
                bod = float(values[4])  # TDS used as BOD input

                waterlevel = 0   # RX doesn't send WL in MLDATA

                payload = {
                    "pH": ph,
                    "Turbidity (NTU)": turb,
                    "Temperature (°C)": temp,
                    "DO (mg/L)": do,
                    "BOD (mg/L)": bod,
                    "WaterLevel": waterlevel
                }

                print("Sending to ML:", payload)

                res = requests.post(
                    "http://127.0.0.1:5000/predict",
                    json=payload
                )

                print("ML RESULT:", res.json())
                print("---------------------------")

    except Exception as e:
        print("Error:", e)