from fastapi import FastAPI, Body, Path, Query, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from jwt import decode, DecodeError
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
from things import movies as movies

from config.database import Session, Base, engine
from models.movie import Movie


# Inicializar app
app = FastAPI()

# Propiedades de la app
app.title = "Aplicacion"
app.version = "0.0.1"
app.description = "Aplicacion de prueba"

Base.metadata.create_all(bind=engine)

class User(BaseModel):
  user:str
  password:str

class Movies(BaseModel):
  id: Optional[int] = None
  title: str = Field(min_length=5, max_length=15)
  overview: str = Field(min_length=10, max_length=50)
  year: int = Field(le=2024)
  rating: float = Field(ge=0.0, le=10.0)
  category: str = Field(min_length=5, max_length=15)

  class Config:
    schema_extra = {
      "example": {
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        "year": 2009,
        "rating": 7.8,
        "category": "Acción"
      }
    }


class JWTBearer(HTTPBearer):
  async def __call__(self, request: Request):
    auth = await super().__call__(request)
    token = auth.credentials

    if not token:
      raise HTTPException(status_code=403, detail="Credenciales Inválidas")

    try:
      data = validate_token(token)
      if data['user'] != "admin" or data['password'] != "admin":
        raise HTTPException(status_code=403, detail="Credenciales Inválidas")
    except DecodeError:
      raise HTTPException(status_code=403, detail="Error al decodificar el token")
      




@app.post("/login", tags=["auth"])
def login(user: User):
    if user.user == "admin" and user.password == "admin":
        token = create_token(user.dict())
        return JSONResponse(content={"token": token}, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/movies", tags=["movies"], dependencies=[Depends(JWTBearer())])
def get_all_movies():
  return JSONResponse(content=movies)


@app.get("/movies/{id}", tags=["movies"])
def get_movie(id: int = Path(..., ge=1)):
  for item in movies:
    if item['id'] == id:
      return JSONResponse(content=item, status_code=200)
  return JSONResponse({'message': 'Movie not found'}, status_code=404)


@app.get("/movies/", tags=["movies"], status_code=200)
def get_movies_by_category(category: str = Query(..., min_length=5, max_length=15)):
  results = []
  for item in movies:
    if item['category'] == category:
      results.append(item)
  return JSONResponse(content=results)


@app.post("/newMovie", tags=["movies"])
def create_movie(movie: Movies):
  movie.id = len(movies) + 1
  movie_dict = movie.dict()
  movies.append(movie_dict)
  return JSONResponse({'message': 'Movie created successfully'})



@app.put("/movies/{id}", tags=["movies"])
def update_movie(id: int, movie: Movies):
  for item in movies:
    if id == item['id']:
      item['title'] = movie.title
      item['overview'] = movie.overview
      item['year'] = movie.year
      item['rating'] = movie.rating
      item['category'] = movie.category
      return JSONResponse({'message': 'Movie updated successfully'})


@app.delete("/movies/{id}", tags=["movies"])
def delete_movie(id: int):
  for index, item in enumerate(movies):
    if id == item['id']:
      movies.pop(index)
      return JSONResponse({'message': 'Movie deleted successfully'}, status_code=200)
  return JSONResponse({"nessage": "Movie not found"}, status_code=404)


