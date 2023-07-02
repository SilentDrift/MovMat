import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from Levenshtein import distance as levenshtein_distance

# Load the movie data from Excel into a pandas DataFrame
df = pd.read_csv('movies_metadata.csv')


# Calculate similarity scores for genres using Jaccard index
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1) + len(set2) - intersection
    return intersection / union

genres_similarity = []
for i in range(len(df)):
    genres_i = set(df.loc[i, 'genres'].split('|'))
    row_similarities = []
    for j in range(len(df)):
        genres_j = set(df.loc[j, 'genres'].split('|'))
        similarity = jaccard_similarity(genres_i, genres_j)
        row_similarities.append(similarity)
    genres_similarity.append(row_similarities)

# Calculate similarity scores for production companies using Jaccard index
production_companies_similarity = []
for i in range(len(df)):
    companies_i = set(df.loc[i, 'production_companies'].split('|'))
    row_similarities = []
    for j in range(len(df)):
        companies_j = set(df.loc[j, 'production_companies'].split('|'))
        similarity = jaccard_similarity(companies_i, companies_j)
        row_similarities.append(similarity)
    production_companies_similarity.append(row_similarities)

# Calculate similarity scores for release dates using Euclidean distance
release_dates = pd.to_datetime(df['release_date'])
release_dates_normalized = (release_dates - release_dates.min()) / (release_dates.max() - release_dates.min())

release_date_similarity = []
for i in range(len(df)):
    date_i = release_dates_normalized[i]
    row_similarities = []
    for j in range(len(df)):
        date_j = release_dates_normalized[j]
        similarity = 1 / (1 + abs(date_i - date_j))
        row_similarities.append(similarity)
    release_date_similarity.append(row_similarities)

# Calculate similarity scores for titles using Levenshtein distance
title_similarity = []
for i in range(len(df)):
    title_i = df.loc[i, 'title']
    row_similarities = []
    for j in range(len(df)):
        title_j = df.loc[j, 'title']
        similarity = 1 - levenshtein_distance(title_i, title_j) / max(len(title_i), len(title_j))
        row_similarities.append(similarity)
    title_similarity.append(row_similarities)

# Calculate similarity scores for main actors using Jaccard index or cosine similarity
actors_similarity = []
for i in range(len(df)):
    actors_i = set(df.loc[i, 'main_actor'].split('|'))
    row_similarities = []
    for j in range(len(df)):
        actors_j = set(df.loc[j, 'main_actor'].split('|'))
        similarity = jaccard_similarity(actors_i, actors_j)
        row_similarities.append(similarity)
    actors_similarity.append(row_similarities)

# Combine the similarity scores into an overall similarity matrix
similarity_matrix = (
    genres_similarity +
    production_companies_similarity +
    release_date_similarity +
    title_similarity +
    actors_similarity
) / 5.0

# Take input from the user for a movie name
movie_name = input("Enter the name of a movie: ")

# Find the index of the movie in the DataFrame
movie_index = df[df['title'] == movie_name].index[0]

# Get the similarity scores of the given movie with other movies
scores = similarity_matrix[movie_index]

# Create a dictionary to store the movie titles and their similarity scores
movie_scores = {df.loc[i, 'title']: scores[i] for i in range(len(df)) if i != movie_index}

# Sort the movies based on similarity scores in descending order
sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)

# Print the similar movies and their similarity scores
print(f"Similar movies to '{movie_name}':")
for movie, score in sorted_movies:
    print(f"{movie}: {score}")