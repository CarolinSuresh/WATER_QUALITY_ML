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

        if "MLDATA:" in line:

            data = line.split("MLDATA:")[1].strip()
            values = data.split(",")

            # Now expecting 6 values
            if len(values) >= 6:

                ph = float(values[0])
                turb = float(values[1])
                temp = float(values[2])
                do = float(values[3])
                bod = float(values[4])
                waterlevel = float(values[5])   # <-- FIXED

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

            else:
                print("⚠ Incomplete MLDATA:", values)

    except Exception as e:
        print("Error:", e)