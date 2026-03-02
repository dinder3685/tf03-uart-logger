"""TF03 serial port debug - raw data check"""
import serial
import time
import sys

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM12"
BAUDS = [115200, 9600, 57600, 19200, 38400, 230400, 256000]

results = []

for baud in BAUDS:
    line = f"Test: {PORT} @ {baud} baud"
    results.append(line)
    print(line)
    try:
        ser = serial.Serial(PORT, baud, timeout=2)
        time.sleep(0.3)
        ser.reset_input_buffer()

        start = time.time()
        total_bytes = 0
        raw_sample = b''

        while time.time() - start < 3:
            waiting = ser.in_waiting
            if waiting > 0:
                data = ser.read(waiting)
                total_bytes += len(data)
                if len(raw_sample) < 50:
                    raw_sample += data

        ser.close()

        if total_bytes > 0:
            line = f"  DATA RECEIVED! {total_bytes} bytes / 3 sec"
            results.append(line)
            print(line)
            hex_str = ' '.join(f'{b:02X}' for b in raw_sample[:50])
            line = f"  Raw hex (first 50): {hex_str}"
            results.append(line)
            print(line)

            count_59 = 0
            for i in range(len(raw_sample) - 1):
                if raw_sample[i] == 0x59 and raw_sample[i+1] == 0x59:
                    count_59 += 1
            if count_59 > 0:
                line = f"  TF03 header (0x59 0x59) found! ({count_59}x)"
                results.append(line)
                print(line)
            else:
                line = f"  TF03 header (0x59 0x59) NOT found"
                results.append(line)
                print(line)

            line = f"  >>> CORRECT BAUD RATE: {baud} <<<"
            results.append(line)
            print(line)
            break
        else:
            line = f"  NO DATA"
            results.append(line)
            print(line)

    except serial.SerialException as e:
        line = f"  PORT ERROR: {e}"
        results.append(line)
        print(line)
        break
else:
    line = "NO DATA AT ANY BAUD RATE! Check: TX/RX wiring, power, USB-TTL converter"
    results.append(line)
    print(line)

# Save results to file
with open("debug_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
print("\nResults saved to debug_result.txt")
