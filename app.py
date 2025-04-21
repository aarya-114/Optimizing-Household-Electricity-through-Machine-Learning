# app.py
from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
import os
import io

app = Flask(__name__)

# Load data function
def load_data():
    # Create a data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Path to your data files - update these paths to where your data is stored
    base_path = 'data'
    
    # Load the datasets
    df = pd.read_csv(os.path.join(base_path, 'Optimizing-Household-Electricity-through-Machine-Learning/Datasets/electricity_data.csv'))
    df = df[1110:]
    df.reset_index(drop=True, inplace=True)
    df.index = pd.to_datetime(df['Date'])
    
    df2 = pd.read_csv(os.path.join(base_path, 'Optimizing-Household-Electricity-through-Machine-Learning/Datasets/electrical_appliance_consumption.csv'))
    df2 = df2[df2['year'] == 2021]
    df2.reset_index(drop=True, inplace=True)
    
    df3 = pd.read_csv(os.path.join(base_path, 'Optimizing-Household-Electricity-through-Machine-Learning/Datasets/electrical_forecast.csv'))
    
    df4 = pd.read_csv(os.path.join(base_path, 'Optimizing-Household-Electricity-through-Machine-Learning/Datasets/electricity_appliance_wise_data.csv'))
    df4['Date'] = pd.to_datetime(df4['Date'])
    df4 = df4[df4['Date'].dt.year == 2021]
    df4.reset_index(drop=True, inplace=True)
    
    return df, df2, df3, df4

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/time_series')
def time_series():
    df, _, _, _ = load_data()
    
    # Create time series plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['Total_Consumption'],
        mode='lines',
        name='Electricity Consumption',
        line_color="#19E2C5"
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin={'b': 15},
        autosize=True,
        yaxis_title="Consumption (kWh)",
        xaxis_title="Date",
        title={'text': 'Time-Series Plot of Electricity Consumption', 'font': {'color': 'white'}, 'x': 0.5}
    )
    
    # Convert the plot to JSON for the frontend
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('time_series.html', plot_json=plot_json)

@app.route('/appliance_consumption')
def appliance_consumption():
    _, df2, _, _ = load_data()
    
    # Create list of months for dropdown
    months = df2['month'].unique().tolist()
    
    # Create default plot for first month
    first_month = months[0]
    month_data = df2[df2['month'] == first_month]
    
    # Get the data for the pie chart
    labels = ['Fridge', 'Kitchen Appliances', 'AC', 'Washing Machine', 'Other Appliances']
    values = [
        month_data['Fridge'].values[0],
        month_data['Kitchen Appliances'].values[0],
        month_data['AC'].values[0],
        month_data['Washing Machine'].values[0],
        month_data['Other Appliances'].values[0]
    ]
    
    # Create the pie chart
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        marker_colors=['rgb(33, 75, 99)', 'rgb(79, 129, 102)', 'rgb(151, 179, 100)', 
                      'rgb(175, 49, 35)', 'rgb(36, 73, 147)'],
        hole=0.3
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        title_font_color="#90E219",
        font_color="#90E219",
        title={'text': f'{first_month} Consumption Distribution (%) by each Appliance', 'font': {'color': 'white'}, 'x': 0.5}
    )
    
    # Convert the plot to JSON for the frontend
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('appliance_consumption.html', plot_json=plot_json, months=months)

@app.route('/get_appliance_data/<month>')
def get_appliance_data(month):
    _, df2, _, _ = load_data()
    
    # Filter data for the selected month
    month_data = df2[df2['month'] == month]
    
    # Get the data for the pie chart
    labels = ['Fridge', 'Kitchen Appliances', 'AC', 'Washing Machine', 'Other Appliances']
    values = [
        month_data['Fridge'].values[0],
        month_data['Kitchen Appliances'].values[0],
        month_data['AC'].values[0],
        month_data['Washing Machine'].values[0],
        month_data['Other Appliances'].values[0]
    ]
    
    # Create the pie chart
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        marker_colors=['rgb(33, 75, 99)', 'rgb(79, 129, 102)', 'rgb(151, 179, 100)', 
                      'rgb(175, 49, 35)', 'rgb(36, 73, 147)'],
        hole=0.3
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        title_font_color="#90E219",
        font_color="#90E219",
        title={'text': f'{month} Consumption Distribution (%) by each Appliance', 'font': {'color': 'white'}, 'x': 0.5}
    )
    
    # Convert the plot to JSON for the frontend
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return jsonify({'plot_json': plot_json})

@app.route('/forecast')
def forecast():
    _, _, df3, _ = load_data()
    
    # Create forecast plot
    df_sub = df3
    df_anoms = df_sub[df_sub['MAE'] >= 15]
    df_anoms.reset_index(drop=True, inplace=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sub['Date'], 
        y=df_sub['Total_Consumption'],
        mode='lines',
        name='Actual Consumption',
        line_color="#19E2C5"
    ))
    
    fig.add_trace(go.Scatter(
        x=df_sub['Date'], 
        y=df_sub['Predicted_Consumption'],
        mode='lines',
        name='Predicted Consumption',
        line_color="#C6810B"
    ))
    
    fig.add_trace(go.Scatter(
        x=df_anoms['Date'], 
        y=df_anoms['Total_Consumption'],
        mode='markers',
        name='Excess Consumption',
        marker=dict(size=5, line=dict(width=5, color='#C60B0B'))
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin={'b': 15},
        autosize=True,
        yaxis_title="Consumption (kWh)",
        xaxis_title="Date",
        title={'text': 'Forecasting Electricity Consumption', 'font': {'color': 'white'}, 'x': 0.5}
    )
    
    # Convert the plot to JSON for the frontend
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('forecast.html', plot_json=plot_json)

@app.route('/faulty_devices')
def faulty_devices():
    _, _, _, df4 = load_data()
    
    # Process data for anomaly detection
    def zscore(x, window):
        r = x.rolling(window=window)
        m = r.mean().shift(1)
        s = r.std(ddof=0).shift(1)
        z = (x-m)/s
        return z
    
    df_sub = df4
    df_sub['kap_zscore'] = zscore(df_sub['Kitchen Appliances'], 30)
    df_sub['fridge_zscore'] = zscore(df_sub['Fridge'], 30)
    df_sub['ac_zscore'] = zscore(df_sub['AC'], 30)
    df_sub['oap_zscore'] = zscore(df_sub['Other Appliances'], 30)
    df_sub['wm_zscore'] = zscore(df_sub['Washing Machine'], 3)

    df_sub.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_sub.fillna(0, inplace=True)

    # Identify anomalies
    df_anom_fridge = df_sub[df_sub['fridge_zscore'] > 5]
    
    # Create plot for fridge anomalies
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sub['Date'], 
        y=df_sub['Fridge'],
        mode='lines',
        name='Actual Consumption',
        line_color="#19E2C5"
    ))
    
    fig.add_trace(go.Scatter(
        x=df_anom_fridge['Date'], 
        y=df_anom_fridge['Fridge'],
        mode='markers',
        name='Fluctuations in Power Consumption',
        marker=dict(size=10, color='#C60B0B')
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin={'b': 15},
        autosize=True,
        yaxis_title="Consumption (kWh)",
        xaxis_title="Date",
        title={'text': 'Anomalies in power consumption of Fridge', 'font': {'color': 'white'}, 'x': 0.5}
    )
    
    # Convert the plot to JSON for the frontend
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # List of available appliances
    appliances = ['Fridge', 'AC', 'Kitchen Appliances', 'Washing Machine', 'Other Appliances']
    
    return render_template('faulty_devices.html', plot_json=plot_json, appliances=appliances)

@app.route('/get_faulty_device_data/<appliance>')
def get_faulty_device_data(appliance):
    _, _, _, df4 = load_data()
    
    # Process data for anomaly detection
    def zscore(x, window):
        r = x.rolling(window=window)
        m = r.mean().shift(1)
        s = r.std(ddof=0).shift(1)
        z = (x-m)/s
        return z
    
    df_sub = df4
    df_sub['kap_zscore'] = zscore(df_sub['Kitchen Appliances'], 30)
    df_sub['fridge_zscore'] = zscore(df_sub['Fridge'], 30)
    df_sub['ac_zscore'] = zscore(df_sub['AC'], 30)
    df_sub['oap_zscore'] = zscore(df_sub['Other Appliances'], 30)
    df_sub['wm_zscore'] = zscore(df_sub['Washing Machine'], 3)

    df_sub.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_sub.fillna(0, inplace=True)

    # Map appliance to its corresponding zscore column
    zscore_map = {
        'Fridge': 'fridge_zscore',
        'AC': 'ac_zscore',
        'Kitchen Appliances': 'kap_zscore',
        'Washing Machine': 'wm_zscore',
        'Other Appliances': 'oap_zscore'
    }
    
    # Identify anomalies for the selected appliance
    df_anom = df_sub[df_sub[zscore_map[appliance]] > 5]
    
    # Create plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sub['Date'], 
        y=df_sub[appliance],
        mode='lines',
        name='Actual Consumption',
        line_color="#19E2C5"
    ))
    
    fig.add_trace(go.Scatter(
        x=df_anom['Date'], 
        y=df_anom[appliance],
        mode='markers',
        name='Fluctuations in Power Consumption',
        marker=dict(size=10, color='#C60B0B')
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin={'b': 15},
        autosize=True,
        yaxis_title="Consumption (kWh)",
        xaxis_title="Date",
        title={'text': f'Anomalies in power consumption of {appliance}', 'font': {'color': 'white'}, 'x': 0.5}
    )
    
    # Convert the plot to JSON for the frontend
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return jsonify({'plot_json': plot_json})

@app.route('/download/<data_type>')
def download_data(data_type):
    df, df2, df3, df4 = load_data()
    
    output = io.BytesIO()
    
    if data_type == 'time_series':
        df.to_csv(output)
        filename = 'electricity_consumption_data.csv'
    elif data_type == 'appliance_consumption':
        df2.to_csv(output)
        filename = 'appliance_consumption_data.csv'
    elif data_type == 'forecast':
        df3.to_csv(output)
        filename = 'electricity_forecast_data.csv'
    elif data_type == 'faulty_devices':
        df4.to_csv(output)
        filename = 'appliance_wise_data.csv'
    else:
        return "Invalid data type", 400
    
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv'
    )

if __name__ == '__main__':
    app.run(debug=True)