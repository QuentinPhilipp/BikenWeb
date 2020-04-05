import requests
import json


# small
north = "49.018312"
west = "7.3889923"
south = "49.083115"
east = "7.4961090"

# bigger
# north = "48.672826"
# west = "6.4709473"
# south = "49.206832"
# east = "7.8717041"

# 3.4936523,46.604167,8.3276367,49.667628

overpass_url = "http://overpass-api.de/api/interpreter"
# overpass_query = f"[out:json];\n(\nnode[highway=tertiary]({south},{west},{north},{east});\nway[highway=tertiary]({south},{west},{north},{east});\nnode[highway=secondary]({south},{west},{north},{east});\nway[highway=secondary]({south},{west},{north},{east});\nnode[highway=primary]({south},{west},{north},{east});\nway[highway=primary]({south},{west},{north},{east});\nway[highway=cycleway]({south},{west},{north},{east});\n);\nout body;\n>;\nout skel qt;\n"

overpass_query = f"""
[out:json];
// gather results
(
  // query part for: “highway=tertiary”
  node["highway"="tertiary"]({north},{west},{south},{east});
  way["highway"="tertiary"]({north},{west},{south},{east});
  // query part for: “highway=secondary”
  node["highway"="secondary"]({north},{west},{south},{east});
  way["highway"="secondary"]({north},{west},{south},{east});
  // query part for: “highway=primary”
  node["highway"="primary"]({north},{west},{south},{east});
  way["highway"="primary"]({north},{west},{south},{east});
  // query part for: “highway=residential”
  way[highway=cycleway]({north},{west},{south},{east});
);
// print results
out body;
>;
out skel qt;
"""
print(overpass_query)

response = requests.get(overpass_url,
                params={'data': overpass_query})

print("API response :",response)
data = response.json()
print(len(data["elements"]))






# [out:json];
# // gather results
# (
#   // query part for: “highway=tertiary”
#   node["highway"="tertiary"](49.018312,7.3889923,49.083115,7.4961090);
#   way["highway"="tertiary"](49.018312,7.3889923,49.083115,7.4961090);
#   // query part for: “highway=secondary”
#   node["highway"="secondary"](49.018312,7.3889923,49.083115,7.4961090);
#   way["highway"="secondary"](49.018312,7.3889923,49.083115,7.4961090);
#   // query part for: “highway=primary”
#   node["highway"="primary"](49.018312,7.3889923,49.083115,7.4961090);
#   way["highway"="primary"](49.018312,7.3889923,49.083115,7.4961090);
#   // query part for: “highway=residential”
#   way[highway=cycleway](49.018312,7.3889923,49.083115,7.4961090);
#
# );
# // print results
# out body;
# >;
# out skel qt;
