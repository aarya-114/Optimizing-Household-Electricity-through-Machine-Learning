# Directory structure:
# electricity_dashboard/
# ├── app.py
# ├── assets/
# │   ├── styles.css
# │   └── script.js
# ├── data/
# │   └── placeholder.txt
# ├── utils/
# │   └── data_processor.py
# └── requirements.txt

# app.py
import os
import base64
import io
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import plotly.express as px

# Create required directories
os.makedirs('data', exist_ok=True)
os.makedirs('assets', exist_ok=True)
os.makedirs('utils', exist_ok=True)

# Initialize the Dash app
app = dash.Dash(__name__, 
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
app.title = 'Electra.AI'
server = app.server

# Visualization options
viz_options = [
    {'label': 'Time-Series Plot', 'value': 'Time-Series Plot'},
    {'label': 'Appliance-wise Consumption', 'value': 'Appliance-wise Consumption'},
    {'label': 'Electricity Consumption Forecast', 'value': 'Electricity Consumption Forecast'},
    {'label': 'Faulty Devices', 'value': 'Faulty Devices'}
]

# App layout
app.layout = html.Div([
    # Theme toggle switch
    html.Div([
        html.Label('Theme Mode:'),
        dcc.RadioItems(
            id='theme-toggle',
            options=[
                {'label': ' Light', 'value': 'light'},
                {'label': ' Dark', 'value': 'dark'},
            ],
            value='dark',
            inline=True,
            className='theme-toggle'
        ),
    ], className='theme-container'),
    
    # Header
    html.Div([
        html.H1('Electra.AI Dashboard', className='dashboard-title'),
        html.P('Optimize Your Household Electricity with Machine Learning', className='dashboard-subtitle')
    ], className='header'),
    
    # Main content container
    html.Div([
        # Left sidebar
        html.Div([
            # File Upload
            html.Div([
                html.H3('Upload Data Files', className='section-title'),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px 0'
                    },
                    multiple=True
                ),
                html.Div(id='upload-status'),
                html.Div(id='file-list', className='file-list')
            ], className='upload-container'),
            
            # Visualization Controls
            html.Div([
                html.H3('Visualization Controls', className='section-title'),
                html.Label('Select Visualization:'),
                dcc.Dropdown(
                    id='viz-selector',
                    options=viz_options,
                    value='Time-Series Plot',
                    clearable=False,
                    className='dropdown'
                ),
                html.Div(id='dynamic-controls', className='dynamic-controls'),
                html.Button('Generate Visualization', id='generate-btn', className='button')
            ], className='controls-container'),
            
            # Data Summary
            html.Div([
                html.H3('Data Summary', className='section-title'),
                html.Div(id='data-summary', className='summary-content')
            ], className='summary-container')
        ], className='sidebar'),
        
        # Main visualization area
        html.Div([
            html.Div(id='viz-title', className='viz-title'),
            dcc.Graph(id='main-graph', config={'displayModeBar': True, 'responsive': True}),
            html.Div(id='analysis-output', className='analysis-output')
        ], className='visualization-container')
    ], className='main-content'),
    
    # Footer
    html.Footer([
        html.P('© 2025 Electra.AI - Optimizing Household Electricity through Machine Learning')
    ], className='footer'),
    
    # Store uploaded data in hidden divs
    dcc.Store(id='electricity-data'),
    dcc.Store(id='appliance-data'),
    dcc.Store(id='forecast-data'),
    dcc.Store(id='appliance-wise-data'),
], id='main-container')

# Callback to handle uploaded files
@app.callback(
    [Output('upload-status', 'children'),
     Output('file-list', 'children'),
     Output('electricity-data', 'data'),
     Output('appliance-data', 'data'),
     Output('forecast-data', 'data'),
     Output('appliance-wise-data', 'data')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('electricity-data', 'data'),
     State('appliance-data', 'data'),
     State('forecast-data', 'data'),
     State('appliance-wise-data', 'data')]
)
def update_output(list_of_contents, list_of_names, electricity_data, appliance_data, forecast_data, appliance_wise_data):
    if list_of_contents is None:
        # On initial load, try to load any existing sample data
        try:
            sample_electricity = pd.read_csv('data/electricity_data_sample.csv').to_json(date_format='iso', orient='split')
            sample_appliance = pd.read_csv('data/electrical_appliance_consumption_sample.csv').to_json(date_format='iso', orient='split')
            sample_forecast = pd.read_csv('data/electrical_forecast_sample.csv').to_json(date_format='iso', orient='split')
            sample_appliance_wise = pd.read_csv('data/electricity_appliance_wise_data_sample.csv').to_json(date_format='iso', orient='split')
            
            return [
                html.Div('Sample data loaded successfully!', className='success-msg'),
                html.Ul([
                    html.Li('Sample: electricity_data.csv'),
                    html.Li('Sample: electrical_appliance_consumption.csv'),
                    html.Li('Sample: electrical_forecast.csv'),
                    html.Li('Sample: electricity_appliance_wise_data.csv')
                ]),
                sample_electricity,
                sample_appliance,
                sample_forecast,
                sample_appliance_wise
            ]
        except:
            return [
                html.Div('Please upload data files to begin analysis.'),
                None,
                electricity_data,
                appliance_data, 
                forecast_data,
                appliance_wise_data
            ]
    
    if list_of_contents is not None:
        file_list = []
        status = []
        
        for content, name in zip(list_of_contents, list_of_names):
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            
            try:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                
                # Save file to data directory
                save_path = os.path.join('data', name)
                df.to_csv(save_path, index=False)
                
                # Assign to appropriate data store
                if 'electricity_data' in name.lower():
                    electricity_data = df.to_json(date_format='iso', orient='split')
                    status.append(html.Div(f"Processed: {name}", className='success-msg'))
                elif 'appliance_consumption' in name.lower():
                    appliance_data = df.to_json(date_format='iso', orient='split')
                    status.append(html.Div(f"Processed: {name}", className='success-msg'))
                elif 'forecast' in name.lower():
                    forecast_data = df.to_json(date_format='iso', orient='split')
                    status.append(html.Div(f"Processed: {name}", className='success-msg'))
                elif 'appliance_wise' in name.lower():
                    appliance_wise_data = df.to_json(date_format='iso', orient='split')
                    status.append(html.Div(f"Processed: {name}", className='success-msg'))
                else:
                    status.append(html.Div(f"Note: {name} doesn't match any expected file pattern", className='warning-msg'))
                
                file_list.append(html.Li(f"{name} - {len(df)} rows"))
                
            except Exception as e:
                status.append(html.Div(f"Error processing {name}: {str(e)}", className='error-msg'))
        
        return [
            html.Div(status),
            html.Ul(file_list),
            electricity_data,
            appliance_data,
            forecast_data,
            appliance_wise_data
        ]
    
    return [
        html.Div('Please upload data files to begin analysis.'),
        None,
        electricity_data,
        appliance_data, 
        forecast_data,
        appliance_wise_data
    ]

# Callback to update data summary based on uploaded data
@app.callback(
    Output('data-summary', 'children'),
    [Input('electricity-data', 'data'),
     Input('appliance-data', 'data'),
     Input('forecast-data', 'data'),
     Input('appliance-wise-data', 'data')]
)
def update_data_summary(electricity_data, appliance_data, forecast_data, appliance_wise_data):
    summary = []
    
    if electricity_data:
        df = pd.read_json(electricity_data, orient='split')
        summary.append(html.Div([
            html.H4('Electricity Data:'),
            html.P(f"Rows: {len(df)}"),
            html.P(f"Date Range: {df['Date'].min()} to {df['Date'].max()}" if 'Date' in df.columns else ""),
            html.P(f"Average Consumption: {df['Total_Consumption'].mean():.2f} kWh" if 'Total_Consumption' in df.columns else "")
        ]))
    
    if appliance_data:
        df = pd.read_json(appliance_data, orient='split')
        summary.append(html.Div([
            html.H4('Appliance Data:'),
            html.P(f"Rows: {len(df)}"),
            html.P(f"Year: {df['year'].unique()[0]}" if 'year' in df.columns else ""),
            html.P(f"Months: {', '.join(df['month'].unique())}" if 'month' in df.columns else "")
        ]))
    
    if forecast_data:
        df = pd.read_json(forecast_data, orient='split')
        summary.append(html.Div([
            html.H4('Forecast Data:'),
            html.P(f"Rows: {len(df)}"),
            html.P(f"Average MAE: {df['MAE'].mean():.2f}" if 'MAE' in df.columns else "")
        ]))
    
    if appliance_wise_data:
        df = pd.read_json(appliance_wise_data, orient='split')
        summary.append(html.Div([
            html.H4('Appliance-wise Data:'),
            html.P(f"Rows: {len(df)}"),
            html.P(f"Appliances: {', '.join([col for col in df.columns if col not in ['Date']])}")
        ]))
        
    if not summary:
        return html.P("No data available. Please upload files to see summary.")
        
    return summary

# Callback to update theme
@app.callback(
    Output('main-container', 'className'),
    [Input('theme-toggle', 'value')]
)
def update_theme(selected_theme):
    return f"theme-{selected_theme}"

# Callback to update visualization title
@app.callback(
    Output('viz-title', 'children'),
    [Input('viz-selector', 'value')]
)
def update_viz_title(selected_viz):
    title_mapping = {
        'Time-Series Plot': 'Time-Series Analysis of Electricity Consumption',
        'Appliance-wise Consumption': 'Monthly Appliance-wise Consumption Distribution',
        'Electricity Consumption Forecast': 'Electricity Consumption Forecast and Anomaly Detection',
        'Faulty Devices': 'Faulty Device Detection and Power Fluctuations'
    }
    return html.H2(title_mapping.get(selected_viz, selected_viz))

# Callback for dynamic controls based on visualization type
@app.callback(
    Output('dynamic-controls', 'children'),
    [Input('viz-selector', 'value')]
)
def update_dynamic_controls(selected_viz):
    if selected_viz == 'Time-Series Plot':
        return html.Div([
            html.Label('Date Range:'),
            dcc.DatePickerRange(
                id='date-range',
                start_date_placeholder_text='Start Date',
                end_date_placeholder_text='End Date',
                className='date-picker'
            )
        ])
    
    elif selected_viz == 'Appliance-wise Consumption':
        return html.Div([
            html.Label('Select Month:'),
            dcc.Dropdown(
                id='month-selector',
                options=[
                    {'label': 'January', 'value': 'Jan'},
                    {'label': 'February', 'value': 'Feb'},
                    {'label': 'March', 'value': 'Mar'},
                    {'label': 'April', 'value': 'Apr'},
                    {'label': 'May', 'value': 'May'},
                    {'label': 'June', 'value': 'Jun'},
                    {'label': 'July', 'value': 'Jul'},
                    {'label': 'August', 'value': 'Aug'},
                    {'label': 'September', 'value': 'Sep'},
                    {'label': 'October', 'value': 'Oct'},
                    {'label': 'November', 'value': 'Nov'},
                    {'label': 'December', 'value': 'Dec'},
                ],
                value='Jan',
                clearable=False,
                className='dropdown'
            )
        ])
    
    elif selected_viz == 'Faulty Devices':
        return html.Div([
            html.Label('Select Appliance:'),
            dcc.Dropdown(
                id='appliance-selector',
                options=[
                    {'label': 'Fridge', 'value': 'Fridge'},
                    {'label': 'AC', 'value': 'AC'},
                    {'label': 'Kitchen Appliances', 'value': 'Kitchen Appliances'},
                    {'label': 'Washing Machine', 'value': 'Washing Machine'},
                    {'label': 'Other Appliances', 'value': 'Other Appliances'},
                ],
                value='Fridge',
                clearable=False,
                className='dropdown'
            ),
            html.Label('Z-Score Threshold:'),
            dcc.Slider(
                id='zscore-threshold',
                min=1,
                max=10,
                step=0.5,
                value=5,
                marks={i: str(i) for i in range(1, 11, 1)},
                className='slider'
            )
        ])
    
    elif selected_viz == 'Electricity Consumption Forecast':
        return html.Div([
            html.Label('MAE Threshold for Anomalies:'),
            dcc.Slider(
                id='mae-threshold',
                min=5,
                max=25,
                step=1,
                value=15,
                marks={i: str(i) for i in range(5, 26, 5)},
                className='slider'
            )
        ])
    
    return html.Div()

# Main visualization callback
@app.callback(
    [Output('main-graph', 'figure'),
     Output('analysis-output', 'children')],
    [Input('generate-btn', 'n_clicks')],
    [State('viz-selector', 'value'),
     State('electricity-data', 'data'),
     State('appliance-data', 'data'),
     State('forecast-data', 'data'),
     State('appliance-wise-data', 'data'),
     State('theme-toggle', 'value')]
)
def update_visualization(n_clicks, viz_type, electricity_data, appliance_data, forecast_data, appliance_wise_data, theme):
    if n_clicks is None:
        # Initial load - show placeholder
        fig = go.Figure()
        fig.add_annotation(
            text="Click 'Generate Visualization' to see data analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            template='plotly_dark' if theme == 'dark' else 'plotly_white',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0.05)' if theme == 'dark' else 'rgba(240, 240, 240, 0.7)',
        )
        return fig, html.Div("Select visualization type and generate to see analysis.")
    
    template = 'plotly_dark' if theme == 'dark' else 'plotly_white'
    bg_color = 'rgba(0, 0, 0, 0)' 
    plot_bg = 'rgba(0, 0, 0, 0.05)' if theme == 'dark' else 'rgba(240, 240, 240, 0.7)'
    font_color = 'white' if theme == 'dark' else 'black'
    analysis_output = html.Div()
    
    try:
        if viz_type == 'Time-Series Plot' and electricity_data:
            df = pd.read_json(electricity_data, orient='split')
            df.index = pd.to_datetime(df['Date'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Total_Consumption'],
                mode='lines',
                name='Electricity Consumption',
                line=dict(color="#19E2C5" if theme == 'dark' else "#007BFF", width=2)
            ))
            
            # Add a 7-day moving average
            df['MA_7'] = df['Total_Consumption'].rolling(window=7).mean()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MA_7'],
                mode='lines',
                name='7-Day Moving Average',
                line=dict(color="#E27619" if theme == 'dark' else "#FF6B35", width=2, dash='dash')
            ))
            
            fig.update_layout(
                title='Time-Series Analysis of Electricity Consumption',
                xaxis_title='Date',
                yaxis_title='Consumption (kWh)',
                template=template,
                paper_bgcolor=bg_color,
                plot_bgcolor=plot_bg,
                font=dict(color=font_color),
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            # Analysis output
            avg_consumption = df['Total_Consumption'].mean()
            max_consumption = df['Total_Consumption'].max()
            max_date = df.loc[df['Total_Consumption'] == max_consumption].index[0].strftime('%Y-%m-%d')
            
            analysis_output = html.Div([
                html.H3('Analysis Insights'),
                html.Ul([
                    html.Li(f"Average daily consumption: {avg_consumption:.2f} kWh"),
                    html.Li(f"Peak consumption: {max_consumption:.2f} kWh on {max_date}"),
                    html.Li(f"Data spans from {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
                ])
            ])
            
        elif viz_type == 'Appliance-wise Consumption' and appliance_data:
            df = pd.read_json(appliance_data, orient='split')
            df = df[df['year'] == 2021]  # Assuming 2021 data
            
            # Prepare data for pie charts
            month_data = {month: df[df['month'] == month] for month in df['month'].unique()}
            
            fig = go.Figure()
            for month, data in month_data.items():
                if len(data) > 0:
                    values = [
                        data['Fridge'].values[0],
                        data['Kitchen Appliances'].values[0],
                        data['AC'].values[0],
                        data['Washing Machine'].values[0],
                        data['Other Appliances'].values[0]
                    ]
                    
                    fig.add_trace(go.Pie(
                        labels=['Fridge', 'Kitchen Appliances', 'AC', 'Washing Machine', 'Other Appliances'],
                        values=values,
                        name=month,
                        visible=(month == 'Jan'),  # Make January visible by default
                        hole=0.3,
                        textinfo='percent+label',
                        marker=dict(
                            colors=['#003f5c', '#58508d', '#bc5090', '#ff6361', '#ffa600']
                        )
                    ))
            
            # Add dropdown for month selection
            buttons = []
            for i, month in enumerate(df['month'].unique()):
                visible = [False] * len(df['month'].unique())
                visible[i] = True
                buttons.append(dict(
                    method='update',
                    label=month,
                    args=[{'visible': visible}, {'title': f'{month} 2021: Appliance-wise Consumption Distribution'}]
                ))
            
            fig.update_layout(
                updatemenus=[dict(
                    active=0,
                    buttons=buttons,
                    direction='down',
                    pad={'r': 10, 't': 10},
                    showactive=True,
                    x=0.1,
                    xanchor='left',
                    y=1.1,
                    yanchor='top'
                )],
                title='January 2021: Appliance-wise Consumption Distribution',
                template=template,
                paper_bgcolor=bg_color,
                plot_bgcolor=plot_bg,
                font=dict(color=font_color)
            )
            
            # Analysis output
            ac_usage = df.groupby('month')['AC'].sum()
            highest_ac_month = ac_usage.idxmax()
            
            analysis_output = html.Div([
                html.H3('Analysis Insights'),
                html.Ul([
                    html.Li(f"Highest AC usage in {highest_ac_month}: {ac_usage[highest_ac_month]:.2f} kWh"),
                    html.Li(f"Average fridge consumption: {df['Fridge'].mean():.2f} kWh per month"),
                    html.Li("Switch between months using the dropdown menu to compare consumption patterns")
                ])
            ])
            
        elif viz_type == 'Electricity Consumption Forecast' and forecast_data:
            df = pd.read_json(forecast_data, orient='split')
            
            # Find anomalies (where MAE is high)
            mae_threshold = 15  # Default threshold
            df_anoms = df[df['MAE'] >= mae_threshold]
            
            fig = go.Figure()
            
            # Actual consumption
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Total_Consumption'],
                mode='lines',
                name='Actual Consumption',
                line=dict(color="#19E2C5" if theme == 'dark' else "#007BFF", width=2)
            ))
            
            # Predicted consumption
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Predicted_Consumption'],
                mode='lines',
                name='Predicted Consumption',
                line=dict(color="#C6810B" if theme == 'dark' else "#FF6B35", width=2)
            ))
            
            # Anomalies
            fig.add_trace(go.Scatter(
                x=df_anoms['Date'],
                y=df_anoms['Total_Consumption'],
                mode='markers',
                name='Excess Consumption',
                marker=dict(
                    size=10,
                    color='#C60B0B' if theme == 'dark' else '#FF0000',
                    line=dict(width=2, color='#C60B0B' if theme == 'dark' else '#FF0000')
                )
            ))
            
            fig.update_layout(
                title='Electricity Consumption Forecast and Anomaly Detection',
                xaxis_title='Date',
                yaxis_title='Consumption (kWh)',
                template=template,
                paper_bgcolor=bg_color,
                plot_bgcolor=plot_bg,
                font=dict(color=font_color),
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            # Analysis output
            avg_mae = df['MAE'].mean()
            anomaly_count = len(df_anoms)
            
            analysis_output = html.Div([
                html.H3('Analysis Insights'),
                html.Ul([
                    html.Li(f"Average Model Error (MAE): {avg_mae:.2f} kWh"),
                    html.Li(f"Number of anomalies detected: {anomaly_count}"),
                    html.Li(f"Percentage of days with excess consumption: {(anomaly_count/len(df)*100):.1f}%")
                ])
            ])
            
        elif viz_type == 'Faulty Devices' and appliance_wise_data:
            df = pd.read_json(appliance_wise_data, orient='split')
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Calculate z-scores for anomaly detection
            def zscore(x, window):
                r = x.rolling(window=window)
                m = r.mean().shift(1)
                s = r.std(ddof=0).shift(1)
                z = (x-m)/s
                return z
            
            appliances = ['Fridge', 'AC', 'Kitchen Appliances', 'Washing Machine', 'Other Appliances']
            zscore_threshold = 5  # Default threshold
            
            # Calculate z-scores for each appliance
            for app in appliances:
                df[f'{app}_zscore'] = zscore(df[app], 30)
            
            # Replace inf and NaN values
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df.fillna(0, inplace=True)
            
            # Create figure
            fig = go.Figure()
            
            # Add traces for each appliance
            for app in appliances:
                df_anom = df[df[f'{app}_zscore'] > zscore_threshold]
                
                # Make only first appliance visible by default
                is_visible = (app == 'Fridge')
                
                # Actual consumption
                fig.add_trace(go.Scatter(
                    x=df['Date'],
                    y=df[app],
                    mode='lines',
                    name=f'{app} Consumption',
                    line=dict(color="#19E2C5" if theme == 'dark' else "#007BFF"),
                    visible=is_visible
                ))
                
                # Anomalies
                fig.add_trace(go.Scatter(
                    x=df_anom['Date'],
                    y=df_anom[app],
                    mode='markers',
                    name=f'{app} Anomalies',
                    marker=dict(
                        size=10,
                        color='#C60B0B' if theme == 'dark' else '#FF0000'
                    ),
                    visible=is_visible
                ))
            
            # Create buttons for appliance selection
            buttons = []
            for i, app in enumerate(appliances):
                visible = [False] * (len(appliances) * 2)
                visible[i*2] = True  # Make the appliance consumption visible
                visible[i*2+1] = True  # Make the appliance anomalies visible
                
                buttons.append(dict(
                    method='update',
                    label=app,
                    args=[{'visible': visible}, {'title': f'Anomalies in power consumption of {app}'}]
                ))
            
            fig.update_layout(
                updatemenus=[dict(
                    active=0,
                    buttons=buttons,
                    direction='down',
                    pad={'r': 10, 't': 10},
                    showactive=True,
                    x=0.1,
                    xanchor='left',
                    y=1.1,
                    yanchor='top'
                )],
                title='Anomalies in power consumption of Fridge',
                xaxis_title='Date',
                yaxis_title='Consumption (kWh)',
                template=template,
                paper_bgcolor=bg_color,
                plot_bgcolor=plot_bg,
                font=dict(color=font_color)
            )
            
            # Analysis output
            analysis_results = []
            for app in appliances:
                anomalies = len(df[df[f'{app}_zscore'] > zscore_threshold])
                if anomalies > 0:
                    analysis_results.append(html.Li(f"{app}: {anomalies} potential issues detected"))
            
            analysis_output = html.Div([
                html.H3('Anomaly Detection Results'),
                html.P("Fluctuations in power consumption may indicate faulty devices or abnormal usage patterns."),
                html.Ul(analysis_results)
            ])
        
        else:
            # Fallback - show empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for the selected visualization. Please upload the required data files.",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            # Current code ends in the middle of update_layout for Faulty Devices visualization
        fig.update_layout(
            template=template,
            paper_bgcolor=bg_color,
            plot_bgcolor=plot_bg,
            font=dict(color=font_color)
        )
        
    except Exception as e:
        # If an error occurs, show error message
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error generating visualization: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color='red')
        )
        fig.update_layout(
            template=template,
            paper_bgcolor=bg_color,
            plot_bgcolor=plot_bg,
            font=dict(color=font_color)
        )
        analysis_output = html.Div(f"An error occurred: {str(e)}", className='error-msg')
    
    return fig, analysis_output

# Function to generate sample data for testing
def generate_sample_data():
    """Generate sample data files for the application."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Sample electricity data
        date_range = pd.date_range(start='2021-01-01', end='2021-12-31')
        electricity_df = pd.DataFrame({
            'Date': date_range,
            'Total_Consumption': np.random.normal(loc=25, scale=5, size=len(date_range))
        })
        electricity_df['Total_Consumption'] = electricity_df['Total_Consumption'] + \
                                             5 * np.sin(np.arange(len(date_range)) * 2 * np.pi / 30)  # Seasonal pattern
        electricity_df.to_csv('data/electricity_data_sample.csv', index=False)
        
        # Sample appliance consumption data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        appliance_df = pd.DataFrame({
            'month': months,
            'year': [2021] * 12,
            'Fridge': np.random.uniform(70, 90, 12),
            'AC': np.array([10, 15, 30, 50, 90, 120, 150, 140, 70, 30, 15, 10]),  # Seasonal pattern
            'Kitchen Appliances': np.random.uniform(40, 60, 12),
            'Washing Machine': np.random.uniform(30, 50, 12),
            'Other Appliances': np.random.uniform(20, 40, 12)
        })
        appliance_df.to_csv('data/electrical_appliance_consumption_sample.csv', index=False)
        
        # Sample forecast data
        forecast_df = pd.DataFrame({
            'Date': date_range,
            'Total_Consumption': electricity_df['Total_Consumption'],
            'Predicted_Consumption': electricity_df['Total_Consumption'] + np.random.normal(loc=0, scale=3, size=len(date_range)),
            'MAE': np.abs(np.random.normal(loc=5, scale=7, size=len(date_range)))
        })
        forecast_df.to_csv('data/electrical_forecast_sample.csv', index=False)
        
        # Sample appliance-wise data
        appliance_wise_df = pd.DataFrame({
            'Date': date_range
        })
        
        # Add appliance data with occasional spikes
        for appliance in ['Fridge', 'AC', 'Kitchen Appliances', 'Washing Machine', 'Other Appliances']:
            base_consumption = np.random.uniform(5, 20)
            consumption = np.random.normal(loc=base_consumption, scale=1, size=len(date_range))
            
            # Add some anomalies
            anomaly_indices = np.random.choice(range(len(date_range)), size=10, replace=False)
            consumption[anomaly_indices] = consumption[anomaly_indices] * np.random.uniform(2, 4, size=10)
            
            appliance_wise_df[appliance] = consumption
        
        appliance_wise_df.to_csv('data/electricity_appliance_wise_data_sample.csv', index=False)
        
        return True
    except Exception as e:
        print(f"Error generating sample data: {str(e)}")
        return False

# Generate sample data when the app starts
generate_sample_data()

# Run the server
if __name__ == '__main__':
    app.run(debug=True, port=8050)