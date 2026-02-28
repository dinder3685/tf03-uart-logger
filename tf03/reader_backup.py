import pandas as pd
import matplotlib.pyplot as plt
import glob
import sys
from pathlib import Path

def analyze_tf03_data(csv_file=None):
    """Analyze and visualize TF03 test data from CSV"""
    
    # Find the latest CSV file if not specified
    if csv_file is None:
        csv_files = glob.glob('tf03_data_*.csv')
        if not csv_files:
            print("No CSV files found. Run the sensor visualization first!")
            sys.exit(1)
        csv_file = sorted(csv_files)[-1]  # Get the latest file
        print(f"Using: {csv_file}")
    
    # Read CSV data
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
    
    # Extract data
    time = df['Elapsed_Time(s)'].values
    distance_cm = df['Distance(cm)'].values
    distance_m = df['Distance(m)'].values
    strength = df['Strength'].values
    
    # Calculate statistics
    min_dist = distance_cm.min()
    max_dist = distance_cm.max()
    avg_dist = distance_cm.mean()
    total_time = time[-1] if len(time) > 0 else 0
    num_readings = len(distance_cm)
    
    print(f"\n{'='*60}")
    print(f"{'OVERALL TEST ANALYSIS':^60}")
    print(f"{'='*60}")
    print(f"CSV File: {csv_file}")
    print(f"Total Duration: {total_time:.2f} seconds")
    print(f"Total Measurements: {num_readings}")
    print(f"Sampling Rate: {num_readings/total_time:.1f} Hz" if total_time > 0 else "N/A")
    print(f"\nDistance Statistics:")
    print(f"  Minimum: {min_dist:.0f} cm ({min_dist/100:.2f} m)")
    print(f"  Maximum: {max_dist:.0f} cm ({max_dist/100:.2f} m)")
    print(f"  Average: {avg_dist:.0f} cm ({avg_dist/100:.2f} m)")
    print(f"  Range: {max_dist - min_dist:.0f} cm ({(max_dist-min_dist)/100:.2f} m)")
    print(f"\nSignal Strength:")
    print(f"  Min: {strength.min()}")
    print(f"  Max: {strength.max()}")
    print(f"  Average: {strength.mean():.0f}")
    print(f"{'='*60}\n")
    
    # Create comprehensive figure
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle(f'TF03 Distance Sensor - Complete Test Analysis\n({csv_file})', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    # 1. Main distance plot
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(time, distance_cm, 'b-', linewidth=2, label='Distance')
    ax1.axhline(y=avg_dist, color='r', linestyle='--', linewidth=2, label=f'Average: {avg_dist:.0f}cm')
    ax1.fill_between(time, min_dist, max_dist, alpha=0.2, color='blue')
    ax1.set_xlabel('Time (s)', fontsize=10)
    ax1.set_ylabel('Distance (cm)', fontsize=10)
    ax1.set_title('Distance Over Time', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(0, 2500)
    
    # 2. Distance in meters
    ax2 = plt.subplot(3, 2, 2)
    ax2.plot(time, distance_m, 'g-', linewidth=2, label='Distance')
    ax2.axhline(y=avg_dist/100, color='r', linestyle='--', linewidth=2, label=f'Average: {avg_dist/100:.2f}m')
    ax2.set_xlabel('Time (s)', fontsize=10)
    ax2.set_ylabel('Distance (m)', fontsize=10)
    ax2.set_title('Distance in Meters', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim(0, 25)
    
    # 3. Signal strength
    ax3 = plt.subplot(3, 2, 3)
    ax3.plot(time, strength, 'orange', linewidth=1.5, marker='o', markersize=2)
    ax3.fill_between(time, strength, alpha=0.3, color='orange')
    ax3.set_xlabel('Time (s)', fontsize=10)
    ax3.set_ylabel('Signal Strength', fontsize=10)
    ax3.set_title('Signal Quality Over Time', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Histogram of distances
    ax4 = plt.subplot(3, 2, 4)
    ax4.hist(distance_cm, bins=50, color='blue', alpha=0.7, edgecolor='black')
    ax4.axvline(x=avg_dist, color='r', linestyle='--', linewidth=2, label=f'Mean: {avg_dist:.0f}cm')
    ax4.axvline(x=min_dist, color='g', linestyle='--', linewidth=1, label=f'Min: {min_dist:.0f}cm')
    ax4.axvline(x=max_dist, color='purple', linestyle='--', linewidth=1, label=f'Max: {max_dist:.0f}cm')
    ax4.set_xlabel('Distance (cm)', fontsize=10)
    ax4.set_ylabel('Frequency', fontsize=10)
    ax4.set_title('Distance Distribution', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Distance change rate (derivative)
    ax5 = plt.subplot(3, 2, 5)
    if len(time) > 1:
        distance_change = [(distance_cm[i] - distance_cm[i-1]) for i in range(1, len(distance_cm))]
        time_diff = time[1:]
        ax5.plot(time_diff, distance_change, 'purple', linewidth=1, marker='o', markersize=2)
        ax5.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax5.fill_between(time_diff, distance_change, alpha=0.3, color='purple')
        ax5.set_xlabel('Time (s)', fontsize=10)
        ax5.set_ylabel('Distance Change (cm/sample)', fontsize=10)
        ax5.set_title('Distance Change Rate', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3)
    
    # 6. Statistics text box
    ax6 = plt.subplot(3, 2, 6)
    ax6.axis('off')
    stats_text = f"""
TEST SUMMARY STATISTICS

Total Duration: {total_time:.2f} seconds
Total Measurements: {num_readings}
Sampling Rate: {num_readings/total_time:.1f} Hz

DISTANCE (cm):
  Minimum: {min_dist:.0f} cm
  Maximum: {max_dist:.0f} cm
  Average: {avg_dist:.0f} cm
  Range: {max_dist - min_dist:.0f} cm
  Std Dev: {distance_cm.std():.0f} cm

DISTANCE (m):
  Minimum: {min_dist/100:.2f} m
  Maximum: {max_dist/100:.2f} m
  Average: {avg_dist/100:.2f} m
  Range: {(max_dist - min_dist)/100:.2f} m

SIGNAL STRENGTH:
  Minimum: {strength.min()}
  Maximum: {strength.max()}
  Average: {strength.mean():.0f}
    """
    ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, 
            fontsize=10, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save figure
    output_file = csv_file.replace('.csv', '_analysis.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Graph saved as: {output_file}\n")
    
    plt.show()

if __name__ == '__main__':
    csv_file = sys.argv[1] if len(sys.argv) > 1 else None
    analyze_tf03_data(csv_file)
