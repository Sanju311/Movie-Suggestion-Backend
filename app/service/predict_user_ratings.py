import pandas as pd
import ast


def predict_ratings(trained_model, scraped_movies_output):    
    
    try:
        #load movies from database
        input_csv = 'app/service/data/movie_database.csv'
        data = pd.read_csv(input_csv)
        
        #TODO: Filter out movies the user has already watched from the data
        
        features = ['budget', 'runtime', 'Release_year', 'vote_average', 'parents_rating']
        genre_features = [f'genre_{i}' for i in range(18)]
        features = features + genre_features
        
        #data['plot_vector'] = data['plot_vector'].apply(ast.literal_eval)
        
        data.rename(columns={
        'release_date': 'Release_year'
        }, inplace=True)
        data['Release_year'] = data['Release_year'].astype(str).str[:4]
         
        # Convert genre_encoding from string to list
        def safe_literal_eval(val):
            
            if isinstance(val, list):
                return val
            elif isinstance(val, str):
                try:
                    return ast.literal_eval(val)
                except (ValueError, SyntaxError):
                    print(f"Failed to evaluate {val}")
                    print(ValueError, SyntaxError)
                    return [0] * 18
        
        data['genre_one_hot'] = data['genre_one_hot'].apply(safe_literal_eval)
        genre_df = pd.DataFrame(data['genre_one_hot'].tolist(), columns=genre_features)
        data = pd.concat([data, genre_df], axis=1)
        
        
        # Ensure other features are numeric
        data[features] = data[features].apply(pd.to_numeric, errors='coerce')
        
        X_predict = data[features]
        data['predicted_rating'] = trained_model.predict(X_predict)
        
        # Sort by predicted ratings and select top N
        top_movies = data.sort_values(by='predicted_rating', ascending=False).head(100)
        
        # Filter out movies the user has already watched
        watched_movie_ids = scraped_movies_output['ID'].tolist()
        top_movies = top_movies[~top_movies['id'].isin(watched_movie_ids)]
        
        # Multiply the predicted_rating by 2 to make it out of 10
        top_movies['predicted_rating'] = top_movies['predicted_rating'] * 2
        
        #return that data in the API in a format that the front end can consume
        # Return all features along with the top movies
        
        return top_movies[['title','id','vote_average','predicted_rating', 'Release_year', 'parents_rating', 'runtime', 'genre_0', 'genre_1', 'genre_2', 'genre_3', 'genre_4', 'genre_5', 'genre_6', 'genre_7', 'genre_8', 'genre_9', 'genre_10', 'genre_11', 'genre_12', 'genre_13', 'genre_14', 'genre_15', 'genre_16', 'genre_17', 'genres']]

    
    except Exception as e:
        print(e)
        return {"Failed trying to predict user ratings"}, 500
    
