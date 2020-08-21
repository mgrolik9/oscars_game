
import requests

from oscars.local_settings import apikey


#functions to get data from api

def get_movie_poster(query_list, dictionary):
    for movie in query_list:
        payload = {'t': movie.title, 'y': 2019, 'apikey': apikey}
        response = requests.get("http://www.omdbapi.com/", params=payload)
        json_response = response.json()
        poster = json_response.get("Poster")
        dictionary[movie] = poster
    return dictionary


def get_people_movie_poster(query_list, dictionary):
    for person in query_list:
        payload = {'t': person.movie.title, 'y': 2019, 'apikey': apikey}
        response = requests.get("http://www.omdbapi.com/", params=payload)
        json_response = response.json()
        poster = json_response.get("Poster")
        dictionary[person] = poster
    return dictionary

