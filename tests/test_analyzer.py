import pandas as pd
from tf03.analyzer import analyze_dataframe


def test_analyzer_basic(tmp_path, monkeypatch):
    # create minimal data
    df = pd.DataFrame({
        'Elapsed_Time(s)': [0, 1, 2],
        'Distance(cm)': [100, 200, 150],
        'Distance(m)': [1.0, 2.0, 1.5],
        'Strength': [500, 600, 550]
    })
    # attach csv_file attribute to allow saving
    df.csv_file = str(tmp_path / "test.csv")
    analyze_dataframe(df, save_image=True)
    # expect image file exists
    out = tmp_path / "test_analysis.png"
    assert out.exists()
