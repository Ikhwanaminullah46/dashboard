import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.header(':nauseated_face: Dicoding Collection Dashboard :nauseated_face:')

viz = pd.read_csv("Dashboard/viz.csv")
viz['date'] = pd.to_datetime(viz['date'])

min_date = viz["date"].min()
max_date = viz["date"].max()

 
with st.sidebar:
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
monthly_AQI = viz[(viz["date"] >= str(start_date)) & 
                 (viz["date"] <= str(end_date))]


monthly_AQI['month'] = monthly_AQI.date.dt.month
monthly_AQI['year'] = monthly_AQI.date.dt.year
monthly_AQI = monthly_AQI.groupby(['year', 'month']).mean(numeric_only = True).reset_index()

st.subheader('Monthly AQI')

col1, col2 = st.columns(2)

with col1:
    avg_aqi = viz.AQI.mean(numeric_only=True)
    st.metric("Avg. AQI", value= round(avg_aqi))
 

average_values = monthly_AQI.groupby('month')['AQI'].mean(numeric_only=True)
max_month = average_values.idxmax()

def number_to_month(max_month):
    month_mapping = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    return month_mapping.get(max_month, 'Invalid Month')

with col2:
    st.metric("Worst Avg. Month", value = number_to_month(max_month))

fig = plt.figure(figsize=(16, 4)) 
sns.lineplot(data = monthly_AQI, x = 'month', y = 'AQI', hue = 'year', palette = 'bright')
plt.ylim(0, 250)

st.pyplot(fig)

station_AQI = viz[(viz["date"] >= str(start_date)) & 
                 (viz["date"] <= str(end_date))]

station_AQI = station_AQI[['date', 'AQI', 'station']]
station_AQI = station_AQI.groupby('station')[['station', 'AQI']].mean(numeric_only=True).reset_index()

st.subheader('Highest Polluted Station')

fig = plt.figure(figsize=(16,4)) 
sns.barplot(y = station_AQI.sort_values(by = 'AQI', ascending = True)['AQI'],
            x = station_AQI.sort_values(by = 'AQI', ascending = True)['station'],
            palette = 'flare')
plt.xticks(rotation= 90)

st.pyplot(fig)


st.subheader('Pollution Source')

wind = pd.concat([
    pd.read_csv("Dashboard/PM10_AQI.csv"),
    pd.read_csv("Dashboard/PM2.5_AQI.csv"),
    pd.read_csv("Dashboard/SO2_AQI.csv"),
    pd.read_csv("Dashboard/NO2_AQI.csv"),
    pd.read_csv("Dashboard/CO_AQI.csv"),
    pd.read_csv("Dashboard/O3_AQI.csv")], axis = 0)

wind['date'] = pd.to_datetime(wind['date'])

wind = wind[(wind["date"] >= str(start_date)) & 
                 (wind["date"] <= str(end_date))]

wind = wind.groupby('wd').mean(numeric_only=True).reset_index()

def compass_to_degrees(direction):
    compass_directions = ['E', 'ENE', 'NE', 'NNE',
                          'N', 'NNW', 'NW', 'WNW',
                          'W', 'WSW', 'SW', 'SSW',
                          'S', 'SSE', 'SE', 'ESE'
                         ]
    degrees_per_direction = 360 / len(compass_directions)
    
    return compass_directions.index(direction)*degrees_per_direction

wind["wd_degrees"] = wind["wd"].apply(lambda x: compass_to_degrees(x))

def plot_radar_chart(ax, categories, values, title="Radar Chart"):
    num_vars = len(categories)

    # Make sure the data wraps around the circular plot
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    # Plot the radar chart
    ax.fill(angles, values, alpha=0.25, label=title)

    # Label each axis
    ax.set_thetagrids(np.degrees(angles[:-1]), categories)

# Example data for multiple radar charts
wind_directions = ['E', 'ENE', 'NE', 'NNE',
                   'N', 'NNW', 'NW', 'WNW',
                   'W', 'WSW', 'SW', 'SSW',
                   'S', 'SSE', 'SE', 'ESE'
                  ]
air_quality = {
    'PM10': [wind[wind['wd'] == i]['PM10_AQI'].values[0] for i in wind_directions],
    'PM2.5':[wind[wind['wd'] == i]['PM2.5_AQI'].values[0] for i in wind_directions],
    'SO2':[wind[wind['wd'] == i]['SO2_AQI'].values[0] for i in wind_directions],
    'NO2':[wind[wind['wd'] == i]['NO2_AQI'].values[0] for i in wind_directions],
    'CO':[wind[wind['wd'] == i]['CO_AQI'].values[0] for i in wind_directions],
    'O3':[wind[wind['wd'] == i]['O3_AQI'].values[0] for i in wind_directions]
}

# Create a single subplot
fig, ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(8, 8))

# Plot radar charts for each dataset on the same axes
for title, values in air_quality.items():
    plot_radar_chart(ax, wind_directions, values, title=title)

# Set the title and legend
ax.legend(loc='upper left')

st.pyplot(fig)
