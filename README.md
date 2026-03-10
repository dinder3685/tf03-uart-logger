# TF03 Serial Sensor Library

<img width="823" height="482" alt="image" src="https://github.com/user-attachments/assets/341c8ac3-f512-4605-b863-80818d22b242" />

##  Characteristics of UART 

<img width="889" height="493" alt="image" src="https://github.com/user-attachments/assets/a8451790-e8f0-49b4-8ae6-3386533ebee8" />

 ##  Data communication: User protocol frame format of UART
<img width="1270" height="356" alt="image" src="https://github.com/user-attachments/assets/7eeea6f6-68ff-4dbf-9fdf-7baf572df5fd" />

[Datasheet]([datasheet]([url](https://en.benewake.com/uploadfiles/2024/04/20240426134845102.pdf)) )



This repository provides a small Python package for interacting with the TF03
LiDAR distance sensor over a serial connection. It includes a real‑time
visualizer, CSV logging, and post‑test analysis tools.

## Features

- Read distance & signal strength from TF03
- Live plot of measurements (0–25 m range) with real-time updates
- Automatic CSV logging of every reading (timestamp, distance, signal strength)
- End‑of‑test summary graph and statistics
- Data analysis utilities for offline processing

## Installation

1. Clone the repo:

```bash
git clone <repo-url> tf03_serial_project
cd tf03_serial_project
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```
python read_tf03.py <COM_PORT>
```

Example:

```
python read_tf03.py COM7
```

The script will open a window showing live distance and strength plots. Close the
window (or press Ctrl+C) to stop the test; an analysis image and statistics will
be generated automatically.

## Sample Output

The system generates analysis reports with visualization:

```
python read_tf03.py COM7
```

An analysis graph and CSV log are created automatically after measurement.

### Library API

You can also import the package from your own code:

```python
from tf03 import TF03Visualizer, analyze_csv

vis = TF03Visualizer(port='COM7')
vis.start()  # blocking
# after stop it will have created a CSV file
analyze_csv(vis.csv_file)
```

## Testing

Run unit tests with pytest:

```bash
pytest tests
```

Tests cover frame parsing, visualization buffer handling, and analysis logic.

## Project Structure

```text
├── tf03/                # Python package
│   ├── __init__.py
│   ├── reader.py        # serial reader & visualizer
│   └── analyzer.py      # data analysis functions
├── tests/               # pytest test cases
├── read_tf03.py         # CLI launcher
├── debug_serial.py      # Serial debugging utility
├── requirements.txt
└── README.md
```

## License

MIT (or whichever license you prefer)
