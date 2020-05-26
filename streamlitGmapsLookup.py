import streamlit as st
import numpy as np
import pandas as pd
import requests, json
from geocoder import ip
import googlemaps
from haversine import haversine
from os import listdir
import csv
from datetime import datetime

now = datetime.now()

class nearest_ammenity():
    def __init__(self, data_path):
        self.data_path = data_path
        self.key = api_key
        self.gmaps = googlemaps.Client(key = self.key)
        self.df = pd.read_csv(f"{self.data_path}")

    def view_ammenity(self):
        return self.df

    def make_coordinates(self):
        self.lat = self.df['latitude'].tolist()
        self.long = self.df['longitude'].tolist()
        coordinates = list(zip(self.lat, self.long))
        return coordinates

    def search_results(self, query, radius, now):
        self.query = query
        self.radius = radius
        self.now = now
        self.coordinates = self.make_coordinates()
        self.results = []

        for coordinate in self.coordinates:
            self.result = self.gmaps.places(self.query, location=coordinate, radius=self.radius, open_now=self.now)
            self.results.append(self.result)
            return self.results

    def frame_process(self, result_dict):
        format_result_dict = {}
        for school in list(result_dict.keys()):
            names = []
            latitudes = []
            longitudes = []
            total_user_ratings = []
            ratings = []
            price_levels = []
            for result_structure in result_dict[school]:
                for result in result_structure['results']:
                    name = result['name']
                    latitude = result['geometry']['location']['lat']
                    longitude = result['geometry']['location']['lng']
                    user_rating = result['user_ratings_total']
                    rating = result['rating']
                    if 'price_level' in result.keys():
                        price_level = result['price_level']
                    else:
                        price_level = float('nan')
                        names.append(name)
                        latitudes.append(latitude)
                        longitudes.append(longitude)
                        total_user_ratings.append(user_rating)
                        ratings.append(rating)
                        price_levels.append(price_level)
                        format_result_dict[school] = {'names': names, 'latitude': latitudes, 'longitude': longitudes, 'total_user_ratings': total_user_ratings, 'ratings': ratings, 'price_levels': price_levels}
                        format_result_df_dict = {school: pd.DataFrame.from_dict(format_result_dict[school]) for school in format_result_dict.keys()}
        return format_result_df_dict

    def haversine_distance(self, school_results_dict, metric):
        distance_dict = {}
        school_coordinates = self.make_coordinates()
        school_coord_dict = {school: school_coordinates[i] for i, school in enumerate(self.df['school_name'].tolist())}
        for school in list(school_results_dict.keys()):
            distance_list = []
            restaurant_lat = school_results_dict[school]['latitude'].tolist()
            restaurant_long = school_results_dict[school]['longitude'].tolist()
            restaurant_coordinates = list(zip(restaurant_lat, restaurant_long))
            for restaurant_coordinate in restaurant_coordinates:
                dist = haversine(school_coord_dict[school], restaurant_coordinate, unit=metric)
                distance_list.append(dist)
                distance_dict[school] = distance_list
                haversine_df_dict = {school: pd.DataFrame.from_dict({f'haversine_distance ({metric})': distance_dict[school]}) for school in distance_dict.keys()}
        return haversine_df_dict

    def google_distance(self, frame_dict, transporation_mode):
        school_coordinates = self.make_coordinates()
        school_coordinate_dict = {school : school_coordinates[i] for i, school in enumerate(self.df['school_name'].tolist())}
        result_dict = {}
        for school in list(frame_dict.keys()):
            latitudes = frame_dict[school]['latitude'].tolist()
            longitudes = frame_dict[school]['longitude'].tolist()
            restaurant_coordinates = list(zip(latitudes, longitudes))
            result = self.gmaps.distance_matrix(origins=school_coordinate_dict[school], destinations=restaurant_coordinates, mode=transporation_mode, units='imperial')
            result_dict[school] = result
            frame_dict = {}
            for school in list(result_dict.keys()):
                results = result_dict[school]['rows'][0]['elements']
                distances = []
                durations = []
                for element in results:
                    if element['status'] == 'ZERO_RESULTS':
                        distance = float('nan')
                        duration = float('nan')
                    else:
                        dist_elem = element['distance']['text'].split(" ")
                        dur_elem = element['duration']['text'].split(" ")
                        distance = float(dist_elem[0])
                        duration = float(dur_elem[0])
                        distances.append(distance)
                        durations.append(duration)
                        frame_dict[school] = pd.DataFrame.from_dict({f'distance_from_school ({dist_elem[1]})': distances, f'{transporation_mode} duration ({dur_elem[1]})': durations})
        return frame_dict


    def merge_frames(self, result_dict, haversine_results, google_results):
        merged_results = {}
        for key in result_dict.keys():
            value = pd.concat([result_dict[key], haversine_results[key], google_results[key]], axis=1)
            merged_results[key] = value
        return merged_results

def load_mapped_data():
    data = pd.read_csv(filename)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data
# enter your api key here
api_key = 'AIzaSyDzGFnUansbrpbKmBriOfe0MV7jgIE0tq4'

url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"


# r = requests.get(url + 'query=' + query +
#                         '&key=' + api_key)
#
# x = r.json()
#
# y = x['results']
#
# for i in range(len(y)):
#
#     print(y[i]['name'])
st.title('Necessity service look up')

query=st.text_input('input your search here')

user_radius = st.slider("How far do you want your search results to be (km): ", 0, 100)

gmaps = googlemaps.Client(key=api_key)

my_location = ip("me").latlng

if (query != '') and  (user_radius!=0):
    try:
        results = gmaps.places(query, radius=user_radius, location=my_location, open_now=True)
        headers = results['results'][0].keys()
        filename = str(query) + str(now)
        filename = f'{filename}'+'.csv'

        with open(filename, 'w') as f:
            dict_writer = csv.DictWriter(f, headers)
            dict_writer.writeheader()
            dict_writer.writerows(results['results'])
            amenity = nearest_ammenity(filename)
    except:
        st.error('Sorry, we could not retrieve data for this request. Please check your location and search text.')

def load_mapped_data():
    data = pd.read_csv(filename)
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

if st.checkbox('Show raw data'):
     st.subheader('Raw data for search')
     st.write(amenity.view_ammenity())

if st.checkbox('Show map'):
    st.subheader('Mapped locations')
    st.map(load_mapped_data())
