from passlib.hash import bcrypt


class User:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        hashed_password: str,
    ) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hashed_password = hashed_password

    def check_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.hashed_password)

    def set_password(self, password: str) -> None:
        self.hashed_password = bcrypt.hash(password)
