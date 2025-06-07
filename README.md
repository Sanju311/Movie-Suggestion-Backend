# 🎬 Movie Suggestion Engine – Backend

This is the backend service for the Movie Suggestion Engine. It handles data processing, scraping, and model inference to generate personalized movie recommendations based on a user’s Letterboxd viewing history. The service uses a machine learning model trained on the user's rated movies to predict how much a user would enjoy unseen films.

---

## 🛠 Tech Stack

- **Framework:** Flask  
- **Machine Learning:** XGBoost  
- **Web Scraping:** Selenium, BeautifulSoup  
- **Data Processing:** Pandas, NumPy  
- **Deployment:** Railway  

---

## 🚀 Features

- Accepts a Letterboxd username and scrapes the user's watched films
- Cleans, formats, and enriches movie data with external sources if not stored within our own database (e.g., TMDB api)
- Extracts and engineers features for each unseen movie
- Uses a trained ML model to predict ratings for each unseen film
- Returns top personalized movie recommendations in descending order of predicted rating

---

## 🧠 Model Creation & Features

The core of the recommendation engine is an XGBoost regression model trained to predict a user's rating (0–5 scale) for unseen films based on their past ratings and movie metadata.

### 🎯 Training Data

The model was trained using a personally labeled dataset of several hundred movies, each with a user-provided rating. This ensured that the predictions aligned with personal taste rather than generalized public opinion.

### ✅ Features Used

- `genre`: One-hot encoded across 18+ genres
- `budget`: Estimated production budget
- `runtime`: Duration of the movie in minutes
- `release_year`: Extracted from full date
- `vote_average`: TMDB's average rating
- `parents_rating`: Encoded maturity rating
- `Owner_rating`: Target label (user's personal rating)


This structured dataset was passed into an XGBoost regressor, tuned for regression accuracy using cross-validation. After training, the model was used to infer ratings for unseen movies and return the top-N results.

---

## 📦 How to Run Locally

```bash
git clone https://github.com/yourusername/movie-suggestion-backend.git
cd movie-suggestion-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
