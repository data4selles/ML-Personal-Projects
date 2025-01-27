#pip install fastapi uvicorn
#para lanzarlo poner en el terminal:
#uvicorn recomendador_api:app
#curl http://127.0.0.1:8000/recomendaciones/0

from fastapi import FastAPI, HTTPException
import pandas as pd
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import random
from pydantic import BaseModel


app = FastAPI()


# Agregar el middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes (en producción, deberías restringirlo)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)


# Cargar la matriz de recomendaciones y el dataset de películas
matriz_recomendaciones_long = pd.read_pickle("matriz_recomendaciones_peliculas_long.pkl")
df_movienames = pd.read_csv("movies.csv")  
df_movienames = df_movienames[df_movienames['MovieId'].isin(matriz_recomendaciones_long['id1'])]

# Modelo para las películas
class Movie(BaseModel):
    name: str

# Endpoint para obtener una película aleatoria con recomendaciones
@app.get("/pelicula-aleatoria")
async def pelicula_aleatoria():
    # Seleccionamos un MovieId aleatorio de las películas disponibles
    movie_id_random = random.choice(matriz_recomendaciones_long['id1'].unique())

    # Obtener el nombre de la película desde df_movienames
    movie_name = df_movienames[df_movienames['MovieId'] == movie_id_random]['MovieTitle'].values
    if len(movie_name) == 0:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    movie_name = movie_name[0]

    # Obtener las recomendaciones para esa película
    recomendaciones = matriz_recomendaciones_long[matriz_recomendaciones_long['id1'] == movie_id_random]
    recomendaciones = recomendaciones.sort_values(by='similitud', ascending=False).head(3)

    # Convertir los ids de las recomendaciones a enteros para asegurar que sean serializables
    recomendaciones['id1'] = recomendaciones['id1'].astype(int)
    recomendaciones['id2'] = recomendaciones['id2'].astype(int)

    # Realiza un cruce para agregar el nombre de la película recomendada
    recomendaciones = recomendaciones.merge(df_movienames[['MovieId', 'MovieTitle']], 
                                             left_on='id2', right_on='MovieId', 
                                             how='left')

    # Elimina la columna 'MovieId' ya que no es necesaria en la respuesta
    recomendaciones = recomendaciones.drop(columns=['MovieId'])

    # Devuelve el MovieId aleatorio, el nombre de la película y las recomendaciones
    return {
        "movie_id": int(movie_id_random),  # Convertimos también el id aleatorio a entero
        "movie_name": movie_name,
        "recommendations": recomendaciones.to_dict(orient="records")
    }

# Endpoint para buscar una película por nombre y obtener recomendaciones
@app.get("/buscar-pelicula")
async def buscar_pelicula(titulo: str):
    # Buscar la película en el dataset
    pelicula = df_movienames[df_movienames['MovieTitle'].str.contains(titulo, case=False, na=False)]
    if pelicula.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    # Obtener el ID de la película
    movie_id = pelicula.iloc[0]['MovieId']
    movie_name = pelicula.iloc[0]['MovieTitle']

    # Obtener las recomendaciones basadas en la matriz de similitudes
    recomendaciones = matriz_recomendaciones_long[matriz_recomendaciones_long['id1'] == movie_id]
    recomendaciones = recomendaciones.sort_values(by='similitud', ascending=False).head(3)

    # Convertir los ids de las recomendaciones a enteros para asegurar que sean serializables
    recomendaciones['id1'] = recomendaciones['id1'].astype(int)
    recomendaciones['id2'] = recomendaciones['id2'].astype(int)

    # Realiza un cruce para agregar el nombre de la película recomendada
    recomendaciones = recomendaciones.merge(df_movienames[['MovieId', 'MovieTitle']], 
                                             left_on='id2', right_on='MovieId', 
                                             how='left')

    # Elimina la columna 'MovieId' ya que no es necesaria en la respuesta
    recomendaciones = recomendaciones.drop(columns=['MovieId'])

    # Devuelve el nombre de la película y las recomendaciones
    return {
        "movie_name": movie_name,
        "recommendations": recomendaciones.to_dict(orient="records")
    }


@app.get("/movies")
async def get_all_movies():
    # Devuelve todas las películas en el dataset
    all_movies = df_movienames[['MovieId', 'MovieTitle']].to_dict(orient='records')
    return all_movies


@app.get("/recommendations/{movie_id}")
async def get_recommendations(movie_id: int):
    # Obtener las recomendaciones desde la matriz de recomendaciones
    recomendaciones = matriz_recomendaciones_long[matriz_recomendaciones_long['id1'] == movie_id]
    recomendaciones = recomendaciones.sort_values(by='similitud', ascending=False).head(3)

    # Obtener los títulos de las películas recomendadas
    recomendaciones = recomendaciones.merge(df_movienames[['MovieId', 'MovieTitle']], 
                                             left_on='id2', right_on='MovieId', 
                                             how='left')

    recomendaciones_list = recomendaciones['MovieTitle'].tolist()
    
    return {"recommendations": recomendaciones_list}

