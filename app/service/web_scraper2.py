from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_letterboxd_movies_and_ratings(username_to_scrape):
    """
    Scrape all films and ratings from a Letterboxd user's profile,
    with extra debugging to help diagnose issues.
    """

    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-gpu")

    # Create driver without specifying custom paths
    driver = webdriver.Chrome(options=chrome_options)

    page = 1
    results = []

    try:
        while True:
            # Replace with your target URL
            url = f"https://letterboxd.com/{username_to_scrape}/films/page/{page}/"
            driver.get(url)

            print(f"\n--- Scraping page {page} ---")
            print(f"Request URL: {url}")
            # Wait for the JavaScript to load the content (adjust timing as needed)
            time.sleep(1)

            # Get the rendered HTML and parse it with BeautifulSoup
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # Find all film containers on this page
            film_containers = soup.find_all("li", class_="poster-container")
            print(f"Found {len(film_containers)} film containers on this page.")

            # If there are no films, we've likely reached the end
            if not film_containers:
                print("No film containers found; assuming end of results.")
                break

            for container in film_containers:
                title_text = None
                user_rating = None
                # Extract the data-film-name attribute
                frame_title = container.find("span", class_="frame-title")
                if frame_title:
                    title_text = frame_title.text.strip()
                    movie = title_text
                    year = movie[-5:-1]  # Extracts the 4-digit year by slicing out the characters between the parentheses
                    movie_name = movie[:-7]   # Removes the space and the 6-character year segment (including the parentheses)

                rating = container.find(
                    "span", class_="rating")
                if rating:
                    rating = rating.get_text()
                    user_rating = rating.count('★') + float(rating.count('½'))/2

                results.append({
                    "Film_title": movie_name,
                    "Release_year": year,
                    "Owner_rating": user_rating
                })
            page += 1
    except Exception as e:
        print(f"parsed up to page {page} until error: {e}")
        driver.quit()

    return results


def scrape_movies(username: str):
    
    data = scrape_letterboxd_movies_and_ratings(username)

    print("\n--- FINAL RESULTS ---")
    print(f"results list length: {len(data)}")
    
    df = pd.DataFrame(data, columns=['Film_title','Release_year','Owner_rating'])
    print(f"Results saved to scraper_output.csv")
    return df