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

                # -------- FIX 1: NORMALIZE MQ --------
                mq_effective = max(0, mq - 60)

                # -------- FIX 2: HANDLE TDS --------
                if tds == 0:
                    tds = 100   # default realistic value

                # -------- FIX 3: UPDATED DO --------
                do = 14.6 - 0.35 * temp

                # -------- FIX 4: UPDATED BOD --------
                bod = (mq_effective / 15) + (turb / 10) + (tds / 200)

                payload = {
                    "pH": ph,
                    "Turbidity (NTU)": turb,
                    "Temperature (°C)": temp,
                    "DO (mg/L)": do,
                    "BOD (mg/L)": bod,
                    "WaterLevel": waterlevel,
                    "Ammonia (MQ)": mq,
                    "TDS (ppm)": tds
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