# TF03 Serial Sensor Library

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
