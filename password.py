from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
new_hash = pwd.hash("1234")
print(new_hash)