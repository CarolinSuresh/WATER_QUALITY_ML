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

            if len(values) >= 6:

                ph = float(values[0])
                turb = float(values[1])
                temp = float(values[2])
                mq = float(values[3])
                tds = float(values[4])
                waterlevel = float(values[5])

                # Derived parameters
                do = max(5, 14.6 - 0.4 * temp)
                bod = max(1, (mq / 10) + (turb / 8) + (tds / 150))

                payload = {
                    "pH": ph,
                    "Turbidity (NTU)": turb,
                    "Temperature (°C)": temp,
                    "MQ": mq,
                    "TDS": tds,
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