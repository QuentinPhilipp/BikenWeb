import xml.etree.ElementTree as ET
import polyline
from datetime import datetime


def createGPXfile(itinerary, title):
    # Convert the polyline into gps points
    path = polyline.decode(itinerary.polyline, 5,geojson=True)

    try:
        filename = encoder(title,path)
        if filename:
            return filename
        else :
            return "Error"
    except :
        return "Error"

    


def encoder(inputTitle,coordList):
    gpx = ET.Element("gpx")
    gpx.set("version","1.1")
    gpx.set("creator","https://www.bikenapp.com")

    # Generating Metadata
    metadata = ET.SubElement(gpx,"metadata")
    name = ET.SubElement(metadata,"name")
    name.text = inputTitle
    author = ET.SubElement(metadata,"author")
    link = ET.SubElement(author,"link")
    link.set('href','https://bikenapp.com')



    #Generating path
    trk = ET.SubElement(gpx,"trk")
    name = ET.SubElement(trk,"name")
    name.text = inputTitle
    trkseg = ET.SubElement(trk,"trkseg")


    for elem in coordList :
        test = ET.SubElement(trkseg,"trkpt")
        test.set("lon",str(elem[0]))
        test.set("lat",str(elem[1]))

    filename = getFilename(inputTitle)

    # create a new XML file with the results
    mydata = ET.tostring(gpx,encoding='unicode', method='xml')
    myfile = open(filename, "w")
    myfile.write(mydata)

    # remove "biken/" from the path so it can be accessed from the browser
    filename = filename[6:]

    return filename

def getFilename(title):
    folder = "biken/static/gpxFiles/"
    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    filename = folder+date+"-"+title+".gpx"
    return filename

if __name__ == "__main__":
    # test route
    coordList = [[46.049877,14.506865],[46.049838,14.506828],[46.049819,14.506873],[46.049536,14.506586],
    [46.048906,14.506341],
    [46.048325,14.506213],
    [46.047817,14.506259],
    [46.047252,14.506427],
    [46.047242,14.506432],
    [46.047233,14.506401],
    [46.047112,14.506460],
    [46.046821,14.506658],
    [46.046797,14.506685],
    [46.046657,14.506697],
    [46.046599,14.506686],
    [46.046105,14.506660],
    [46.046002,14.506660],
    [46.045897,14.506645],
    [46.045868,14.506595],
    [46.045874,14.506527],
    [46.045896,14.506264],
    [46.045909,14.505943],
    [46.045909,14.505875],
    [46.045848,14.505875],
    [46.045846,14.505985],
    [46.045775,14.506022],
    [46.045659,14.506054],
    [46.044846,14.506183],
    [46.044440,14.506270],
    [46.044212,14.506317],
    [46.044061,14.506360],
    [46.043945,14.506392],
    [46.043570,14.506664],
    [46.043363,14.506963],
    [46.043157,14.507313],
    [46.042361,14.508615],
    [46.041738,14.509711],
    [46.041461,14.509407]]
    encoder('Example Route',coordList)





