import os, urllib.request
import argparse
import cv2
import numpy as np
from lxml import etree


def get_streetview_image(params, path):
    size = params['size']
    location = params['location']
    fov = params['fov']
    heading = params['heading']
    pitch = params['pitch']
    key = params['key']

    url = f'https://maps.googleapis.com/maps/api/streetview?size={size}&location={location}&fov={fov}&heading={heading}&pitch={pitch}&key={key}'
    urllib.request.urlretrieve(url, path)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="path to input gpx file to be scrapped")
ap.add_argument("-o", "--output", required=True, help="path to the directory to save scrapping results")
args = vars(ap.parse_args())

# Get API key from txt
file = open('api_key.txt', 'r')
api_key = file.read()

parameters = {
  'size': '640x640', # max 640x640 pixels
  'location': '',
  'pitch': '0',
  'fov' : '90',
  'heading' : '',
  'key': api_key
}

# Parse GPX file
tree = etree.parse(args["input"]) # 'gpx_data/delporren2.gpx'

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
    parameters['location'] = f'{location_node.get("lat")},{location_node.get("lon")}'
    # Set heading of this position to params
    if children :
        parameters['heading'] = f'{children[0].text}'

    # Get the image at given url and save it into given folder
    get_streetview_image(parameters, f'{args["output"]}/output/gsv_{index}.jpg')

    # Image enhancement with opencv ---------------------------
    img = cv2.imread(f'{args["output"]}/output/gsv_{index}.jpg')
    # Resize
    res = cv2.resize(img,None,fx=3, fy=3, interpolation = cv2.INTER_CUBIC)
    # Cropping
    cropped = res[0:1920, 420:1500]
    # Gaussian Blur
    blur = cv2.GaussianBlur(cropped,(5,5),0)
    # Save new image
    cv2.imwrite( f'{args["output"]}/output_2/gsv_{index}.jpg', blur );
