import pandas as pd
import ast


def predict_ratings(trained_model, scraped_movies_output):    
    
    movies = {}
    
    input_csv = 'app/utility/all-movies-FINAL.csv'
    
    #change this so that the input is a data frame
    
    
    #load movies from database
    data = pd.read_csv(input_csv)
    user_watched_movies = pd.read_csv(scraped_movies_output)
    
    #TODO: Filter out movies the user has already watched from the data
    
    features = ['budget', 'runtime', 'release_year', 'vote_average', 'parents_rating', 'plot_vector']
    data['plot_vector'] = data['plot_vector'].apply(ast.literal_eval)
    data = data.dropna(subset=features)
    
    # Ensure other features are numeric
    data[features] = data[features].apply(pd.to_numeric, errors='coerce')
    
    X_predict = data[features]
    data['predicted_rating'] = trained_model.predict(X_predict)
    
    # Sort by predicted ratings and select top N
    top_movies = data.sort_values(by='predicted_rating', ascending=False).head(50)
    
    
    #get movie photo and the url and add it to the dataframe
    
    
    #return that data in the API in a format that the front end can consume
    
    
    return top_movies[['title', 'id','vote_average','predicted_rating']]
    