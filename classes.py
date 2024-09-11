import csv
import json
import os
import requests
from sortedcontainers import SortedSet
import time


def main() -> None:
    Trainer.retrieve()
    Trainer.display_trainers()

    Trainer.sign_up()
    Trainer.display_trainers()

    Trainer.save()
    return None


class Trainer:
    trainers: SortedSet["Trainer"] = SortedSet(key=lambda trainer: trainer.username)
    current_user: "Trainer" = None
    USERNAME_LIMIT = 15
    PASSWORD_LIMIT = 30
    unique_id_counter = 0


    def __init__(self, id:int=-1, username:str="", password:str="", pokemons:list[int]=[], pokeballs_count:int=6) -> None:
        self._id = id
        self.username = username
        self.password = password
        self.pokemons = pokemons # list of TrainedPokemon.id
        self.pokeballs_count = pokeballs_count


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

    @property
    def pokemons(self):
        return self._pokemons
    @pokemons.setter
    def pokemons(self, new_pokemon_list):
        if not isinstance(new_pokemon_list, list):
            raise ValueError("Invalid. Pokemons should be a list of integers")
        self._pokemons = new_pokemon_list

    @property
    def pokeballs_count(self):
        return self._pokeballs_count
    @pokeballs_count.setter
    def pokeballs_count(self, new_count):
        if new_count < 0:
            raise ValueError("You cannot have negative number of pokeballs.")
        elif new_count > 6:
            raise ValueError("You cannot carry more than 6 pokeballs")
        if new_count == 0:
            print("You have ran out of pokeballs! You have used the last one.")
        self._pokeballs_count = new_count
            
    
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
                time.sleep(1.5)
                return None
            
            if cls.search_trainers(username):
                print(f"Username already taken")
                time.sleep(1.5)
                return None
            
            return username
        
        def validate_password(password) -> str:
            if len(password) > Trainer.PASSWORD_LIMIT or len(password) < 5:
                print(f"Password should be 5-{Trainer.PASSWORD_LIMIT} characters.")
                time.sleep(1.5)
                return None
            return password
        
        username = None
        password = None
        while not username or not password:
            os.system("cls")
            print("SIGN UP")
            username = validate_username(input("Username: "))
            if not username:
                continue
            password = validate_password(input("Password: " ))
        
        cls.current_user = Trainer(cls.unique_id_counter + 1, username, password)
        cls.add_to_trainers(cls.current_user)
        
        return cls.current_user

    @classmethod
    def log_in(cls) -> "Trainer":

        def check_username(username: str) -> "Trainer":
            found_trainer = cls.search_trainers(username)
            if not found_trainer:
                print(f"Username not found\n")
                time.sleep(1.5)
                return None
            return found_trainer


        def check_password(trainer: Trainer, password: str) -> bool:
            if password != trainer.password:
                print(f"Incorrect Password\n")
                time.sleep(1.5)
                return False

            return True
        
        while(True):
            os.system("cls")
            print("LOG IN")

            username = input("Username: ")
            found_trainer = check_username(username)
            if not found_trainer:
                continue

            password = input("Password: ")
            if check_password(found_trainer, password):
                print(f"Logged In Successfully\n")
                break
        

        cls.current_user = found_trainer
        return cls.current_user

    @classmethod
    def log_out(cls) -> None:
        cls.current_user = None

    @classmethod
    def save(cls) -> None:
        with open("database/users/trainers.csv", "w", newline='') as file:
            fieldnames = ["id", "username", "password", "pokemons", "pokeballs_count"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for trainer in cls.trainers:
                writer.writerow({
                    "id": trainer._id,
                    "username": trainer.username,
                    "password": trainer.password,
                    "pokemons": json.dumps(trainer.pokemons),
                    "pokeballs_count": trainer.pokeballs_count
                })

    @classmethod
    def retrieve(cls) -> None:
        with open("database/users/trainers.csv", "r", newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                row["pokemons"] = json.loads(row["pokemons"])
                trainer = Trainer(
                    id=int(row["id"]), 
                    username=row["username"], 
                    password=row["password"], 
                    pokemons=row["pokemons"], 
                    pokeballs_count=int(row["pokeballs_count"]))
                
                cls.add_to_trainers(trainer)

    @classmethod
    def add_to_trainers(cls, trainer: "Trainer") -> None:
        if trainer._id > cls.unique_id_counter:
            cls.unique_id_counter = trainer._id

        cls.trainers.add(trainer)

    @classmethod
    def display_trainers(cls) -> None:
        os.system("cls")
        for i, trainer in enumerate(cls.trainers):
            print(f"{i+1}.) {trainer}")
        input("Press enter to continue...")

    
    def __str__(self):
        return f"Trainer {self.username} ID: {self._id}"


if __name__ == "__main__":
    main()