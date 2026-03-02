"""TF03 LiDAR Sensor - CLI Launcher with Live Visualization & Analysis"""

import sys
import os
from tf03 import TF03Visualizer, analyze_csv


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "COM12"
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

    print(f"TF03 LiDAR başlatılıyor...")
    print(f"Port: {port} | Baud: {baud}")
    print(f"Durdurmak için pencereyi kapatın veya Ctrl+C\n")

    vis = TF03Visualizer(port=port, baud=baud)
    vis.start()

    # Test bittiğinde otomatik analiz (sadece veri varsa)
    if vis.csv_file and os.path.exists(vis.csv_file):
        # Check if CSV has any data rows
        with open(vis.csv_file, 'r') as f:
            lines = f.readlines()
        if len(lines) > 1:  # header + at least 1 data row
            print(f"\nAnaliz raporu oluşturuluyor ({len(lines)-1} ölçüm)...")
            try:
                analyze_csv(vis.csv_file)
            except Exception as e:
                print(f"Analiz hatası: {e}")
        else:
            print(f"\nSensörden veri alınamadı — analiz atlandı.")
            print(f"Kontrol edin:")
            print(f"  1. TF03 sensörü {port} portuna bağlı mı?")
            print(f"  2. Kablo bağlantıları: TX→RX, RX→TX, GND→GND")
            print(f"  3. Sensör beslemesi: 5V (veya 5-30V)")
            print(f"  4. Baud rate: {baud} (TF03 varsayılan: 115200)")


if __name__ == "__main__":
    main()
