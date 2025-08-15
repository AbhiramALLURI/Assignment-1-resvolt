import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from scipy.signal import find_peaks
import plotly.express as px
import json

app = Flask(__name__)

@app.route('/')
def home():
    # Data loading and processing
    df = pd.read_csv("Sample_Data.csv")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d/%m/%y %H:%M')
    df.set_index('Timestamp', inplace=True)

    
    # Generate the main plot
    plt.figure(figsize=(15, 8))
    plt.plot(df.index, df['Values'], label='Original Value', color='cornflowerblue')
    plt.plot(df.index, df['MA_1000'], label='1000 Value Moving Average', color='red')
    plt.plot(df.index, df['MA_5000'], label='5000 Value Moving Average', color='green')
    plt.title('Values with 1000 and 5000 Value Moving Averages')
    plt.xlabel('Timestamp')
    plt.ylabel('MA_1000')
    plt.legend()
    plt.grid(True)
    # Save plot to a temporary buffer and encode it
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    plot_data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Find peaks, lows, and other data points
    peak_points, _ = find_peaks(df['Values'])
    low_points, _ = find_peaks(-df['Values'])
    peak_data = df.iloc[peak_points]['Values']
    low_data = df.iloc[low_points]['Values']
    below_20 = df[df['Values'] < 20]
    df['Slope'] = df['Values'].diff()
    df['Slope_Change'] = df['Slope'].diff()
    accel_down = df[(df['Slope'] < 0) & (df['Slope_Change'] < 0)]

    # Render the HTML template with the data
    return render_template(
        'index.html',
        plot_data=plot_data,
        peak_data=peak_data.to_string(),
        low_data=low_data.to_string(),
        below_20=below_20[['Values']].to_string(),
        accel_down=accel_down[['Values', 'Slope', 'Slope_Change']].to_string()
    )

if __name__ == '__main__':
    app.run(debug=True)