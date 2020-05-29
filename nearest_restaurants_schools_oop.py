import numpy as np
import pandas as pd
import googlemaps
from haversine import haversine
from os import listdir
from random import choice


def format_geo_location(data_path):
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
    return data_longitude, data_latitude

class nearest_restaurants:

    def __init__(self, data_path):
        api_keys = ["AIzaSyBHWiHNgsyEL8IzkG42rcZYmqzjIXXHswE", "AIzaSyCWg8Nc_PHzUa3QFPDuiJZbTtduSR0Oy1o", "AIzaSyA6_WJ3FFz275fXDdUDqbfAoCeJv-MgU3M", "AIzaSyA-uUIEY9yQlMxLyB1VvClmccmh0UhAF1I", "AIzaSyBEY4QQTyrSpkQ7zh7cLTAarT1XT5n7-OM", "AIzaSyCHHKIsjkmyc7Gl-3FlwDwvriIdolBNxm0", "AIzaSyChA2jpAdVygHY3t2_JgIpLVPf5Slddc_4", "AIzaSyBOBMgIgASl-f_ti76DAHrIwQDXRkoOSAU"]
        self.data_path = data_path
        self.key = choice(api_keys)
        self.gmaps = googlemaps.Client(key = self.key)
        self.df = pd.read_csv(f"{self.data_path}")

    def view_schools(self):
        return self.df

    def make_coordinates(self):
        self.lat = format_geo_location(self.data_path)[1]
        self.long = format_geo_location(self.data_path)[0]
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
        school_coord_dict = {school: school_coordinates[i] for i, school in enumerate(self.df['name'].tolist())}

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
        school_coordinate_dict = {school : school_coordinates[i] for i, school in enumerate(self.df['name'].tolist())}
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
