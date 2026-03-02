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
    """Read TF03 sensor with live visualization using FuncAnimation."""

    def __init__(self, port='COM3', baud=115200, max_points=500, timeout=0.5):
        import sys
        try:
            self.ser = serial.Serial(port, baud, timeout=timeout)
        except serial.SerialException as e:
            print(f"Failed to open {port}: {e}")
            sys.exit(1)

        # Flush any stale data in the serial buffer
        time.sleep(0.5)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        self.max_points = max_points
        self.distances = deque(maxlen=max_points)
        self.strengths = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)
        self.start_time = time.time()
        self.frame_count = 0
        self.csv_file = f"tf03_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self._setup_csv()
        self._init_plot()

        print(f"TF03 Started on {port} @ {baud} baud")
        print(f"Data: {self.csv_file}")
        print(f"Pencereyi kapatarak durdurabilirsiniz.\n")

    def _setup_csv(self):
        with open(self.csv_file, 'w', newline='') as f:
            csv.writer(f).writerow(['Timestamp', 'Elapsed_Time(s)', 'Distance(cm)', 'Strength', 'Distance(m)'])

    def _init_plot(self):
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation

        plt.style.use('seaborn-v0_8-darkgrid')
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(14, 9))
        self.fig.suptitle('TF03 LiDAR Real-Time Sensor', fontsize=16, fontweight='bold')
        self.fig.patch.set_facecolor('#f5f5f5')

        # Distance plot — max 20m = 2000cm
        self.line1, = self.ax1.plot([], [], '#1f77b4', linewidth=2, marker='o', markersize=2, label='Distance')
        self.fill1 = None
        self.ax1.set_ylabel('Distance (cm)', fontsize=11, fontweight='bold')
        self.ax1.set_xlabel('Elapsed Time (s)', fontsize=11, fontweight='bold')
        self.ax1.set_ylim(0, 2000)
        self.ax1.set_xlim(0, 10)
        self.ax1.grid(True, alpha=0.4, linestyle='--', linewidth=0.7)
        self.ax1.legend(loc='upper right', fontsize=10)
        self.ax1.set_title('Distance (max 20m)', fontsize=12, fontweight='bold', pad=10)

        # Strength plot
        self.line2, = self.ax2.plot([], [], '#ff7f0e', linewidth=2, marker='s', markersize=2, label='Signal Strength')
        self.ax2.set_ylabel('Signal Strength', fontsize=11, fontweight='bold')
        self.ax2.set_xlabel('Elapsed Time (s)', fontsize=11, fontweight='bold')
        self.ax2.set_xlim(0, 10)
        self.ax2.grid(True, alpha=0.4, linestyle='--', linewidth=0.7)
        self.ax2.legend(loc='upper right', fontsize=10)
        self.ax2.set_title('Signal Quality', fontsize=12, fontweight='bold', pad=10)

        # Status text
        self.status_text = self.ax1.text(0.02, 0.95, 'Sensör bekleniyor...',
                                          transform=self.ax1.transAxes, fontsize=10,
                                          verticalalignment='top',
                                          bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

        plt.tight_layout()

        # FuncAnimation — calls _update_plot every 50ms
        self._anim = FuncAnimation(self.fig, self._update_plot, interval=50,
                                   blit=False, cache_frame_data=False)

    def _read_one_frame(self):
        """Try to read one TF03 frame. Returns (dist, strength) or None."""
        # Sync to header: look for 0x59 0x59
        b1 = self.ser.read(1)
        if not b1 or b1 != b'\x59':
            return None
        b2 = self.ser.read(1)
        if not b2 or b2 != b'\x59':
            return None
        # Read 7 data bytes
        data = self.ser.read(7)
        if len(data) != 7:
            return None
        try:
            return parse_frame(data)
        except ValueError:
            return None

    def read_sensor(self):
        """Read all available frames from serial buffer."""
        frames = 0
        # Process all bytes currently in buffer
        max_reads = 50  # prevent infinite loop
        while self.ser.in_waiting >= 9 and max_reads > 0:
            max_reads -= 1
            result = self._read_one_frame()
            if result is None:
                continue
            dist, strength = result
            t = time.time() - self.start_time
            self.distances.append(dist)
            self.strengths.append(strength)
            self.timestamps.append(t)
            with open(self.csv_file, 'a', newline='') as f:
                csv.writer(f).writerow([datetime.now().isoformat(), f"{t:.2f}", dist, strength, f"{dist/100:.2f}"])
            self.frame_count += 1
            frames += 1

        # If buffer was empty, try a single blocking read (uses serial timeout)
        if frames == 0:
            result = self._read_one_frame()
            if result is not None:
                dist, strength = result
                t = time.time() - self.start_time
                self.distances.append(dist)
                self.strengths.append(strength)
                self.timestamps.append(t)
                with open(self.csv_file, 'a', newline='') as f:
                    csv.writer(f).writerow([datetime.now().isoformat(), f"{t:.2f}", dist, strength, f"{dist/100:.2f}"])
                self.frame_count += 1
                frames += 1

        if frames > 0:
            dist = self.distances[-1]
            strength = self.strengths[-1]
            print(f"[{self.frame_count:5d}] Distance: {dist:5d}cm ({dist/100:6.2f}m) | Strength: {strength:5d}")

        return frames

    def _update_plot(self, _frame):
        """Called by FuncAnimation — read sensor + update graph lines."""
        self.read_sensor()

        elapsed = time.time() - self.start_time

        if len(self.timestamps) > 0:
            times = list(self.timestamps)
            dists = list(self.distances)
            strengths = list(self.strengths)

            # Update distance line
            self.line1.set_data(times, dists)
            x_max = max(10, times[-1] + 2)
            x_min = max(0, times[-1] - 60)
            self.ax1.set_xlim(x_min, x_max)

            # Update fill
            if self.fill1 is not None:
                self.fill1.remove()
            self.fill1 = self.ax1.fill_between(times, dists, alpha=0.15, color='#1f77b4')

            # Update strength line
            self.line2.set_data(times, strengths)
            self.ax2.set_xlim(x_min, x_max)
            self.ax2.relim()
            self.ax2.autoscale_view(scaley=True, scalex=False)

            # Update status
            last_dist = dists[-1]
            self.status_text.set_text(
                f'Frames: {self.frame_count} | Son: {last_dist}cm ({last_dist/100:.2f}m) | Süre: {elapsed:.1f}s')
            self.status_text.set_bbox(dict(boxstyle='round', facecolor='#90EE90', alpha=0.8))
        else:
            # No data yet
            self.status_text.set_text(f'Sensör bekleniyor... ({elapsed:.0f}s)')

        return self.line1, self.line2

    def start(self):
        """Show the live plot window (blocks until closed)."""
        import matplotlib.pyplot as plt
        try:
            plt.show()
        except KeyboardInterrupt:
            pass
        finally:
            print("\nStopped")
            try:
                self.ser.close()
            except Exception:
                pass
