from plotly import colors
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import plotly.figure_factory as ff
from streamlit_metrics import metric, metric_row


st.set_page_config(layout="wide")

st.sidebar.header('Filters')

user_type = st.sidebar.radio('Type of User', ['All', 'Subscriber', 'Casual'])
age = st.sidebar.slider('Max Age of Users', 0, 100, (0, 100), 1)
days_of_week = st.sidebar.multiselect('Days Of Week', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
sgmasters = st.sidebar.multiselect('Month Of Year', ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
gender = st.sidebar.radio('Type of User', ['All', 'Male', 'Female'])



# st.markdown(
#         f"""
# <style>
#     .reportview-container .main .block-container{{
#         max-width: 1000px;
#         padding-top: 10rem;
#         padding-right: 10rem;
#         padding-left: 10rem;
#         padding-bottom: 10rem;
#     }}
    
# </style>
# """,
#         unsafe_allow_html=True,
#     )


    # .reportview-container .main {{
    #      color: white;
    #      background-color: black;
    #  }}

st.write("""
# BLUE BIKES (Boston) Data Visualization
""")

with st.expander("View Data Details"):
    st.write("Under Dev")

df = pd.read_csv('enriched_boston.csv')
orig_df = df
station_df = pd.read_csv('station_index.csv')
station_df = station_df.drop([station_df.columns[0]], axis=1)

station_df = station_df[station_df.latitude != 0]
station_df = station_df[station_df.longitude != 0]

col1, col2, col3, col4, col5, col6, col7 = st.columns(7) # cols for displaying metrics


num_rides = len(df)
bikes_in_use = df['bikeid'].nunique()
avg_trip_duration = ((df['tripduration'].sum()/num_rides)/60).round(2)
gender1_trips = len(df[df.gender==1])
gender2_trips = len(df[df.gender==2])
subscribers_trips = len(df[df.usertype=="Subscriber"])
customer_trips = len(df[df.usertype=="Customer"])

col1.metric(label="Total Number of Rides", value="{0}".format(num_rides), delta="1.2 °F")
col2.metric(label="Number of Bikes in Use", value="{0}".format(bikes_in_use), delta="1.2 °F")
col3.metric(label="Average Ride Duration", value="{0}".format(avg_trip_duration), delta="1.2 °F")
col4.metric(label="Trips by Gender 1", value="{0}".format(gender1_trips), delta="1.2 °F")
col5.metric(label="Trips by Gender 2", value="{0}".format(gender2_trips), delta="1.2 °F")
col6.metric(label="Trips by Subscribers", value="{0}".format(subscribers_trips), delta="1.2 °F")
col7.metric(label="Trips by Customer", value="{0}".format(customer_trips), delta="1.2 °F")

# heat map to find busy areas
start_ride_distribution = df.groupby(['start_hour', 'start station id'], as_index=False)['usertype'].count().rename(columns = {'usertype':'count'})


start_ride_distribution = start_ride_distribution.merge(station_df, left_on='start station id', right_on='id', how='inner')

fig = px.density_mapbox(start_ride_distribution, lat='latitude', lon='longitude', z='count', radius=10, center=dict(lat=42.361001, lon=-71.084025), zoom=11, mapbox_style="stamen-terrain", hover_name='name', range_color=[0, 500], animation_frame='start_hour', animation_group='id', width=500, height=500)

start_ride_distribution = start_ride_distribution.sort_values(by='count', ascending=False)

station_use = df.groupby('start station id', as_index=False)['gender'].count().rename(columns={'start station id':'station_id', 'gender':'count'})
station_use = station_use.merge(station_df, left_on='station_id', right_on='id', how='inner')

fig_used_station = px.pie(station_use.head(10), values='count', names='name')
fig_used_station.update_traces(textinfo='percent+label', showlegend=False)

row1_col1, dummy, row1_col2 = st.columns([6, 6, 1]) # first row of page

row1_col1.plotly_chart(fig, use_container_width=True)
dummy.plotly_chart(fig_used_station, use_container_width=True)
row1_col2.slider("Time Range", 0, 23, (0, 23))
row1_col2.selectbox("Top N stations", [i for i in range (5, 21)])


row2_col1, row2_col2 = st.columns(2) #row 2

# count of trips taken by day of week
count_df = df.groupby(['month','start_day'], as_index=False)['usertype'].count().rename(columns = {'usertype':'count'})

day_dict = {'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4, 'Friday':5, 'Saturday':6, 'Sunday':7, 'All':8}

count_df['day_int'] = count_df['start_day'].apply(lambda x: day_dict[x])

count_df = count_df.sort_values(by=['month', 'day_int'])

fig = px.bar(count_df, x = 'start_day', y='count', color='start_day', animation_frame='month', animation_group='start_day', range_y=[0, 80000])

row2_col1.plotly_chart(fig)

# number of trips taken per day of week/hour of day
scatter_df = df.groupby(['month', 'start_hour', 'start_day'], as_index=False).count().rename(columns = {'usertype':'count'})

scatter_df['day_int'] = scatter_df['start_day'].apply(lambda x: day_dict[x])
scatter_df = scatter_df.sort_values(by=['month', 'day_int'])

fig2 = px.scatter(scatter_df, x='start_hour', y='start_day', color='start_day', size='count', animation_group='start_hour', animation_frame='month')

row2_col2.plotly_chart(fig2)


row3_col1, row3_col2 = st.columns(2)

# subscribers vs casual across months

user_df = df.groupby(['month', 'usertype'], as_index=False)['gender'].count().rename(columns={'gender':'Number of Trips'})

user_df = user_df.sort_values(['month'])

utype_fig = px.bar(user_df, x="month", y="Number of Trips", color="usertype", color_discrete_sequence=px.colors.qualitative.D3)

row3_col1.plotly_chart(utype_fig)

# subscriber demographic

age_df = df[['usertype', 'birth year']]
age_df['Age'] = ((2019-age_df['birth year'])//5)*5

age_df = age_df.groupby(['Age', 'usertype'], as_index=False)['birth year'].count().rename(columns={'birth year':'Count'})

age_user_fig = px.bar(age_df, x="Age", y="Count", color="usertype", color_discrete_sequence=px.colors.qualitative.D3)

row3_col2.plotly_chart(age_user_fig)


row4_col1, row4_col2 = st.columns(2)

# total time every bike isused for
usage_df = orig_df.groupby(['bikeid'], as_index=False)['tripduration'].agg('sum').rename(columns={'bikeid':'bikeid'})
usage_df['tripduration'] = usage_df['tripduration']/3600
usage_df = usage_df.groupby(['tripduration'], as_index=False)['bikeid'].agg('nunique').rename(columns={'bikeid':'Bikes', 'tripduration':'Trip Duration in Hours'})

usage_fig = px.histogram(usage_df, x="Trip Duration in Hours", y="Bikes", marginal="rug")

row4_col1.plotly_chart(usage_fig)


#new bikes added per month

bike_df = orig_df.groupby(['month'], as_index=False)['bikeid'].agg('nunique').rename(columns={'bikeid':'Number of Bikes Used'})
bike_fig = px.line(bike_df, x="month", y="Number of Bikes Used", text="Number of Bikes Used")

row4_col2.plotly_chart(bike_fig)


row5_col1, row5_col2 = st.columns(2)

# trip duration with hour of day

tripd_hour = df.groupby(['start_hour'], as_index=False)['tripduration'].agg('mean').rename(columns={'tripduration':'Avg Trip Time Mins', 'start_hour':'Hour of Day', 'start_day':'Day of Week'})

tripd_hour['Avg Trip Time Mins'] = tripd_hour['Avg Trip Time Mins']/60

tripd_fig = px.bar(tripd_hour, x="Hour of Day", y="Avg Trip Time Mins")

tripd_fig.update_traces(marker_color='rgb(237, 66, 66)', marker_line_width=1.5, opacity=0.6)

row5_col1.plotly_chart(tripd_fig)


#trip time by age

age_trip = df[['tripduration', 'birth year']]
age_trip['Age'] = ((2019-age_trip['birth year'])//5)*5
age_trip['tripduration'] = age_trip['tripduration']/60

age_trip = age_trip.groupby(['Age'], as_index=False)['tripduration'].agg('mean').rename(columns={'tripduration':'Avg Trip Duration'})

age_trip_fig = px.bar(age_trip, x="Age", y="Avg Trip Duration")

age_trip_fig.update_traces(marker_color='rgb(237, 157, 66)', marker_line_width=1.5, opacity=0.6)

row5_col2.plotly_chart(age_trip_fig)






