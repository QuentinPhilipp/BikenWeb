import requests
import json


def getActivity(userToken,number):


    endpoint = f"https://www.strava.com/api/v3/athlete/activities?&per_page={number}"
    headers = {"Authorization": f"Bearer {userToken}"}


    itineraries = requests.get(endpoint,headers=headers)

    print("Number of itinerary fetched:",len(itineraries.json()))
    # print(itineraries.json())

    return itineraries.json()


def getDetailedActivity(userToken,activityId):

    endpoint = f"https://www.strava.com/api/v3/activities/{activityId}"
    headers = {"Authorization": f"Bearer {userToken}"}


    activity = requests.get(endpoint,headers=headers)
    print(activity.json())


    return activity.json()
