import google_streetview.api
import google_streetview.helpers
import os
from lxml import etree

# Get API key
file = open('api_key.txt', 'r')
api_key = file.read()

# Define parameters for street view api
apiargs = {
  'size': '640x640', # max 640x640 pixels
  'location': '',
  'pitch': '0',
  'fov' : '90',
  'heading' : '180',
  'key': api_key
}

# Parse GPX file
tree = etree.parse('gpx_data/delporren.gpx')

namespaces = {'ns':'http://www.topografix.com/GPX/1/1'}

# Iterate over all locations in the gpx file
for index, location_node in enumerate(tree.xpath("//ns:trk/ns:trkseg/ns:trkpt", namespaces=namespaces), start=1):
    #locations[index] = {'lat':location_node.get("lat"), 'lon':location_node.get("lon")}

    print('-----', index, '-----')
    print('latitude', location_node.get("lat"))
    print('longitude', location_node.get("lon"))

    # Add the position of this location to apiargs
    apiargs['location'] += f';{location_node.get("lat")},{location_node.get("lon")}'

# Get a list of all possible queries from multiple parameters
api_list = google_streetview.helpers.api_list(apiargs)

# Create a results object for all possible queries
results = google_streetview.api.results(api_list)

# Download images to directory 'downloads'
results.download_links('maps')
