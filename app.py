from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import sys
import os
sys.path.append('src')
from src.update_all_data import update_all_data
from matplotlib.patches import Rectangle

app = Flask(__name__)

def plot_to_uri(plt):
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    uri = 'data:image/png;base64,' + base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    return uri

def create_infographic(data, title):
    fig, ax = plt.subplots()
    ax.text(0.5, 0.9, f"Mean: {data.mean():.6f}", ha='center')
    ax.text(0.5, 0.8, f"Std Dev: {data.std():.6f}", ha='center')
    ax.text(0.5, 0.7, f"Max: {data.max():.6f}", ha='center')
    ax.text(0.5, 0.6, f"Min: {data.min():.6f}", ha='center')
    ax.text(0.5, 0.5, f"Last price: {data.iloc[0]:.6f}", ha='center')
    ax.text(0.5, 0.4, f"Last price*1.03: {data.iloc[0]*1.03:.6f}", ha='center')

    box = Rectangle((0, 0), 1, 1, fill=False, edgecolor="black", lw=2, transform=ax.transAxes)
    ax.add_patch(box)

    ax.axis('off')
    plt.title(title)

    # Convert plot to URI like in previous examples
    uri = plot_to_uri(plt)
    return uri

@app.route('/')
def show_graphs():
    update_all_data()
    price_graphs = []
    vol_graphs = []
    info_graphs = []
    symbols = []
    for filename in os.listdir(os.path.join('data')):
        if filename.endswith(".csv") and filename != "tickers.csv":
            symbols.append(filename[:-4])
    for symbol in symbols:
        print(f"Getting data for {symbol}")
        main_df = pd.read_csv(os.path.join('data',f"{symbol}.csv"))
        main_df['time'] = pd.to_datetime(main_df['time'])
        #set time as index
        #main_df = main_df.set_index('time')
        #only keep time and close columns
        price_df = main_df[['time','close']]
        vol_df = main_df[['time','volume']]
        #set time as index
        price_df = price_df.set_index('time')
        vol_df = vol_df.set_index('time')
        #only keep first n rows
        n = 24*60
        price_df = price_df.iloc[:n]
        vol_df = vol_df.iloc[:n]
        plt.figure()
        price_df.plot()  # Customize your plot here (e.g., df['column'].plot())
        plt.title(symbol)
        uri = plot_to_uri(plt)
        price_graphs.append(uri)
        plt.figure()
        vol_df.plot()  # Customize your plot here (e.g., df['column'].plot())
        plt.title(symbol)
        uri = plot_to_uri(plt)
        vol_graphs.append(uri)
        #create infographic
        info_graphs.append(create_infographic(price_df['close'], symbol))
    graphs = list(zip(price_graphs, vol_graphs,info_graphs))
    return render_template('graphs.html', graphs=graphs)

if __name__ == '__main__':
    app.run(debug=True)
