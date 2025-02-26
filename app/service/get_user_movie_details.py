import requests
from app.config import MY_API_KEY
import spacy
import pandas as pd
import unicodedata


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
        
        # # Extract the first 3 acting credits
        # actors = [member['name'] for member in data['cast'][:3]]

        # Extract specific crew members
        director = next((member['name'] for member in data['crew'] if member['job'] == 'Director'), None)
        composer = next((member['name'] for member in data['crew'] if member['job'] == 'Original Music Composer'), None)
        screenplay = next((member['name'] for member in data['crew'] if member['job'] == 'Screenplay'), None)
        producer = next((member['name'] for member in data['crew'] if member['job'] == 'Producer'), None)
        
        return director, composer, screenplay, producer
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
        #origin_country = data.get('origin_country', None)
        #overview = data.get('overview', None)
        release_date = data.get('release_date', None)
        vote_average = data.get('vote_average', None)
        
        return budget, genres, runtime, vote_average, parents_rating
    
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


movie_database = pd.read_csv('app/service/data/final_movie_database.csv')
def fetch_all_movie_data(row):
    
    # Resolve the path dynamically (recommended for deployment)
    #CSV_PATH = Path(__file__).resolve().parent / "data" / "movie_database.csv"
    try: 
    
        #Film_title,Release_year,Owner_rating,Description
        title, year = row['Film_title'], row['Release_year']
        title = unicodedata.normalize('NFKC', title).encode('ascii', 'ignore').decode('ascii')
        
        
        print(f"fetching data for: {title}")
        
        curr_movie = movie_database[(movie_database['title'] == title) & (movie_database['Release_year'] == year)]
        
        if len(curr_movie) == 1:
            genres = curr_movie['genres'].values[0] 
            ID = curr_movie['id'].values[0]
            #origin_country = existing_movie_data["origin_country"].values[0] if "origin_country" in existing_movie_data else [None] * 7
            #overview = existing_movie_data["overview"].values[0] if "overview" in existing_movie_data else [None] * 7
            budget = curr_movie['budget'].values[0] 
            runtime = curr_movie['runtime'].values[0]
            #director_avg_rating = existing_movie_data["director_avg_rating"].values[0] if "director_avg_rating" in existing_movie_data else [None] * 7
            vote_average = curr_movie['vote_average'].values[0] 
            parents_rating = curr_movie['parents_rating'].values[0] 
            
            if parents_rating == 0:
                parents_rating = 13
            
            genre_encoding = curr_movie['genre_one_hot'].values[0]
            genres = curr_movie['genres'].values[0] 

        else:
            ID = fetch_movie_ID(title,year)
            if ID is None:
                return [None] * 7

            #if movie is already in the database, get the movie details needede 
            if ID in movie_database['id'].values:
                
                existing_movie_data = movie_database[
                    (movie_database["id"] == ID)].iloc[0]
                
                if not existing_movie_data.empty:
                    # Extract specific features from the existing movie data
                    #actors = existing_movie_data["actors"].values[0] if "actors" in existing_movie_data else [None] * 7
                    #director = existing_movie_data["director"].values[0] if "director" in existing_movie_data else [None] * 7
                    #release_date = existing_movie_data["release_date"].values[0] if "release_date" in existing_movie_data else [None] * 7
                    #composer = existing_movie_data["composer"].values[0] if "composer" in existing_movie_data else [None] * 7
                    #screenplay = existing_movie_data["screenplay"].values[0] if "screenplay" in existing_movie_data else [None] * 7
                    #producer_avg_rating = existing_movie_data["producer_avg_rating"].values[0] if "producer_avg_rating" in existing_movie_data else [None] * 7
                    genres = existing_movie_data["genres"] if "genres" in existing_movie_data else None
                    #origin_country = existing_movie_data["origin_country"].values[0] if "origin_country" in existing_movie_data else None
                    #overview = existing_movie_data["overview"].values[0] if "overview" in existing_movie_data else None
                    budget = existing_movie_data["budget"] if "budget" in existing_movie_data else None
                    runtime = existing_movie_data["runtime"] if "runtime" in existing_movie_data else None
                    #director_avg_rating = existing_movie_data["director_avg_rating"].values[0] if "director_avg_rating" in existing_movie_data else None
                    vote_average = existing_movie_data["vote_average"] if "vote_average" in existing_movie_data else None
                    parents_rating = existing_movie_data["parents_rating"] if "parents_rating" in existing_movie_data else None
                    genre_encoding = existing_movie_data["genre_one_hot"] if "genre_one_hot" in existing_movie_data else None
                    #plot_vector = existing_movie_data["plot-vector"].values[0] if "plot-vector" in existing_movie_data else None
                    #producer_avg_rating = existing_movie_data["producer_avg_rating"].values[0] if "producer_avg_rating" in existing_movie_data else None
                    #writer_avg_rating = existing_movie_data["writer_avg_rating"].values[0] if "writer_avg_rating" in existing_movie_data else None
                    #composer_avg_rating = existing_movie_data["composer_avg_rating"].values[0] if "composer_avg_rating" in existing_movie_data else None
                else:
                    raise ValueError("existing_movie_data is empty")
            else:
                
                # cast_data = fetch_cast(ID)
                # director, composer, screenplay, producer = cast_data
                
                movie_data = fetch_other_data(ID)
                budget, genres, runtime, vote_average, parents_rating = movie_data
                genre_encoding = calculate_genre_encoding(genres)

        if all(v is not None for v in [ID, budget, genres, genre_encoding, runtime, vote_average, parents_rating]):
            
            if parents_rating == 0.0:
                parents_rating = 13.0
            return [
            ID, budget, genres, genre_encoding, runtime, vote_average, parents_rating
            ]
        else:
            return [None] * 7
        
    except Exception as e:
        print(f"failed trying to get movie data for {title}: {e}")
        return [None] * 7
        



def get_user_movie_details(user_movie_data) -> pd.DataFrame:

    #all_movie_data = 'app/utility/all-movies-FINAL.csv'
    #output_csv = 'app/service/data/user_movie_list_details.csv'
    
    #writer.writerow(['title', 'id', 'actors', 'director', 'composer', 'writer', 'producer', 'budget', 'genres', 'genre_encoding','runtime', 'origin_country', 'overview', 'release_year', 'vote_average', 'parents_rating', 'user_rating', 'plot_vector'])

    new_columns = [
        "ID", "budget", "genres", "genre_encoding", "runtime", 
        "vote_average", "parents_rating"
    ]
    try:
        print(user_movie_data.head())
        # Apply function row-by-row and convert to DataFrame
        new_data = user_movie_data.apply(fetch_all_movie_data, axis=1, result_type="expand")
        new_data = new_data.dropna().reset_index(drop=True)
        
        # Assign new columns to DataFrame
        user_movie_data[new_columns] = new_data
        print(user_movie_data.head())
        return user_movie_data
    
    except Exception as e:
        print(f"failed trying to get user movie details: {e}")
        return None
