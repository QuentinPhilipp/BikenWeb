import requests
import json
import re  #Regex

south = "49.018312"
west = "7.3889923"
north = "49.083115"
east = "7.4961090"


overpass_url = "http://overpass-api.de/api/interpreter"
# overpass_query = f"[out:json];\n(\nnode[highway=tertiary]({south},{west},{north},{east});\nway[highway=tertiary]({south},{west},{north},{east});\nnode[highway=secondary]({south},{west},{north},{east});\nway[highway=secondary]({south},{west},{north},{east});\nnode[highway=primary]({south},{west},{north},{east});\nway[highway=primary]({south},{west},{north},{east});\nway[highway=cycleway]({south},{west},{north},{east});\n);\nout body;\n>;\nout skel qt;\n"

overpass_query = f"""
[out:json];
// gather results
(
  // query part for: “highway=tertiary”
  node["highway"="tertiary"]({south},{west},{north},{east});
  way["highway"="tertiary"]({south},{west},{north},{east});
  // query part for: “highway=secondary”
  node["highway"="secondary"]({south},{west},{north},{east});
  way["highway"="secondary"]({south},{west},{north},{east});
  // query part for: “highway=primary”
  node["highway"="primary"]({south},{west},{north},{east});
  way["highway"="primary"]({south},{west},{north},{east});
  // query part for: “highway=residential”
  way[highway=cycleway]({south},{west},{north},{east});
);
// print results
out body;
>;
out skel qt;
"""
print(overpass_query)



s = "this\n is \n a good \n question"
s = re.sub(r"\bis\b","is not",s)
print(s)

response = requests.get(overpass_url,
                params={'data': overpass_query})

# print(response)
data = response.json()
# print(data)






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
