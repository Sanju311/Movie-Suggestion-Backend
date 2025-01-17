import subprocess
from app.service.get_user_movie_details import get_user_movie_details
from app.service.train_user_taste_profile import train_model
from app.service.predict_user_ratings import predict_ratings


def get_movie_recomendations(username: str):
    
    try:
        #scrape user's movies from Letterboxd given their username
        letterboxdurl = "https://letterboxd.com/" + username + "/films/"
        command = [
            "python", "-m", "app.service.listscraper",  # Adjust path as needed
            "--concat",
            "--url", letterboxdurl,
        ]
        subprocess.run(command, check=True)
        scraped_movies_output = "app/service/outputs/user_movie_list.csv"
        
        #Use scraped movies to get movie details from the database or the API
        user_rated_movies_output = get_user_movie_details(scraped_movies_output)

        #Use user's watched movie details to train the model
        trained_model = train_model(user_rated_movies_output)

        #Use model to predict user's rating for various movies and returning the top N
        predicted_ratings = predict_ratings(trained_model)
        return predict_ratings, 200
    
    except Exception as e:
        print(e)
        return {"error": "An error occurred while processing the request"}, 500