import pandas as pd

# Load the original CSV file with the full movie list
data = pd.read_csv("/Users/sanjusathiyamoorthy/Desktop/Side Projects/GitHub/Movie-Suggestion-Backend/TMDB/output/all-movies-details-final.csv")  # Replace with your file name
#original_ids = set(data['id'])  # Extract all movie IDs from the original dataset

# Load the new CSV file with the genre one-hot encodings
# output_data = pd.read_csv("/Users/sanjusathiyamoorthy/Desktop/Side Projects/GitHub/Movie-Suggestion-Backend/Model/movies_with_genre_encoding.csv")  # Replace with your file name
# encoded_ids = set(output_data['movie_ID'])  # Extract all movie IDs from the encoded dataset

# Find the difference (IDs in original list but not in the encoded list)
#missing_ids = original_ids - encoded_ids



# Find duplicate movie IDs
duplicate_ids = data[data.duplicated(subset='id', keep=False)]

# Print duplicates
if not duplicate_ids.empty:
    print("Duplicate movie IDs found:")
    print(duplicate_ids)
else:
    print("No duplicate movie IDs found.")



