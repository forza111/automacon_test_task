from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = "461554dcb6e1169277a0658acdb9b4634caf0c901fa63aaf5d3d9aa48f141056"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")






