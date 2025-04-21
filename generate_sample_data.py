# generate_sample_data.py
# Run this script to generate sample data for testing

import pandas as pd
import numpy as np
import os

def generate_sample_electricity_data():
    """Generate sample electricity consumption data"""
    # Create date range for a year
    dates = pd.date_range(start='2021-01-01', end='2021-12-31', freq='D')
    
    # Base consumption with some randomness
    base_consumption = 30 + np.random.normal(0, 5, len(dates))
    
    # Add seasonal pattern (higher in summer/winter)
    seasonal_effect = 15 * np.sin((np.arange(len(dates)) + 180) / 365 * 2 * np.pi)
    
    # Add weekly pattern (higher on weekends)
    weekly_pattern = np.array([0, 0, 0, 0, 2, 5, 5] * (len(dates) // 7 + 1))[:len(dates)]
    
    # Add random spikes
    random_spikes = np.zeros(len(dates))
    spike_days = np.random.choice(len(dates), size=15, replace=False)
    random_spikes[spike_days] = np.random.uniform(10, 25, len(spike_days))
    
    # Combine patterns
    total_consumption = base_consumption + seasonal_effect + weekly_pattern + random_spikes
    
    # Ensure all values are positive
    total_consumption = np.maximum(total_consumption, 5)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Total_Consumption': total_consumption
    })
    
    return df

def generate_sample_appliance_consumption():
    """Generate sample appliance consumption data"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Base values for each appliance
    fridge_base = 15
    kitchen_base = 25
    ac_base = 0  # Will vary significantly by season
    washing_base = 10
    other_base = 20
    
    # Seasonal patterns
    # AC usage peaks in summer
    ac_pattern = [5, 8, 12, 20, 35, 45, 50, 45, 25, 15, 8, 5]
    # Fridge uses more energy in summer
    fridge_pattern = [12, 12, 13, 14, 16, 18, 18, 17, 16, 14, 13, 12]
    # Other appliances fairly consistent
    kitchen_pattern = [23, 24, 24, 25, 26, 28, 28, 27, 26, 25, 24, 23]
    washing_pattern = [9, 9, 10, 10, 11, 12, 12, 12, 11, 10, 9, 9]
    other_pattern = [19, 19, 20, 20, 21, 22, 22, 22, 21, 20, 19, 19]
    
    # Add some randomness
    fridge = [val + np.random.normal(0, 1) for val in fridge_pattern]
    kitchen = [val + np.random.normal(0, 2) for val in kitchen_pattern]
    ac = [val + np.random.normal(0, 5) for val in ac_pattern]
    washing = [val + np.random.normal(0, 1) for val in washing_pattern]
    other = [val + np.random.normal(0, 2) for val in other_pattern]
    
    # Ensure all values are positive
    fridge = [max(10, val) for val in fridge]
    kitchen = [max(15, val) for val in kitchen]
    ac = [max(0, val) for val in ac]
    washing = [max(5, val) for val in washing]
    other = [max(10, val) for val in other]
    
    # Create DataFrame
    df = pd.DataFrame({
        'month': months,
        'year': 2021,
        'Fridge': fridge,
        'Kitchen Appliances': kitchen,
        'AC': ac,
        'Washing Machine': washing,
        'Other Appliances': other
    })
    
    return df

def generate_sample_forecast():
    """Generate sample forecast data with actual and predicted consumption"""
    # Get electricity data as base
    electricity_df = generate_sample_electricity_data()
    
    # Create predicted values with some error
    electricity_df['Predicted_Consumption'] = electricity_df['Total_Consumption'] + np.random.normal(0, 5, len(electricity_df))
    
    # Ensure predicted values are positive
    electricity_df['Predicted_Consumption'] = np.maximum(electricity_df['Predicted_Consumption'], 5)
    
    # Calculate error metrics
    electricity_df['MAE'] = abs(electricity_df['Total_Consumption'] - electricity_df['Predicted_Consumption'])
    
    # Intentionally add some anomalies
    anomaly_days = np.random.choice(len(electricity_df), size=20, replace=False)
    electricity_df.loc[anomaly_days, 'Total_Consumption'] += np.random.uniform(15, 30, len(anomaly_days))
    electricity_df.loc[anomaly_days, 'MAE'] = abs(electricity_df.loc[anomaly_days, 'Total_Consumption'] - 
                                              electricity_df.loc[anomaly_days, 'Predicted_Consumption'])
    
    return electricity_df

def generate_appliance_wise_data():
    """Generate sample daily appliance-wise consumption data"""
    # Create date range for a year
    dates = pd.date_range(start='2021-01-01', end='2021-12-31', freq='D')
    
    # Create patterns for each appliance
    day_of_year = np.arange(len(dates))
    
    # Fridge - fairly consistent with slight seasonal variation
    fridge_base = 0.4 + 0.1 * np.sin(day_of_year / 365 * 2 * np.pi)
    fridge = fridge_base + np.random.normal(0, 0.03, len(dates))
    
    # AC - strong seasonal pattern
    ac_seasonal = 0.8 * np.sin((day_of_year - 180) / 365 * 2 * np.pi)
    ac_seasonal = np.maximum(ac_seasonal, 0)  # No negative values
    ac = ac_seasonal + np.random.normal(0, 0.1, len(dates))
    ac = np.maximum(ac, 0)  # Ensure no negative values
    
    # Kitchen appliances - weekend pattern
    kitchen_base = 0.6 + np.zeros(len(dates))
    weekend_mask = (pd.Series(dates).dt.dayofweek >= 5).values
    kitchen_base[weekend_mask] += 0.2  # More cooking on weekends
    kitchen = kitchen_base + np.random.normal(0, 0.08, len(dates))
    
    # Washing machine - mainly used on specific days
    washing_base = np.zeros(len(dates))
    washing_days = (pd.Series(dates).dt.dayofweek == 6) | (pd.Series(dates).dt.dayofweek == 2)  # Sunday and Wednesday
    washing_base[washing_days] = 0.4
    washing = washing_base + np.random.normal(0, 0.05, len(dates))
    washing = np.maximum(washing, 0)
    
    # Other appliances - fairly consistent
    other_base = 0.5 + np.zeros(len(dates))
    other = other_base + np.random.normal(0, 0.07, len(dates))
    
    # Add some anomalies to simulate faulty devices
    # Fridge malfunction
    fridge_anomaly_days = np.random.choice(len(dates), size=5, replace=False)
    fridge[fridge_anomaly_days] *= np.random.uniform(1.5, 2.5, len(fridge_anomaly_days))
    
    # AC malfunction
    ac_anomaly_days = np.random.choice(len(dates), size=8, replace=False)
    ac[ac_anomaly_days] *= np.random.uniform(1.8, 3.0, len(ac_anomaly_days))
    
    # Kitchen spike
    kitchen_anomaly_days = np.random.choice(len(dates), size=6, replace=False)
    kitchen[kitchen_anomaly_days] *= np.random.uniform(1.5, 2.2, len(kitchen_anomaly_days))
    
    # Washing machine issues
    washing_anomaly_days = np.random.choice(len(dates), size=4, replace=False)
    washing[washing_anomaly_days] *= np.random.uniform(2.0, 3.0, len(washing_anomaly_days))
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Fridge': fridge,
        'AC': ac,
        'Kitchen Appliances': kitchen,
        'Washing Machine': washing,
        'Other Appliances': other
    })
    
    return df

def main():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate and save sample data
    print("Generating sample data...")
    
    # Electricity consumption data
    electricity_df = generate_sample_electricity_data()
    electricity_df.to_csv('data/electricity_data_sample.csv', index=False)
    print("- Electricity data saved")
    
    # Appliance consumption data
    appliance_df = generate_sample_appliance_consumption()
    appliance_df.to_csv('data/electrical_appliance_consumption_sample.csv', index=False)
    print("- Appliance consumption data saved")
    
    # Forecast data
    forecast_df = generate_sample_forecast()
    forecast_df.to_csv('data/electrical_forecast_sample.csv', index=False)
    print("- Forecast data saved")
    
    # Appliance-wise data
    appliance_wise_df = generate_appliance_wise_data()
    appliance_wise_df.to_csv('data/electricity_appliance_wise_data_sample.csv', index=False)
    print("- Appliance-wise data saved")
    
    print("Sample data generation complete!")

if __name__ == "__main__":
    main()