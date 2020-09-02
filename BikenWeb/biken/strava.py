import requests
import json


def getActivity(userToken):


    endpoint = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {userToken}"}


    itineraries = requests.get(endpoint,headers=headers)


    print(len(itineraries.json()))



    return itineraries.json()
