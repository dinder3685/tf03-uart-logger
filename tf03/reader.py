"""TF03 LiDAR sensor module for reading distance measurements."""

import serial
import csv
import time
from datetime import datetime
from collections import deque


def parse_frame(frame: bytes):
    """Parse a 7-byte TF03 frame."""
    if len(frame) != 7:
        raise ValueError("Frame must be 7 bytes")
    dist_L, dist_H, strength_L, strength_H, reserved1, reserved2, checksum = frame
    total = 0x59 + 0x59 + dist_L + dist_H + strength_L + strength_H + reserved1 + reserved2
    if (total & 0xFF) != checksum:
        raise ValueError("Checksum failed")
    return dist_L + (dist_H << 8), strength_L + (strength_H << 8)


def make_frame(distance: int, strength: int) -> bytes:
    """Create a TF03 frame."""
    dist_L = distance & 0xFF
    dist_H = (distance >> 8) & 0xFF
    str_L = strength & 0xFF
    str_H = (strength >> 8) & 0xFF
    total = 0x59 + 0x59 + dist_L + dist_H + str_L + str_H
    checksum = total & 0xFF
    return bytes([dist_L, dist_H, str_L, str_H, 0, 0, checksum])


class TF03Visualizer:
    """Read TF03 sensor with live visualization."""

    def __init__(self, port='COM3', baud=115200, max_points=500, timeout=0.1):
        import sys
        try:
            self.ser = serial.Serial(port, baud, timeout=timeout)
        except serial.SerialException as e:
            print(f"Failed to open {port}: {e}")
            sys.exit(1)

        self.distances = deque(maxlen=max_points)
        self.strengths = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)
        self.start_time = time.time()
        self.csv_file = f"tf03_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self._setup_csv()
        self._init_plot()
        
        print(f"TF03 Started on {port}...")
        print(f"Data: {self.csv_file}\n")

    def _setup_csv(self):
        with open(self.csv_file, 'w', newline='') as f:
            csv.writer(f).writerow(['Timestamp', 'Elapsed_Time(s)', 'Distance(cm)', 'Strength', 'Distance(m)'])

    def _init_plot(self):
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('TkAgg')
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.ion()
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(15, 10))
        self.fig.suptitle('TF03 LiDAR Real-Time Distance Sensor - Z-Axis Measurement', fontsize=16, fontweight='bold')
        self.fig.patch.set_facecolor('#f5f5f5')

    def read_sensor(self):
        frames = 0
        while self.ser.in_waiting >= 9:
            if self.ser.read(1) != b'\x59' or self.ser.read(1) != b'\x59':
                continue
            frame = self.ser.read(7)
            try:
                dist, strength = parse_frame(frame)
                t = time.time() - self.start_time
                self.distances.append(dist)
                self.strengths.append(strength)
                self.timestamps.append(t)
                with open(self.csv_file, 'a', newline='') as f:
                    csv.writer(f).writerow([datetime.now().isoformat(), f"{t:.2f}", dist, strength, f"{dist/100:.2f}"])
                print(f"Distance: {dist:4d}cm ({dist/100:.2f}m) | Strength: {strength:5d}")
                frames += 1
            except ValueError:
                pass
        return frames

    def start(self):
        import matplotlib.pyplot as plt
        try:
            while True:
                self.read_sensor()
                if len(self.timestamps) > 1:
                    times = list(self.timestamps)
                    dists = list(self.distances)
                    strengths = list(self.strengths)
                    
                    self.ax1.clear()
                    self.ax1.plot(times, dists, '#1f77b4', linewidth=2.5, marker='o', markersize=2, label='Distance')
                    self.ax1.fill_between(times, dists, alpha=0.15, color='#1f77b4')
                    self.ax1.set_ylabel('Distance (cm)', fontsize=11, fontweight='bold')
                    self.ax1.set_xlabel('Elapsed Time (s)', fontsize=11, fontweight='bold')
                    self.ax1.set_ylim(0, 2500)
                    self.ax1.grid(True, alpha=0.4, linestyle='--', linewidth=0.7)
                    self.ax1.legend(loc='upper right', fontsize=10)
                    self.ax1.set_title('Distance Measurements', fontsize=12, fontweight='bold', pad=10)
                    
                    self.ax2.clear()
                    self.ax2.plot(times, strengths, '#ff7f0e', linewidth=2.5, marker='s', markersize=2, label='Signal Strength')
                    self.ax2.fill_between(times, strengths, alpha=0.15, color='#ff7f0e')
                    self.ax2.set_ylabel('Signal Strength', fontsize=11, fontweight='bold')
                    self.ax2.set_xlabel('Elapsed Time (s)', fontsize=11, fontweight='bold')
                    self.ax2.grid(True, alpha=0.4, linestyle='--', linewidth=0.7)
                    self.ax2.legend(loc='upper right', fontsize=10)
                    self.ax2.set_title('Signal Quality', fontsize=12, fontweight='bold', pad=10)
                    
                    plt.tight_layout()
                    plt.pause(0.05)
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            print("\nStopped")
        finally:
            plt.close('all')
