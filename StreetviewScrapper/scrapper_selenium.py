import os
import urllib.request
import argparse
import cv2
import numpy as np
import time

from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

from lxml import etree

# Construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument(
    "-i", "--input",
    required=True, help="path to input gpx file to be scrapped"
)
ap.add_argument(
    "-o", "--output",
    required=True, help="path to the directory to save scrapping results"
)
args = vars(ap.parse_args())

# Panorama options
pitch = 0
fov = 90

# 4096x2160
width = 1920
height = 1920

# Selenium & PhantomJS
options = webdriver.ChromeOptions()
# headless mode
options.add_argument('headless')
# set the window size
options.add_argument(f'window-size={width}x{height}')
# log level
options.add_argument("log-level=3")

# Headless Chrome Driver
driver = webdriver.Chrome(
    executable_path='./chromedriver',
    chrome_options=options
)

# Parse GPX file
tree = etree.parse(args["input"])  # 'gpx_data/delporren2.gpx'

namespaces = {'ns': 'http://www.topografix.com/GPX/1/0'}

# Iterate over all locations in the gpx file
for index, location_node in enumerate(
        tree.xpath('//ns:trk/ns:trkseg/ns:trkpt', namespaces=namespaces),
        start=1):
    children = location_node.getchildren()
    print('-----', index, '-----')

    heading = 0
    if children:
        heading = f'{children[0].text}'

    print('lat : ', location_node.get("lat"))
    print('lon : ', location_node.get("lon"))
    print('hea : ', heading)
    print('pit : ', pitch)
    print('fov : ', fov)

    url = 'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=' + \
        f'{location_node.get("lat")},{location_node.get("lon")}' + \
        f'&heading={heading}&pitch={pitch}&fov={fov}'

    print(url)

    # Get the streetview page
    driver.get(url)

    # Waiting the page to load
    time.sleep(5)

    # save a screenshot to disk
    driver.save_screenshot(f'{args["output"]}/output/gsv_{index}.png')

    # Image enhancement with opencv ---------------------------
    img = cv2.imread(f'{args["output"]}/output/gsv_{index}.png')
    # Cropping
    cropped = img[0:1920, 420:1500]

    # Save new image
    cv2.imwrite(f'{args["output"]}/output_2/gsv_{index}.jpg', cropped)
