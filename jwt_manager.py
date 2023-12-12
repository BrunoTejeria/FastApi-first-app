from jwt import (
  decode,
  encode
)

ALGORITHM = "HS256"
KEY = "bruno"
def create_token(data:dict):
  token: str = encode(payload=data, key=KEY, algorithm=ALGORITHM)
  return token

def validate_token(token: str) -> dict:
  data: dict = decode(token, key=KEY, algorithms=[ALGORITHM])
  return data


