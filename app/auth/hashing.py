from passlib.context import CryptContext


class Hash:
    ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def hash_password(password: str) -> str:
        return Hash.ctx.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return Hash.ctx.verify(plain_password, hashed_password)
