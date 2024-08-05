import json
import os
from bs4 import BeautifulSoup
import random
from time import sleep
from datetime import datetime
from selenium import webdriver
import vlc


# URL of udlejning.cej.dk with the corresponding search filters pre-applied
WEBSITE = ""
BASE = ""
# Range of seconds within which to check for new flats
PAUSE_RANGE_SECONDS = (30, 40)


def dump_to_json(flats):
    with open('flats.json', 'w') as f:    
        json.dump(flats, f)

def load_from_json():
    if os.path.exists('flats.json'):
        with open('flats.json') as f:
            return json.load(f)
    return {}

def compare_current_and_cached(flats, cached_flats):
    return {k: v for k, v in flats.items() if k not in cached_flats}
    

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    while True:
        driver.get(WEBSITE)
        rendered_source = driver.page_source

        # Parse the HTML
        soup = BeautifulSoup(rendered_source, 'html.parser')

        # Alternative method to check the presence of a tag with specific href inside div
        flats = {}
        for div in soup.find_all('div'):
            a_tag = div.find('a', href=True)
            if a_tag and a_tag['href'].startswith('/boliger/'):
                text = a_tag.text.replace('Reserveret', '')
                text = text.encode('ascii', 'ignore').decode('ascii')
                flats[text] = a_tag['href']

        # load cached
        cached_flats = load_from_json()

        # dump flats to a file
        dump_to_json(flats)
        
        # get the difference between the new flats and the cached flats
        new_flats = compare_current_and_cached(flats, cached_flats)

        # if new_flats is not empty, send a notification
        if new_flats:
            p = vlc.MediaPlayer("done-for-you.mp3")
            p.play()

            print("New flats found")
            head_driver = webdriver.Chrome()
            head_driver.maximize_window()
            for k, v in new_flats.items():
                # open each link as a new tab
                head_driver.execute_script("window.open('');")
                head_driver.switch_to.window(head_driver.window_handles[-1])
                head_driver.get(f"{BASE}{v}")
                print(f"New flat: {k}")

        else:
            # get current time hh:mm:ss
            print(f"{datetime.now().strftime('%H:%M:%S')}: Nothing new")

        # Sleep for a random amount of time
        sleep_time = random.randint(*PAUSE_RANGE_SECONDS)
        sleep(sleep_time)
        

if __name__ == "__main__":
    main()