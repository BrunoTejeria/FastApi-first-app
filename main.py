from fastapi import Depends, FastAPI, Body, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder

app = FastAPI()
app.title = "Mi aplicación con  FastAPI"
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
	async def __call__(self, request: Request):
		auth = await super().__call__(request)
		data = validate_token(auth.credentials)
		if data['user'] != "admin":
			raise HTTPException(status_code=403, detail="Credenciales son invalidas")







"""
Login
"""

class User(BaseModel):
	user:str
	password:str
@app.post('/login', tags=['auth'])
def login(user: User):
	"""
	email: admin
	\n
	pass: admin
	"""
	token: str = create_token(user.dict())
	return JSONResponse(status_code=200, content=token)



"""
Movies
"""

class Movie(BaseModel):
	id: Optional[int] = None
	title: str = Field(min_length=5, max_length=15)
	overview: str = Field(min_length=15, max_length=50)
	year: int = Field(le=2022)
	rating:float = Field(ge=1, le=10)
	category:str = Field(min_length=5, max_length=15)

	class Config:
		schema_extra = {
			"example": {
				"title": "Mi película",
				"overview": "Descripción de la película",
				"year": 2022,
				"rating": 9.8,
				"category" : "Acción"
			}
		}

@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
	db = Session()
	result = db.query(MovieModel).all()
	return JSONResponse(status_code=200, content=jsonable_encoder(result))

@app.get('/movies/{id}', tags=['movies'], response_model=Movie)
def get_movie(id: int = Path(ge=1, le=2000)) -> Movie:
	db = Session()
	result = db.query(MovieModel).filter(MovieModel.id == id).first()
	if not result:
		JSONResponse(status_code=404, content={"message": "Pelicula no encontrada"})
	else:
		return JSONResponse(status_code=200, content=jsonable_encoder(result))


@app.get('/movies/', tags=['movies'], response_model=List[Movie])
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie]:
	db = Session()
	result = db.query(MovieModel).filter(MovieModel.category == category).all()
	return JSONResponse(status_code=200, content=jsonable_encoder(result))


"""
Crear pelicula
"""
@app.post('/movies', tags=['movies'], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_movie(movie: Movie) -> dict:
	db = Session()
	new_movie = MovieModel(**movie.dict())
	db.add(new_movie)
	db.commit()
	return JSONResponse(status_code=201, content={"message": "Se ha registrado la película"})



"""
Actualizar pelicula
"""
@app.put('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def update_movie(id: int, movie: Movie)-> dict:
	db = Session()
	result = db.query(MovieModel).filter(MovieModel.id == id).first()
	if not result:
		JSONResponse(content={"message": "No se encotro la pelicula"}, status_code=404)

	result.title = movie.title
	result.overview = movie.overview
	result.year = movie.year
	result.rating = movie.rating
	result.category = movie.category

	db.commit()
	return JSONResponse(status_code=200, content={"message": "Se ha modificado la película"})

@app.delete('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def delete_movie(id: int)-> dict:
	db = Session()
	result = db.query(MovieModel).filter(MovieModel.id == id).first()

	if not result:
		return JSONResponse(status_code=404, content={"message": "Pelicula no econtrada"})

	db.delete(result)

	db.commit()
	return JSONResponse(status_code=200, content={"message": "Se ha eliminado la película"})

