from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import time
import torch
import tweepy
import os
import glob
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

country_time_zone = pytz.timezone('Portugal')

twitter_auth_keys = {
    "consumer_key": os.environ['API_KEY'],
    "consumer_secret": os.environ['API_KEY_SECRET'],
    "access_token": os.environ['ACCESS_TOKEN'],
    "access_token_secret": os.environ['ACCESS_TOKEN_SECRET'],
}

auth = tweepy.OAuthHandler(
    twitter_auth_keys['consumer_key'],
    twitter_auth_keys['consumer_secret']
)
auth.set_access_token(
    twitter_auth_keys['access_token'],
    twitter_auth_keys['access_token_secret']
)
api = tweepy.API(auth)

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(desired_capabilities=caps, options=options)
driver.get('https://canal.parlamento.pt/?chid=18&title=emissao-linear')

driver.find_element(By.CLASS_NAME, "vjs-big-play-button").click()
time.sleep(5)

while (1):
    country_time = datetime.now(country_time_zone)
    print(country_time.isoweekday())
    if country_time.hour in range(9, 16) and country_time.isoweekday() in range(1, 5):
        try:
            driver.find_element(By.ID, "mplayer_html5_api").screenshot('foo.png')

            # Model
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

            # Images
            dir = 'https://github.com/ultralytics/yolov5/raw/master/data/images/'
            imgs = ['foo.png']  # batch of images

            # Inference
            results = model(imgs)
            detections = results.pandas().xyxy[0].name.tolist()
            #if 'person' in detections:
            if 'cell_phone' in detections:
                # results.print()  # or .show(), .save()
                results.save('.')  # or .show(), .save()
                list_of_files = glob.glob('./runs/detect/*')
                latest_folder = max(list_of_files, key=os.path.getctime)
                latest_file = max(glob.glob(latest_folder+'/*'), key=os.path.getctime)
                print(latest_file)
                api.update_status_with_media('Mais um ao telemóvel...', latest_file)
        
        except:
            api.update_status('Error')
        time.sleep(60)
    else:
        time.sleep(60*60)
