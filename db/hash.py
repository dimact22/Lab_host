from passlib.context import CryptContext

# Configure bcrypt for password hashing
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    @staticmethod
    def bcrypt(password: str) -> str:
        # Hash the password using bcrypt
        return pwd_cxt.hash(password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        # Verify that the plain password matches the hashed password
        return pwd_cxt.verify(plain_password, hashed_password)
