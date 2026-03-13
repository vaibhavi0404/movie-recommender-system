import streamlit as st
import pickle
import pandas as pd
import os
import requests
import time

# 🔑 Paste your TMDB API key here
API_KEY = "2c822f13d4ab812e4c9c67d7cdcb0b53"

# Get folder where app.py exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load pickle files
movies_dict = pickle.load(open(os.path.join(BASE_DIR, 'movie_dict.pkl'), 'rb'))
similarity = pickle.load(open(os.path.join(BASE_DIR, 'similarity.pkl'), 'rb'))

movies = pd.DataFrame(movies_dict)


# Function to fetch poster from TMDB with error handling and retries
def fetch_poster(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"

    for attempt in range(3):  # try up to 3 times
        try:
            response = requests.get(url, timeout=5)  # 5 seconds timeout
            response.raise_for_status()  # raise error for bad HTTP status
            data = response.json()

            if data['results']:
                poster_path = data['results'][0]['poster_path']
                if poster_path:
                    return "https://image.tmdb.org/t/p/w500" + poster_path
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}): {e}")
            time.sleep(2)  # wait 2 seconds before retrying

    # Return placeholder image if all retries fail or no poster found
    return "https://via.placeholder.com/500x750?text=No+Image"


# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_title))

    return recommended_movies, recommended_posters


# Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie:',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for col, name, poster in zip(cols, names, posters):
        with col:
            st.image(poster)
            st.write(name)