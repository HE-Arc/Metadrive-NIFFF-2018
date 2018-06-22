import os
import urllib.request
import argparse
import cv2
import numpy as np
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument(
    "-o", "--output",
    required=True, help="path to the directory to save scrapping results"
)
args = vars(ap.parse_args())



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

# Panorama options
pitch = 0
fov = 90
lat = 0
lon = 0
heading = 0


url = 'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=' + \
    f'{lat},{lon}&heading={heading}&pitch={pitch}&fov={fov}'

print(url)

# Get the streetview page
driver.get(url)

actions = ActionChains(driver)
actions.click()

index = 1

while 1:

    print('-----', index, '-----')
    print(driver.current_url)

    # element = driver.find_element_by_id("content-container")

    # Waiting the page to load
    time.sleep(7)

    # save a screenshot to disk
    driver.save_screenshot(f'{args["output"]}/output/gsv_{index}.png')

    # Image enhancement with opencv ---------------------------
    img = cv2.imread(f'{args["output"]}/output/gsv_{index}.png')
    # Cropping
    cropped = img[0:1920, 420:1500]

    # Save new image
    cv2.imwrite(f'{args["output"]}/output_2/gsv_{index}.jpg', cropped)

    os.remove(f'{args["output"]}/output/gsv_{index}.png')

    # Move forward
    # element.send_keys(Keys.ARROW_UP)
    actions.send_keys(Keys.ARROW_UP)
    actions.perform()
    actions.reset_actions()

    index += 1
