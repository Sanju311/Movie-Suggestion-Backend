import requests
import csv
from apikey import MY_API_KEY
import ast
import spacy


headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {MY_API_KEY}"
}

# https://developer.themoviedb.org/reference/search-movie
def fetch_movie_ID(movie_name, release_year):
    try:
        #fetch movie data
        url = f"https://api.themoviedb.org/3/search/movie?query={movie_name}&include_adult=false&primary_release_year={release_year}"
        
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()  # No need for json.loads() as response.json() already parses
        if not data.get("results"):
            print(f"No results found for movie: {movie_name} ({release_year})")
            return None
            
        id = data["results"][0]["id"]
        return id
    except Exception as e:
        print(f"failed trying to get movie id for {movie_name}: {e}")
        return None


# API documentation: https://developer.themoviedb.org/reference/movie-credits
def fetch_cast(movie_ID):

    try: 
        url = f"https://api.themoviedb.org/3/movie/{movie_ID}/credits?language=en-US"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
    
        if not data['crew']:
            print(f"No results found for movie: {movie_ID}")
            return None
        
        # Extract the first 3 acting credits
        actors = [member['name'] for member in data['cast'][:3]]

        # Extract specific crew members
        director = next((member['name'] for member in data['crew'] if member['job'] == 'Director'), None)
        composer = next((member['name'] for member in data['crew'] if member['job'] == 'Original Music Composer'), None)
        screenplay = next((member['name'] for member in data['crew'] if member['job'] == 'Screenplay'), None)
        producer = next((member['name'] for member in data['crew'] if member['job'] == 'Producer'), None)
        
        return actors, director, composer, screenplay, producer
    except Exception as e:
        print(f"failed trying to get movie cast for {movie_ID}: {e}")
        return None



# https://developer.themoviedb.org/reference/movie-details
def fetch_other_data(movie_ID):
    
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_ID}?language=en-US&append_to_response=release_dates"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        
        release_dates_data = data.get("release_dates", {}).get("results", [])
        
        #default parents rating of PG13
        parents_rating = 13
        for country_data in release_dates_data:
            for release_date in country_data.get("release_dates", []):
                certification = release_date.get("certification", "").strip()
                if certification.isdigit():  # Check if the certification is an integer-only string
                    parents_rating = int(certification)  # Convert to integer and return
        
        
        if not data:
            print(f"No results found for movie: {movie_ID}")
            return None
        
        # Extract budget, genres, runtime, and origin country
        budget = data.get('budget', None)
        genres = [genre['name'] for genre in data.get('genres', [])]
        runtime = data.get('runtime', None)
        origin_country = data.get('origin_country', None)
        overview = data.get('overview', None)
        release_date = data.get('release_date', None)
        vote_average = data.get('vote_average', None)
        
        return budget, genres, runtime, origin_country, overview, release_date, vote_average, parents_rating
    
    except Exception as e:
        print(f"failed trying to get movie details for {movie_ID}: {e}")
        return None


genre_index_dict = {"Action": 0, "Adventure": 1, "Animation": 2, "Comedy": 3, "Crime": 4, "Drama": 5, "Family": 6, 
 "Fantasy": 7, "History": 8, "Horror": 9, "Music": 10, "Mystery": 11, "Romance": 12, "Science Fiction": 13, 
 "TV Movie": 14, "Thriller": 15, "War": 16, "Western": 17}

def calculate_genre_encoding(genres):
    # Initialize a zero array for all genres
    encoding = [0] * len(genre_index_dict)
    
    # try:
    #     parsed_genres = ast.literal_eval(genres)
    # except (ValueError, SyntaxError):
    #     parsed_genres = []  # Default to an empty list if parsing fails

    for genre in genres:
        if genre in genre_index_dict.keys():
            encoding[genre_index_dict[genre]] = 1
            
    return encoding


nlp = spacy.load('en_core_web_lg')
def get_plot_vector(plot):
    doc = nlp(plot)
    vector_array = doc.vector
    vector_list = vector_array.tolist()
    return vector_list

# FILE NAME
output_csv = '/Users/sanjusathiyamoorthy/Desktop/Side Projects/GitHub/Movie-Suggestion-Backend/TMDB/output/user_rated_movie_id.csv'
input_csv = "/Users/sanjusathiyamoorthy/Desktop/Side Projects/GitHub/Movie-Suggestion-Backend/scraper_outputs/user_movie_list.csv"


#read data using csv reader
with open(input_csv, mode='r', newline='', encoding='utf-8') as input_file:
    reader = csv.DictReader(input_file)  # Use DictReader to access columns by name

    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        
        writer = csv.writer(file)
        writer.writerow(['title', 'id', 'actors', 'director', 'composer', 'writer', 'producer', 'budget', 'genres', 'genre_encoding','runtime', 'origin_country', 'overview', 'release_year', 'vote_average', 'parents_rating', 'user_rating', 'plot_vector'])

        for row in reader:
            
            try:
                #check if in database and if not use API to get the data
                title = row['Film_title']
                year = row['Release_year']
                user_rating = row['Owner_rating']
                
                
                ID = fetch_movie_ID(title,year)
                if ID is  None:
                    continue
                    
                cast_data = fetch_cast(ID)
                if ID is  None:
                    continue
                else:
                    actors, director, composer, screenplay, producer = cast_data
                
                movie_data = fetch_other_data(ID)
                if movie_data is None:
                    continue
                else:
                    budget, genres, runtime, origin_country, overview, release_date, vote_average, parents_rating = movie_data
                    
                plot_vector = get_plot_vector(overview)
                if plot_vector is None:
                    continue
                    
            
                genre_encoding = calculate_genre_encoding(genres)
                writer.writerow([title, ID, actors, director, composer, screenplay, producer, budget, genres, genre_encoding, runtime, origin_country, overview, year, vote_average, parents_rating, user_rating, plot_vector])  

            except Exception as e:
                print(f"failed trying to get user movie data for {title}: {e}")


