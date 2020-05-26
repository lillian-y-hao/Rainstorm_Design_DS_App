import numpy as np
import pandas as pd
import streamlit as st
from nearest_restaurants_schools_oop import nearest_restaurants
from os import getcwd, listdir
from time import sleep

# Data Path
data_path = "school_coordinates.csv"

st.title("ChanR Analytics Presents: Geospatial Exploration with Schools")

nr = nearest_restaurants(f"{data_path}")

st.write("## Objectives: ")

st.write("- Transforming Coordinates Into Data via Google Maps API")
st.write("- Visualizing Data on a Map")

if st.button("Show School Data"):
    st.write(nr.df)

st.write("### Using Google Maps API to search places near your schools:")

query = st.text_input(label="What kind of place do you want to search for?")
st.write(f"You selected: {query}")
radius = st.slider(label="Search Radius (m): ", min_value=0, max_value=25, value=10)
st.write(radius)
op_time = st.radio("Place open now or later?: ", options=['Now', 'Later'])
st.write(op_time)

op_val = ""

if st.button("Search"):
    if op_time == 'Now':
        op_val = True
    elif op_time == 'False':
        op_val = False

nr_results = nr.search_results(query=query, radius=radius, now=op_val)
st.write("Google Places API Search Completed")

if st.button("Sample Result: "):
    st.write(nr_results[0]['results'][0])

st.write("### Get All Search Results: ")

count = 0
school_names = nr.df['school_name'].tolist()
result_dict = {}
while count < len(nr_results):
    result = nr_results[count]
    sleep(3)
    result2 = nr.gmaps.places(query=query, page_token=result['next_page_token'])
    sleep(3)
    result3 = nr.gmaps.places(query=query, page_token=result2['next_page_token'])
    result_dict[school_names[count]] = [result, result2, result3]
    count += 1

nr_frame_dict = nr.frame_process(result_dict)

school_option = st.radio("Select your high school: ", options=nr.df['school_name'])

if st.button("View Full Search Result: "):
    st.write(nr_frame_dict[school_option])

st.write("### Getting Haversine and Google Distances: ")
haversine_distance = nr.haversine_distance(nr_frame_dict, 'mi')
st.write("Haversine Distance Completed.")
transport = st.radio("What type of transportation do you want the distance for?: ", options=['walking', 'bicycling', 'transit', 'driving'])
google_distance = nr.google_distance(nr_frame_dict, transporation_mode=transport)
st.write("Google Distance Matrix API Completed.")

final_results = nr.merge_frames(nr_frame_dict, haversine_distance, google_distance)

if st.button("Final Results"):
    st.write(final_results[school_option])

st.write("### Visualizing The Results on a Map: ")
st.map(final_results[school_option])
