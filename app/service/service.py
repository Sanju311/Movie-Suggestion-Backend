from pathlib import Path
from app.service.listscraper.__main__ import scrape_movies
from app.service.get_user_movie_details import get_user_movie_details
from app.service.train_user_taste_profile import train_model
from app.service.predict_user_ratings import predict_ratings
 
def get_movie_recomendations(username: str):
    
    try:
        #scrape user's movies from Letterboxd given their username
        letterboxdurl = "https://letterboxd.com/" + username + "/films/"

        # print("SCRAPING USER MOVIES...")
        scraped_movies = scrape_movies(letterboxdurl, username)
        #scraped_movies.to_csv('app/service/data/scraped_movies.csv', index=False)
        #scraped_movies = read_csv('app/service/data/scraped_movies.csv')
                
        #Use scraped movies to get movie details from the database or the API
        user_movie_details = get_user_movie_details(scraped_movies)
        #user_movie_details.to_csv('app/service/data/user_movie_details.csv', index=False)
        #user_movie_details = read_csv('app/service/data/user_movie_details.csv')
        
        print("TRAINING MODEL...")
        trained_model = train_model(user_movie_details)

        # #Use model to predict user's rating for various movies and returning the top N
        print("PREDICTING USER RATINGS...")
        predicted_ratings = predict_ratings(trained_model, user_movie_details)
        #predicted_ratings.to_csv('app/service/data/predicted_ratings.csv', index=False)
        
        
        # Select specific features to return
        filtered_predictions = predicted_ratings[['title','id','vote_average', 'predicted_rating', 'Release_year', 'genres']]

        return filtered_predictions
    
    except Exception as e:
        print(e)
        return {"error": "An error occurred while processing the request"}, 500
    
