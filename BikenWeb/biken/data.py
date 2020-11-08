from .models import db, User, Itinerary, ItineraryOwnership
from flask_login import current_user, login_required, logout_user
import random
import string
import re

def storeItinerary(itineraryData):

    # Check if itinerary is already stored
    existingItinerary = Itinerary.query.filter_by(polyline=itineraryData["polyline"]).first()
    if not existingItinerary:
        # Create a random ID
        randomString = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        newItinerary = Itinerary(
            itineraryIdentifier=randomString,
            polyline=itineraryData["polyline"],
            distance=itineraryData["distance"],
            duration=int(itineraryData["duration"]),
            startCoordLat=itineraryData["start"]["lat"],
            startCoordLon=itineraryData["start"]["lon"],
            endCoordLat=itineraryData["end"]["lat"],
            endCoordLon=itineraryData["end"]["lon"]
        )
        db.session.add(newItinerary)
        db.session.commit()  #

        print("Itinerary stored")
        return randomString
    else:
        print("Itinerary already stored")
        return existingItinerary.itineraryIdentifier



def bindUserToItinerary(itineraryId,userId) :
    itineraryAlreadyStored = ItineraryOwnership.query.filter_by(itineraryIdentifier=itineraryId,userId=userId).first()
    if not itineraryAlreadyStored:
        ownership = ItineraryOwnership(
            itineraryIdentifier=itineraryId,
            userId=userId,
            private=True,
            name="Itinerary "+itineraryId
        )
        db.session.add(ownership)
        db.session.commit()  
        print("Itinerary bind")
    else:
        print("Itinerary already bind")



def getAllItineraryFromUser(userId):
    itineraryList = []

        # Get all itinerary ID bind to the user
    itinerariesID = ItineraryOwnership.query.filter_by(userId = userId).all()



    for itinerary in itinerariesID:
        itineraryID = itinerary.itineraryIdentifier

        # Search this id in the itinerary DB
        itineraryObject = Itinerary.query.filter_by(itineraryIdentifier=itineraryID).first()
        itineraryObject.name = itinerary.name

        # transform "/" into "//"
        itineraryObject.polyline = re.escape(itineraryObject.polyline)

        itineraryList.append(itineraryObject)

    return itineraryList


def removeLinkUserItinerary(itineraryID,userId):

    itinerary = ItineraryOwnership.query.filter_by(itineraryIdentifier=itineraryID,userId=userId).first()

    if itinerary:
        ItineraryOwnership.query.filter_by(itineraryIdentifier=itineraryID,userId=userId).delete()
        db.session.commit()
        print("Route deleted")
        return True

    else :
        return False



def renameItinerary(itineraryID,userId,newName):

    itinerary = ItineraryOwnership.query.filter_by(itineraryIdentifier=itineraryID,userId=userId).first();

    if itinerary:
        # Edit the itinerary
        if newName!="" :
            if len(newName)<=100:
                print("New name :",newName)
                itinerary.name = newName
                db.session.commit()
                return True
            else:
                False
        else:
            False
    else :
        return False



def mergeAccount(existingStravaUser,current_user):
    # Transfering ownership of itineraries
    itineraries= ItineraryOwnership.query.filter_by(userId=existingStravaUser.userId).all()

    for itinerary in itineraries:
        itinerary.userId=current_user.userId
 
    bufferId = current_user.userId
    bufferName = current_user.name
    bufferEmail = current_user.email
    bufferPassword = current_user.password

    # Remove the one of the two account
    User.query.filter_by(email=current_user.email).delete()


    # Replacing userID, name, email and password from Strava account.
    existingStravaUser.userId=bufferId
    existingStravaUser.name=bufferName
    existingStravaUser.email=bufferEmail
    existingStravaUser.password=bufferPassword

    db.session.commit()

    return existingStravaUser



def getPolylineFromId(itineraryId):
    existingItinerary = Itinerary.query.filter_by(itineraryIdentifier=itineraryId).first()

    if existingItinerary:
        return existingItinerary.polyline
    else:
        return -1