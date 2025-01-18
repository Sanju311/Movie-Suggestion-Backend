
import time
import ast
from sklearn.preprocessing import MultiLabelBinarizer
import json
import pandas as pd

try:
    # Load the CSV file into a DataFrame
    data = pd.read_csv("/Users/sanjusathiyamoorthy/Desktop/Side Projects/GitHub/Movie-Suggestion-Backend/TMDB/output/all-movies-details-final.csv")

    # Convert genres from string representation of list to actual Python list
    data['genres'] = data['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

    # Use MultiLabelBinarizer to generate one-hot encoding for genres
    mlb = MultiLabelBinarizer()
    genre_one_hot = mlb.fit_transform(data['genres'])

    # Convert the one-hot encoding into a list of arrays
    data['genre_one_hot'] = [list(row) for row in genre_one_hot]

    # Create a new DataFrame with movie_ID and genre_one_hot
    output_data = data[['id', 'genre_one_hot']]
    output_data.columns = ['movie_ID', 'genre_one_hot']

    # Save the result to a new CSV file
    output_data.to_csv("movies_with_genre_encoding.csv", index=False)

    print("One-hot encoding saved to movies_with_genre_one_hot.csv")
    print("Genre-to-index mapping saved to genre_mapping.json")

except Exception as e:
    print(f"An error occurred: {e}")