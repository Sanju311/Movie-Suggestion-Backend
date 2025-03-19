from bs4 import BeautifulSoup
import pandas as pd

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import queue
import threading
import time


# def wait_for_elements_to_load(driver, timeout=10):
#     end_time = time.time() + timeout
#     last_empty_count = None
#     stable_start = None
#     stable_duration = 0.75

#     while time.time() < end_time:
#         # Get all the movie title spans
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.frame-title")))
#         elements = driver.find_elements(By.CSS_SELECTOR, "span.frame-title")
#         # Count how many of these have no text (i.e. are empty)
#         empty_count = sum(1 for el in elements if el.text.strip() == "")
        
#         # If there are no empty spans, we're done.
#         if empty_count == 0:
#             return elements
        
#         # If the empty count is unchanged, track the stable duration
#         if empty_count == last_empty_count:
#             if stable_start is None:
#                 stable_start = time.time()
#             elif time.time() - stable_start >= stable_duration:
#                 # The count has been stable long enough, so we return the elements
#                 return driver.page_source
#         else:
#             # Reset the stable timer if the count has changed
#             last_empty_count = empty_count
#             stable_start = None

#         # Wait for a short time before checking again
#         time.sleep(0.25)
    
#     # If timeout is reached, return the current elements even if not perfect
#     return driver.page_source

def scrape_movies(url: str, results: queue.Queue):
    
    try: 

        # Set up Selenium options
        options = Options()
        options.add_argument("--headless")  # Run in headless mode (remove this if you want to see the browser)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")  
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-images")  # Blocks images from loading

        # Initialize WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        
         
        #load the page
        driver.get(url)
        
        time.sleep(3) 
        #html = wait_for_elements_to_load(driver)
        html = driver.page_source
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.frame-title")))
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.rating")))
        
        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # WebDriverWait(driver, 30).until(
        #     lambda d: len(d.find_elements(By.CSS_SELECTOR, "span.frame-title")) > 0 and 
        #     all(el.text.strip() != "" for el in d.find_elements(By.CSS_SELECTOR, "span.frame-title"))
        # )
        
        #html = driver.page_source
        
        if html == None:
            raise Exception("Couldn't load page data")
        
        driver.quit()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, "lxml")

        # Extract movie titles and years
        for span in soup.find_all("span", class_="frame-title"):
            title = None
            year = None
            rating = None
            
            title_text = span.get_text(strip=True)
            #print(span)
            
            if title_text:
                title, year = title_text.rsplit(" ", 1)  # Splits at the last space
                year = year.strip("()")
            
            # Extract rating correctly by finding the nearest rating span
            rating_span = span.find_parent("div").find_next("span", class_="rating")
            
            if rating_span:
                rating = stars2val(rating_span.get_text(strip=True))

            if title and year and rating:
                results.put((title, int(year), float(rating)))
            else:
                #print(f"Couldn't find movie data for {title_text} - {rating_span}")
                continue
            

        
    except Exception as e:
        "Couldn't find movie data"
        print(e)
             
def stars2val(stars):

    conv_dict = {
        "★": 1.0,
        "★★": 2.0,
        "★★★": 3.0,
        "★★★★": 4.0,
        "★★★★★": 5.0,
        "½": 0.5,
        "★½": 1.5,
        "★★½": 2.5,
        "★★★½": 3.5,
        "★★★★½": 4.5 
    }

    try:
        val = conv_dict[stars.strip()]
        return val
    except Exception as e:
        print("Couldn't convert stars to value for {stars}: {e}")
        return None
    
    
def multithreading(user_name: str):
    
    results = queue.Queue()
    # results = []
    threads = []
    
    # determined how many pages are there to scrape
    url = f"https://letterboxd.com/{user_name}/films/"
    page_response = requests.get(url)
        
    page_soup = BeautifulSoup(page_response.content, 'lxml')
    page_elements = page_soup.find_all('li', class_='paginate-page')
    
    if not page_elements:
        last_page_num = 1
    else:
        last_page_num = int(page_elements[-1].find('a').text)
    
    inputURL_pages = []
    for i in range(last_page_num):
        curr_page_num = i+1
        inputURL_pages.append(url + "page/" +str(curr_page_num)+ "/")
        
    for url in inputURL_pages:
        
        #multi threading
        thread = threading.Thread(target=scrape_movies, args=(url, results))
        threads.append(thread)
        thread.start()

    #wait for all threads to finish
    for thread in threads: 
        thread.join()
    
    results_list = []
    while not results.empty():
        results_list.append(results.get())

        
    print(f"results_list: {len(results_list)}")
    df = pd.DataFrame(results_list, columns=['Film_title','Release_year','Owner_rating'])
    df.to_csv(f"new.csv", index=False)
    
    return df
    
    
if __name__ == "__main__":

    start = time.time()
    df = multithreading("pagarw12")
    print(time.time()-start)
       
