import pandas as pd
import concurrent.futures
from imdb import IMDb


df_cast = pd.read_csv('./actorfilms.csv').drop_duplicates(subset=['FilmID']).reset_index(drop=True)


new_df = df_cast[['FilmID', 'Year']]
unique_df = new_df.drop_duplicates(subset=['FilmID'])

list_ = unique_df.copy(deep=True)


# Create a new None column and set all values to None initially
unique_df = unique_df.assign(Genre=None)
unique_df = unique_df.assign(Cast=None)
unique_df = unique_df.assign(Director=None)
unique_df = unique_df.assign(Year=None)


ia = IMDb()

# Define a function to get data from IMDb
def get_imdb_data(film_id):
    rows_with_film_id = df_cast[df_cast['FilmID'] == film_id]


    #Print the index
    print(f"index is {rows_with_film_id.index[0]} of 44455")
    print('\n')
    film_id = film_id.lstrip('tt')
    print(f'film_id is {film_id}, Starting Download Data ...')
    try:
        movie = ia.get_movie(film_id)
        genre = movie['genres'][0] if 'genres' in movie else None
        cast = [actor['name'] for actor in movie['cast']][:10] if 'cast' in movie else None
        director = movie['director'][0]['name'] if 'director' in movie else None
        year = movie['year']
        print(f'Movie {movie}')
        print('Download completed')
        return genre, cast, director, year
    except Exception as e:
        print(f"Error getting data for film {film_id}: {e}")
        return None, None, None, None

# Create a list of film IDs to process
film_ids = list_['FilmID'].tolist()

# Define the number of worker threads to use
num_threads = 4

# Create a thread pool executor with the specified number of threads
with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    # Submit the get_imdb_data function for each film ID to the executor
    futures = [executor.submit(get_imdb_data, film_id) for film_id in film_ids]

    # Wait for all of the futures to complete
    results = concurrent.futures.wait(futures)

print('\nAssign Data to imdb_data')
# Extract the results from the completed futures and add them to the DataFrame
for i, result in enumerate(results[0]):
    genre, cast, director, year = result.result()
    if genre is not None:
        unique_df.iloc[i, unique_df.columns.get_loc('Genre')] = genre
    if cast is not None:
        if isinstance(cast, (list, tuple)):
            cast = ', '.join(cast)
        unique_df.iloc[i, unique_df.columns.get_loc('Cast')] = cast
    if director is not None:
        unique_df.iloc[i, unique_df.columns.get_loc('Director')] = director
    if year is not None:
        unique_df.iloc[i, unique_df.columns.get_loc('Year')] = year


# Save the updated DataFrame to a new CSV file
print('\nCreate imdb_data')
unique_df.to_csv('imdb_data.csv', index=False)
df_imdb_data = pd.read_csv('./imdb_data.csv')
print('completed')
