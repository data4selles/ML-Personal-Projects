import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# IMPORTACIÓN DE DATOS
df_ratings = pd.read_csv("Netflix_User_Ratings.csv")
df_ratings.columns

# Hay tantos datos que revienta al calcular. Vamos a tomar una muestra aleatoria de nuestros datos
# Seleccionar el 50% de los usuarios únicos
users_sample = df_ratings['CustId'].drop_duplicates().sample(frac=0.5, random_state=4)
print(f"Número de usuarios seleccionados: {len(users_sample)}")

# Seleccionar el 60% de las películas únicas
movies_sample = df_ratings['MovieId'].drop_duplicates().sample(frac=0.5, random_state=4)
print(f"Número de películas seleccionadas: {len(movies_sample)}")

# Filtrar el DataFrame con las muestras de usuarios y películas
df_filtered = df_ratings[
    (df_ratings['CustId'].isin(users_sample)) &
    (df_ratings['MovieId'].isin(movies_sample))
]

# Pivotamos la tabla para tener en las columnaslos userid y en las filas las puntuaciones que han hecho en las distintas películas
# Creamos una matriz item-usuario solo con los datos necesarios
matrix_user_rating = df_filtered.pivot_table(index='MovieId', columns='CustId', values='Rating', fill_value=0)

similitud_items = cosine_similarity(matrix_user_rating.to_numpy())

# CREACIÓN DE UNA MATRIZ DE RECOMENDACIONES
matriz_recomendaciones = pd.DataFrame(similitud_items, index=matrix_user_rating.index, columns=matrix_user_rating.index)


# Convertir el DataFrame de una matriz a un formato largo
matriz_recomendaciones_long = matriz_recomendaciones.stack().rename_axis(['id1', 'id2']).reset_index(name='similitud')
matriz_recomendaciones_long = matriz_recomendaciones_long[matriz_recomendaciones_long['id1'] != matriz_recomendaciones_long['id2']]
matriz_recomendaciones_long = matriz_recomendaciones_long[matriz_recomendaciones_long['id1'] < matriz_recomendaciones_long['id2']]


# GUARDA LA MATRIZ DE RECOMENDACION A DISCO
matriz_recomendaciones_long.to_pickle("matriz_recomendaciones_peliculas_long.pkl")
