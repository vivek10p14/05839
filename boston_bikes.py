from numpy import int32
from plotly import colors
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import plotly.figure_factory as ff
from streamlit_metrics import metric, metric_row
import os

os.sys("ls")
os.sys("pip install -r requirements.txt")

st.set_page_config(layout="wide")

st.session_state['user_type'] = 'All'
st.session_state['age'] = [0, 100]
st.session_state['days_of_week'] = []
st.session_state['months'] = []
st.session_state['gender'] = 'All'


@st.cache
def load_data():
    df = pd.read_csv('enriched_boston.csv')
    orig_df = df
    station_df = pd.read_csv('station_index.csv')
    station_df = station_df.drop([station_df.columns[0]], axis=1)

    station_df = station_df[station_df.latitude != 0]
    station_df = station_df[station_df.longitude != 0]

    return df, orig_df, station_df


st.sidebar.header('Filters')

st.session_state['user_type'] = st.sidebar.radio('Type of User', ['All', 'Subscriber', 'Guest'])
st.session_state['age'] = st.sidebar.slider('Age of Users', 0, 100, (0, 100), 1)
st.session_state['days_of_week'] = st.sidebar.multiselect('Days Of Week', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
st.session_state['months'] = st.sidebar.multiselect('Month Of Year', ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
st.session_state['gender'] = st.sidebar.radio('Gender', ['All', '1', '2'])

st.markdown("""
<h1 style="color:#5DADE2" align='center'>
BlueBikes (Boston) Data Visualization
</h1>
""", unsafe_allow_html=True
)


with st.expander("View Data Details"):
    st.markdown("""
        <p>
            <ol>
                <li> This app aims to visualize the usage statistics for Blue Bikes (A bike sharing system in Boston, MA).
                <li> The data used for this app is from the year 2019.
                <li> The data was taken from kaggle <a href=https://www.kaggle.com/jackdaoud/bluebikes-in-boston> Link </a>
                <li> The author sources this data from the blue bikes website who have made some of their usage data public
                <li> This dataset contains a total of 17 columns
                <li> Each row in the data denotes a single trip taken from Station A to Station B.
                <li> The data does not provide any user id's and also masks the gender of the users. Therefore, the app shows Gender 1 and Gender 2.
                <li> Other columns include the name and geographical co-ordiantes of the station, birth year of the user (used to infer age), trip duration (in seconds) and the date and time when the trip was taken. 
            </ol>
        </p>
    """, unsafe_allow_html=True)

df, orig_df, station_df = load_data()


if st.session_state['user_type']!='All':
    if st.session_state['user_type'] == 'Guest':
        df = df[df.usertype == "Customer"]
    else:
        df = df[df.usertype == "Subscriber"]

min_age = st.session_state['age'][0]
max_age = st.session_state['age'][1]
df = df[((2019-(df['birth year']))>=min_age) & ((2019-(df['birth year']))<=max_age)]

if len(st.session_state['days_of_week'])!=0:
    days_filter = df.start_day.isin(st.session_state['days_of_week'])
    df = df[days_filter]

month_mapping = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}

if len(st.session_state['months'])!=0:
    candidate_months = st.session_state['months']
    month_int = [month_mapping[i] for i in candidate_months]
    months_filter = df.month.isin(month_int)
    df = df[months_filter]

if st.session_state['gender']!='All':
    df = df[df.gender == int(st.session_state['gender'])]    

# st.markdown(
#     """
#     <h3 style="color:#F7DC6F">
#     Statistics for the data given the current filters <br>
#     The delta values show change from previous filter set
#     </h3>
#     """,
#     unsafe_allow_html=True
# )

st.markdown(
    """
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    """, unsafe_allow_html=True
)

col1, col2, col3, col4, col5, col6, col7 = st.columns(7) # cols for displaying metrics


num_rides = len(df)
bikes_in_use = df['bikeid'].nunique()
avg_trip_duration = ((df['tripduration'].sum()/num_rides)/60).round(2)
gender1_trips = len(df[df.gender==1])
gender2_trips = len(df[df.gender==2])
subscribers_trips = len(df[df.usertype=="Subscriber"])
customer_trips = len(df[df.usertype=="Customer"])

try:
    col1.metric(label="Total Number of Rides", value="{0}".format(num_rides), delta="{0}".format(num_rides-st.session_state['num_rides']))
except:
    col1.metric(label="Total Number of Rides", value="{0}".format(num_rides), delta="{0}".format(0))

try:
    col2.metric(label="Number of Bikes in Use", value="{0}".format(bikes_in_use), delta="{0}".format(bikes_in_use-st.session_state['bikes_in_use']))
except:
    col2.metric(label="Number of Bikes in Use", value="{0}".format(bikes_in_use), delta="{0}".format(0))

try:
    col3.metric(label="Average Ride Duration", value="{0}".format(avg_trip_duration), delta="{0}".format((avg_trip_duration-st.session_state['avg_trip_duration']).round(2)))
except:
    col3.metric(label="Average Ride Duration", value="{0}".format(avg_trip_duration), delta="{0}".format(0.0))

try:
    col4.metric(label="Trips by Gender 1", value="{0}".format(gender1_trips), delta="{0}".format(gender1_trips-st.session_state['gender1_trips']))
except:
    col4.metric(label="Trips by Gender 1", value="{0}".format(gender1_trips), delta="{0}".format(0))

try:
    col5.metric(label="Trips by Gender 2", value="{0}".format(gender2_trips), delta="{0}".format(gender2_trips-st.session_state['gender2_trips']))
except:
    col5.metric(label="Trips by Gender 2", value="{0}".format(gender2_trips), delta="{0}".format(0))

try:
    col6.metric(label="Trips by Subscribers", value="{0}".format(subscribers_trips), delta="{0}".format(subscribers_trips-st.session_state['subscribers_trips']))
except:
    col6.metric(label="Trips by Subscribers", value="{0}".format(subscribers_trips), delta="{0}".format(0))

try:
    col7.metric(label="Trips by Customer", value="{0}".format(customer_trips), delta="{0}".format(customer_trips-st.session_state['customer_trips']))
except:
    col7.metric(label="Trips by Customer", value="{0}".format(customer_trips), delta="{0}".format(0))


st.markdown(
    """
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <br>
    """, unsafe_allow_html=True
)

st.markdown(
    """
    <h3 align=center style="color:#BDC3C7">
        MOST COMMONLY USED STATIONS
    </h3>
    """, unsafe_allow_html=True
)

st.session_state['num_rides'] = num_rides
st.session_state['bikes_in_use'] = bikes_in_use
st.session_state['avg_trip_duration'] = avg_trip_duration
st.session_state['gender1_trips'] = gender1_trips
st.session_state['gender2_trips'] = gender2_trips
st.session_state['subscribers_trips'] = subscribers_trips
st.session_state['customer_trips'] = customer_trips


row1_col1, dummy, row1_col2 = st.columns([6, 6, 1]) # first row of page

# heat map to find busy areas
start_ride_distribution = df.groupby(['start_hour', 'start station id'], as_index=False)['usertype'].count().rename(columns = {'usertype':'count'})

start_ride_distribution = start_ride_distribution.merge(station_df, left_on='start station id', right_on='id', how='inner')

start_ride_distribution = start_ride_distribution.sort_values(by='start_hour')

min_val = start_ride_distribution['count'].min()
max_val = start_ride_distribution['count'].max()//2

fig = px.density_mapbox(start_ride_distribution, lat='latitude', lon='longitude', z='count', radius=10, center=dict(lat=42.361001, lon=-71.084025), zoom=11, mapbox_style="stamen-terrain", hover_name='name', range_color=[min_val, max_val], animation_frame='start_hour', animation_group='id')

start_ride_distribution = start_ride_distribution.sort_values(by='count', ascending=False)


row1_col1.plotly_chart(fig, use_container_width=True)

row1_col1.markdown(
    """
    <p align='center'>
    1. Georaphical Locations for the most active stations spread over the day
    </p>
    """, unsafe_allow_html=True
)

#top stations used

st.session_state['hourly_range'] = row1_col2.slider("Time Range", 0, 23, (0, 23))
top_n = row1_col2.selectbox("Top N stations", [i for i in range (5, 21)])

station_use = df[['start station id', 'gender', 'start_hour']]

min_hour = st.session_state['hourly_range'][0]
max_hour = st.session_state['hourly_range'][1]

station_use = station_use[(station_use.start_hour>=min_hour) & (station_use.start_hour<=max_hour)]

station_use = station_use.groupby('start station id', as_index=False)['gender'].count().rename(columns={'start station id':'station_id', 'gender':'count'})
station_use = station_use.merge(station_df, left_on='station_id', right_on='id', how='inner')

fig_used_station = px.pie(station_use.head(top_n), values='count', names='name')
fig_used_station.update_traces(textinfo='percent+label', showlegend=False)



dummy.plotly_chart(fig_used_station, use_container_width=True)
dummy.markdown(
    """
    <p align='right'>
    2. Top N most active stations in the given time period of the day 
    </p>
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <br>
    """, unsafe_allow_html=True
)

st.markdown(
    """
    <h3 align=center style="color:#BDC3C7">
        RIDE DISTRIBUTION ACROSS HOURS, DAYS and MONTHS
    </h3>
    """, unsafe_allow_html=True
)

row2_col1, row2_col2 = st.columns(2) #row 2

# count of trips taken by day of week
count_df = df.groupby(['month','start_day'], as_index=False)['usertype'].count().rename(columns = {'usertype':'count'})

day_dict = {'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4, 'Friday':5, 'Saturday':6, 'Sunday':7, 'All':8}

count_df['day_int'] = count_df['start_day'].apply(lambda x: day_dict[x])

count_df = count_df.sort_values(by=['month', 'day_int'])

max_val = (count_df['count'].max())*1.5

fig = px.bar(count_df, x = 'start_day', y='count', color='start_day', animation_frame='month', animation_group='start_day', range_y=[0, max_val])

row2_col1.plotly_chart(fig)

row2_col1.markdown(
    """
    <p align='center'>
    3. Distribution of number of trips taken over different days of the week spread across months
    </p>
    """, unsafe_allow_html=True
)

# number of trips taken per day of week/hour of day
scatter_df = df.groupby(['month', 'start_hour', 'start_day'], as_index=False).count().rename(columns = {'usertype':'count'})

scatter_df['day_int'] = scatter_df['start_day'].apply(lambda x: day_dict[x])
scatter_df = scatter_df.sort_values(by=['month', 'day_int'])

fig2 = px.scatter(scatter_df, x='start_hour', y='start_day', color='start_day', size='count', animation_group='start_hour', animation_frame='month')

row2_col2.plotly_chart(fig2)

row2_col2.markdown(
    """
    <p align='center'>
    4. Most active period of the day for a given day of the week spread across months
    </p>
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <br>
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <h3 align=center style="color:#BDC3C7">
        USER TYPE STATISTICS
    </h3>
    """, unsafe_allow_html=True
)

row3_col1, row3_col2 = st.columns(2)

# subscribers vs casual across months

user_df = df.groupby(['month', 'usertype'], as_index=False)['gender'].count().rename(columns={'gender':'Number of Trips'})

user_df = user_df.sort_values(['month'])

utype_fig = px.bar(user_df, x="month", y="Number of Trips", color="usertype", color_discrete_sequence=px.colors.qualitative.D3)

row3_col1.plotly_chart(utype_fig)

row3_col1.markdown(
    """
    <p align='center'>
    5. The number of Trips taken by the different Subscribers/Guests
    </p>
    """, unsafe_allow_html=True
)

# subscriber demographic

age_df = df[['usertype', 'birth year']]
age_df['Age'] = ((2019-age_df['birth year'])//5)*5

age_df = age_df.groupby(['Age', 'usertype'], as_index=False)['birth year'].count().rename(columns={'birth year':'Count'})

age_user_fig = px.bar(age_df, x="Age", y="Count", color="usertype", color_discrete_sequence=px.colors.qualitative.D3)

row3_col2.plotly_chart(age_user_fig)

row3_col2.markdown(
    """
    <p align='center'>
    6. The number of Guest and Subscribed Users per Age Group
    </p>
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <br>
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <h3 align=center style="color:#BDC3C7">
        TRIP DURATION STATISTICS
    </h3>
    """, unsafe_allow_html=True
)

row5_col1, row5_col2 = st.columns(2)

# trip duration with hour of day

tripd_hour = df.groupby(['start_hour'], as_index=False)['tripduration'].agg('mean').rename(columns={'tripduration':'Avg Trip Time Mins', 'start_hour':'Hour of Day', 'start_day':'Day of Week'})

tripd_hour['Avg Trip Time Mins'] = tripd_hour['Avg Trip Time Mins']/60

tripd_fig = px.bar(tripd_hour, x="Hour of Day", y="Avg Trip Time Mins")

tripd_fig.update_traces(marker_color='rgb(237, 66, 66)', marker_line_width=1.5, opacity=0.6)

row5_col1.plotly_chart(tripd_fig)

row5_col1.markdown(
    """
    <p align='center'>
    7. Average Trip time for trips taken at a given hour of the day
    </p>
    """, unsafe_allow_html=True
)


#trip time by age

age_trip = df[['tripduration', 'birth year']]
age_trip['Age'] = ((2019-age_trip['birth year'])//5)*5
age_trip['tripduration'] = age_trip['tripduration']/60

age_trip = age_trip.groupby(['Age'], as_index=False)['tripduration'].agg('mean').rename(columns={'tripduration':'Avg Trip Duration'})

age_trip_fig = px.bar(age_trip, x="Age", y="Avg Trip Duration")

age_trip_fig.update_traces(marker_color='rgb(237, 157, 66)', marker_line_width=1.5, opacity=0.6)

row5_col2.plotly_chart(age_trip_fig)

row5_col2.markdown(
    """
    <p align='center'>
    8. Average Trip time for trips taken by users from a given age group
    </p>
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <br>
    """, unsafe_allow_html=True
)

st.markdown(
    """
    <h3 align=center style="color:#BDC3C7">
        BIKE USAGE STATICTICS
    </h3>
    """, unsafe_allow_html=True
)

row4_col1, row4_col2 = st.columns(2)

# total time every bike isused for
usage_df = orig_df.groupby(['bikeid'], as_index=False)['tripduration'].agg('sum').rename(columns={'bikeid':'bikeid'})
usage_df['tripduration'] = usage_df['tripduration']/3600
usage_df = usage_df.groupby(['tripduration'], as_index=False)['bikeid'].agg('nunique').rename(columns={'bikeid':'Bikes', 'tripduration':'Trip Duration in Hours'})

usage_fig = px.histogram(usage_df, x="Trip Duration in Hours", y="Bikes", marginal="rug")

row4_col1.plotly_chart(usage_fig)

row4_col1.markdown(
    """
    <p align='center'>
    9. Distribution for the number of bikes that have been used for a given time bucket thorughout the year (STATIC)
    </p>
    """, unsafe_allow_html=True
)

#new bikes added per month

bike_df = orig_df.groupby(['month'], as_index=False)['bikeid'].agg('nunique').rename(columns={'bikeid':'Number of Bikes Used'})
bike_fig = px.line(bike_df, x="month", y="Number of Bikes Used", text="Number of Bikes Used")

row4_col2.plotly_chart(bike_fig)

row4_col2.markdown(
    """
    <p align='center'>
    10. The number of distinct bikes being used over the months (STATIC)
    </p>
    """, unsafe_allow_html=True
)
st.markdown(
    """
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
    """, unsafe_allow_html=True
)


