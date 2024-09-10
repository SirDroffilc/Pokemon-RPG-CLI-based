import os
import json
import requests
from sortedcontainers import SortedSet

def main() -> None:
    os.system("cls")
    trainer1 = Trainer.sign_up()
    print(trainer1)
    trainer2 = Trainer.sign_up()
    print(trainer2)
    trainer3 = Trainer.sign_up()
    print(trainer3)
    print(f"Current User: {Trainer.current_user}")
    return None


class Trainer:
    trainers = SortedSet(key=lambda trainer: trainer.username)
    current_user = None
    USERNAME_LIMIT = 15
    PASSWORD_LIMIT = 30
    unique_id_counter = 0

    def __init__(self, id, username, password) -> None:
        self._id = id
        self.username = username
        self.password = password

    @property
    def username(self):
        return self._username
    @username.setter
    def username(self, new_username):
        if len(new_username) > Trainer.USERNAME_LIMIT or len(new_username) < 3:
            raise ValueError(f"Username should be 3-{Trainer.USERNAME_LIMIT} characters.")
        self._username = new_username


    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, new_password):
        if len(new_password) > Trainer.PASSWORD_LIMIT or len(new_password) < 5:
            raise ValueError(f"Password should be 5-{Trainer.PASSWORD_LIMIT} characters.")
        self._password = new_password


    @classmethod
    def search_trainers(cls, target_username) -> "Trainer":
        left = 0
        right = len(cls.trainers) - 1

        while left <= right:
            mid = (left + right ) // 2
            if target_username == cls.trainers[mid].username:
                return cls.trainers[mid]
            elif target_username < cls.trainers[mid].username:
                right = mid - 1
            else:
                left = mid + 1
        
        return None
            
    @classmethod
    def sign_up(cls) -> "Trainer":

        def validate_username(username) -> str:
            if len(username) > Trainer.USERNAME_LIMIT or len(username) < 3:
                print(f"Username should be 3-{Trainer.USERNAME_LIMIT} characters.")
                return None
            
            if cls.search_trainers(username):
                print(f"Username already taken")
                return None
            
            return username
        
        def validate_password(password) -> str:
            if len(password) > Trainer.PASSWORD_LIMIT or len(password) < 5:
                print(f"Password should be 5-{Trainer.PASSWORD_LIMIT} characters.")
                return None
            return password
        
        username = None
        password = None
        while not username or not password:
            username = validate_username(input("Username: "))
            if not username:
                continue
            password = validate_password(input("Password: " ))
        
        cls.unique_id_counter += 1
        cls.current_user = cls(cls.unique_id_counter, username, password)
        cls.trainers.add(cls.current_user)
        return cls.current_user


    def __str__(self):
        return f"Username: {self.username} | ID: {self._id}"


if __name__ == "__main__":
    main()