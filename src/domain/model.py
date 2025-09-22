import uuid


class User:
    def __init__(self, first_name: str, last_name: str, email: str, id: str | None = None):
        self.id = id or str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def __repr__(self):
        return f"User(first_name={self.first_name}, last_name={self.last_name}, email={self.email})"

    def change_name(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name
