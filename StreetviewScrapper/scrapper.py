import google_streetview.api
import google_streetview.helpers
import os
from lxml import etree

# Get API key
file = open('api_key.txt', 'r')
api_key = file.read()

# Define parameters for street view api
params = [{
  'size': '640x640', # max 640x640 pixels
  'location': '',
  'pitch': '0',
  'fov' : '90',
  'heading' : '',
  'key': api_key
}]

# Parse GPX file
tree = etree.parse('gpx_data/delporren2.gpx')

namespaces = {'ns':'http://www.topografix.com/GPX/1/0'}

# Iterate over all locations in the gpx file
for index, location_node in enumerate(tree.xpath('//ns:trk/ns:trkseg/ns:trkpt', namespaces=namespaces), start=1):
    children = location_node.getchildren()
    print('-----', index, '-----')
    if children :
        print('heading', children[0].text)
    print('latitude', location_node.get("lat"))
    print('longitude', location_node.get("lon"))

    # Set the position of this location to params
    params[0]['location'] = f'{location_node.get("lat")},{location_node.get("lon")}'
    # Set heading of this position to params
    if children :
        params[0]['heading'] = f'{children[0].text}'

    # Create a results object
    results = google_streetview.api.results(params)

    # Download images to directory 'maps'
    results.download_links('maps')

    # Rename file
    os.rename('maps/gsv_0.jpg', f'maps/gsv_{index}.jpg')
