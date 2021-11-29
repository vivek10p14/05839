from re import S
from _plotly_utils.colors import colorscale_to_scale
from plotly import colors
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import plotly.figure_factory as ff
from streamlit.elements import plotly_chart
from streamlit_metrics import metric, metric_row
import numpy as np
import os
import matplotlib.colors as colors
import random

@st.cache
def load_data():
    race_df = pd.read_csv('https://raw.githubusercontent.com/vivek10p14/05839/master/final_project/archive/races.csv')
    race_df = race_df.astype({'year':'str'})
    laps = pd.read_csv('https://raw.githubusercontent.com/vivek10p14/05839/master/final_project/archive/lap_times.csv')
    driver_name = pd.read_csv('https://raw.githubusercontent.com/vivek10p14/05839/master/final_project/archive/drivers.csv')

    return race_df, laps, driver_name

def init():
    st.set_page_config(layout="wide")
    if 'race_year' not in st.session_state:
        st.session_state['race_year'] = "1950"

    if 'race' not in st.session_state:
        st.session_state['race'] = "Belgian Grand Prix"

init()
# print("check point")
# st.write(st.session_state)

race_df, laps, driver_name = load_data()

# race_df = pd.read_csv('archive/races.csv')

race_list = []

try:
    race_list = race_df[race_df.year == st.session_state['race_year']]['name'].unique().tolist()
except:
    race_list = race_df[race_df.year == "1950"]['name'].unique().tolist()

if len(race_list)>1:
    race_list.sort()

def handle_change_race_year():
    if st.session_state.race_year:
        st.session_state.race_year = st.session_state.race_year
        update_race_first()

def handle_change_race():
    if st.session_state.race:
        st.session_state.race = st.session_state.race

def update_race_first():
    if st.session_state.race:
        st.session_state.race = race_df[race_df.year == st.session_state['race_year']]['name'].unique().tolist()[0]

try:
    row1_col1, dum2 = st.columns([5, 5])
    # row1_col1 = st.container()

    row1_col1.selectbox("Select Year", race_df['year'].sort_values().unique().tolist(), on_change=handle_change_race_year, key='race_year')
    row1_col1.selectbox("Select Race", race_list, on_change=handle_change_race, key='race')

    race_id = race_df[(race_df.year==st.session_state['race_year']) & (race_df.name==st.session_state['race'])]['raceId'].tolist()[0]

    #gen race data
    # laps = pd.read_csv('archive/lap_times.csv')
    laps = laps[laps['raceId'] == race_id]
    # driver_name = pd.read_csv('archive/drivers.csv')
    driver_dict = {}
    for index, row in driver_name.iterrows():
        driver_dict[row['driverId']] = row['forename'] + ' ' + row['surname']

    total_laps = len(laps)

    # col1, col2 = st.columns(2)
    # d1, col1, d2 = st.columns([1,6,1])
    col1, d1 = st.columns([5, 5])
    col2, d2 = st.columns([5, 5])

    if total_laps <= 400:
        col1.write('Not enough Data available select another race')

    else:
        df = laps
        driver_list = df['driverId'].unique().tolist()
        driver_df = []
        colors_list = list(colors._colors_full_map.values())
        for driver in driver_list:
            temp = df[df['driverId']==driver]
            temp = temp.sort_values('lap')
        #     print(temp.columns)
            temp = temp[['driverId', 'lap', 'position']]
            driver_df.append(temp)

        traces = []
        for i in range(len(driver_df)):
            temp_df = driver_df[i]
            t = go.Scatter(x=temp_df['lap'][:1], 
                            y=temp_df['position'][:2], mode='lines+markers',
                            line=dict(width=1.5), name=driver_dict[driver_list[i]])
            traces.append(t)

        frames = []
        dtrace = [i for i in range(len(traces))]
        num_laps = df['lap'].max()
        for laps in range(1, num_laps):
            data = []
            for i in range(len(driver_df)):
                temp_df = driver_df[i]
                d = dict(type='scatter', x=temp_df['lap'][:laps+1], y=temp_df['position'][:laps+1])
                data.append(d)
            frames.append(dict(data = data, traces = dtrace))

        layout = go.Layout(
                    updatemenus=[dict(
                    type='buttons', showactive=False, y=0.15, x=1.15,
                        xanchor='right', yanchor='bottom',
                        buttons=[dict(label='Play', method='animate', args=[
                            None, dict(frame=dict(duration=200, redraw=False),
                                        transition=dict(duration=0), fromcurrent=True, mode='immediate')
                        ])]
                    )])
        layout.update(xaxis =dict(range=[0, num_laps+1], autorange=False),
                yaxis =dict(range=[0, len(driver_list)+1], autorange=False), height=800, width=1000, colorway=random.sample(colors_list,  len(driver_list)))
        fig = go.Figure(data=traces, frames=frames, layout=layout)
        fig.update_yaxes(autorange="reversed")
        col1.plotly_chart(fig)
        race_results = pd.read_csv('https://raw.githubusercontent.com/vivek10p14/05839/master/final_project/archive/enriched_results.csv')
        race_results = race_results[race_results['raceId'] == race_id]
        race_results = race_results.drop('raceId', axis=1)
        race_results = race_results.replace('\\N', 'N.A.')
        race_results['Standing'] = race_results['Standing'].replace('N.A.', '1000').astype({'Standing':'int'})
        race_results = race_results.sort_values('Standing')
        race_results= race_results.astype({'Standing':'str'})
        race_results['Standing'] = race_results['Standing'].replace('1000', 'N.A.')
        col1.dataframe(race_results.reset_index().drop('index', axis=1), height=800)
except:
    st.write("Unexpected Error Occured Please Refresh The Page")





