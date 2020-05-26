import numpy as np
import pandas as pd
import streamlit as st
from nearest_restaurants_schools_oop import nearest_restaurants
from os import getcwd, listdir
from time import sleep
from datetime import datetime
from googlemaps import Client
from random import choice
import csv

# api_keys = ["AIzaSyDzGFnUansbrpbKmBriOfe0MV7jgIE0tq4", "AIzaSyAE5RQ7RYaXaQVbo4Hfum_GC7FxPoneiPs", "AIzaSyBCGTBzYDNyawvqpGtMKFdOiCLsUv7gU30", "AIzaSyBq16pq0-Aa6diYVOeBs0Kx-H3ulacDcoc", "AIzaSyDYcHpXlwN5jYFioA1jhNwbDW2_8f40l7Q"]
# key = choice(api_keys)

gmaps = Client("AIzaSyBHWiHNgsyEL8IzkG42rcZYmqzjIXXHswE")

now = datetime.now()

st.title("ChanR Analytics Presents: Geospatial Exploration with Schools")
address = st.text_input(label="What is the address you would like to search for?")

query = st.text_input(label="What kind of place do you want to search for?")

radius = st.slider(label="Search Radius (m): ", min_value=0, max_value=25, value=10)

op_time = st.radio("Place open now or later?: ", options=['Now', 'Later'])

if (address != '') and (query != ''):
    geocode_result = gmaps.geocode(address)
    latitude=geocode_result[0]['geometry']['location']['lat']
    longitude=geocode_result[0]['geometry']['location']['lng']
    lat_long = (latitude, longitude)
    results = gmaps.places(query=query, radius=radius, location=lat_long, open_now=True)
    headers = results['results'][0].keys()
    data_path = str(query) + str(now)
    data_path = f'{data_path}'+'.csv'

    with open(data_path, 'w') as f:
        dict_writer = csv.DictWriter(f, headers)
        dict_writer.writeheader()
        dict_writer.writerows(results['results'])
    nr = nearest_restaurants(f"{data_path}")
    st.write("## Objectives: ")

    st.write("- Transforming Coordinates Into Data via Google Maps API")
    st.write("- Visualizing Data on a Map")

    if st.button("Show School Data"):
        st.write(nr.df)

    st.write("### Using Google Maps API to search places near your schools:")

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

        count = 0
        place_names = nr.df['name'].tolist()
        result_dict = {}
        while count < 5:
            print('hello')
            result = nr_results[count]
            sleep(3)
            try:
                result2 = nr.gmaps.places(query=query, page_token=result['next_page_token'])
            except:
                print('no results')
            try:
                result3 = nr.gmaps.places(query=query, page_token=result2['next_page_token'])
            except:
                print('no results')
            try:
                result_dict[place_names[count]] = [result, result2, result3]
            except:
                result_dict[place_names[count]] = [result, result2]
            count += 1

        nr_frame_dict = nr.frame_process(result_dict)

        # if st.button("View Full Search Result: "):
        #     st.write(nr_frame_dict[])
        def load_mapped_data():
            data = pd.read_csv(data_path)
            data_geometry = data['geometry']
            data_latitude=[]
            data_longitude=[]
            n=0
            while n<len(data_geometry):
                data_dict=eval(data_geometry[n])
                data_latitude.append(data_dict['location']['lat'])
                data_longitude.append(data_dict['location']['lng'])
                n+=1
            lat_long_dict = {'latitude':data_latitude, 'longitude':data_longitude}
            df=pd.DataFrame(lat_long_dict)
            return df

        nr_frame_dict = nr.frame_process(result_dict)
        st.write("### Getting Haversine and Google Distances: ")

        haversine_distance = nr.haversine_distance(nr_frame_dict, 'mi')
        st.write("Haversine Distance Completed.")

        transport = st.radio("What type of transportation do you want the distance for?: ", options=['walking', 'bicycling', 'transit', 'driving'])

        google_distance = nr.google_distance(nr_frame_dict, transporation_mode=transport)
        st.write("Google Distance Matrix API Completed.")


        final_results = nr.merge_frames(nr_frame_dict, haversine_distance, google_distance)
        if st.button("Final Results"):
            st.write(final_results['names'])


        st.write("Show Results on a map: ")
        if st.checkbox('Show map'):
            st.map(load_mapped_data())

        # except:
        #     st.error('Sorry, we could not retrieve data for this request. Please check your location and search text.')
