import csv
import json
import os
import random
import requests
from sortedcontainers import SortedSet
import time


def main() -> None:
    Pokemon.retrieve()
    Pokemon.display_wild_pokemons()

    pokemon = Pokemon.create_pokemon_from_name("charizard")
    if not pokemon:
        print("FAILED")
    else:
        print(repr(pokemon))
        time.sleep(3)

    Trainer.retrieve()
    trainer = Trainer.log_in()
    trainer.catch_and_train_pokemon(pokemon)

    trained_pokemon = TrainedPokemon.get_pokemon_by_id(trainer.pokemons[0])
    print(trained_pokemon)



    print(repr(trainer))


    return None


class Trainer:
    """Global Variables"""
    trainers: SortedSet["Trainer"] = SortedSet(key=lambda trainer: trainer.username)
    current_user: "Trainer" = None
    USERNAME_LIMIT = 15
    PASSWORD_LIMIT = 30
    POKEBALLS_LIMIT = 6
    unique_id_counter = 0


    def __init__(self, id:int=-1, username:str="", password:str="", pokemons:list[int]=[], pokeballs_count:int=6) -> None:
        self._id = id
        self.username = username
        self.password = password
        self.pokemons = pokemons # list of TrainedPokemon.id
        self.pokeballs_count = pokeballs_count

    """Getters and Setters"""
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
        elif new_count > Trainer.POKEBALLS_LIMIT:
            raise ValueError(f"You cannot carry more than {Trainer.POKEBALLS_LIMIT} pokeballs")
        if new_count == 0:
            print("You have ran out of pokeballs! You have used the last one.")
        self._pokeballs_count = new_count
            

    """Class Methods"""
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

    
    """Instance Methods"""
    def catch_and_train_pokemon(self, pokemon: "Pokemon") -> None:
        """Catches a Pokemon object, converts it into a TrainedPokemon object, and adds the id to self.pokemons"""

        if self.pokeballs_count <= 0:
            print(f"No pokeballs left to catch this pokemon.")
            return
        
        trained_pokemon = TrainedPokemon.create_trained_pokemon(pokemon, self._id)
        self.pokemons.append(trained_pokemon._id)
        self.pokeballs_count -= 1
        

    def __str__(self) -> str:
        return f"Trainer {self.username} ID: {self._id}"
    
    def __repr__(self) -> str:
        return (
            f"Trainer: {self.username}\n"
            f"ID: {self._id}\n"
            f"Password: {self.password}\n"
            f"Pokemons: {self.pokemons}\n"
            f"Pokeballs Count: {self.pokeballs_count}\n"
        )


class Pokemon:
    """PokeAPI Base URL"""
    base_url = "https://pokeapi.co/api/v2/"

    """Nested Classes for moves, hp, and base_dmg Attributes"""
    class Move:
        def __init__(self, name="def", type="def", power=1) -> None:
            self.name = name
            self.type = type
            self.power = power
        
        def __str__(self) -> str:
            return f"Move: {self.name} Type: {self.type} Power: {self.power}"
        
    class HitPoints:
        def __init__(self, base=50, current=50) -> None:
            self.base = base
            self.current = current

        def update_base_hp(self, level: int):
            base_hp = level * 50
            self.base = base_hp
            self.current = base_hp

        def __str__(self) -> str:
            return f"{self.current}/{self.base}"
    
    class BaseDamage:
        def __init__(self, dmg=10) -> None:
            self.dmg = dmg
        
        def update_base_dmg(self, level: int):
            base_dmg = level * 10
            self.dmg = base_dmg
        
        def __str__(self) -> str:
            return f"{self.dmg}"


    """Class Variables"""
    wild_fire_pokemons = []
    wild_grass_pokemons = []
    wild_water_pokemons = []
    poketypes = ["fire", "grass", "water"]


    def __init__(self, name="default", level=1, species="default", evolutions=[], types=[], weaknesses=[], moves=[], hp=HitPoints(), base_dmg=BaseDamage())-> None:
        self.name = name
        self.level = level
        self.species = species
        self.evolutions = evolutions
        self.types = types
        self.weaknesses = weaknesses
        self.moves = moves
        self.hp = hp 
        self.base_dmg = base_dmg

    
    @classmethod
    def create_pokemon_from_name(cls, pokemon_name: str) -> "Pokemon":
        """Creates a Pokemon Object from a string (pokemon_name) using PokeAPI"""
        """Always check if returned value is valid"""

        url = f"{cls.base_url}/pokemon/{pokemon_name.lower()}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Base URL Response Error {response.status_code}")
            return None
        pokemon_data = response.json()

        pokemon = Pokemon()
        pokemon.name = pokemon_data["name"]
        pokemon.level = random.randint(1, 10)
        pokemon.species = pokemon_data["species"]
        pokemon.evolutions = pokemon.get_evolutions(pokemon.species)
        pokemon.types = [poketype["type"]["name"] for poketype in pokemon_data["types"]]
        pokemon.weaknesses = pokemon.get_weaknesses(pokemon.types)
        pokemon.moves = pokemon.get_moves(pokemon_data["moves"]); """create a function"""
        pokemon.hp.update_base_hp(pokemon.level)
        pokemon.base_dmg.update_base_dmg(pokemon.level)
        return pokemon
    

    @classmethod
    def retrieve(cls):
        """Retrieves Wild Pokemons from database into the class variables"""
        """Each wild pokemon class variables will contain names only and NOT Pokemon objects"""

        for poketype in cls.poketypes:
            with open(f"./database/all_pokemons/wild_pokemons/wild_{poketype}_pokemons.txt") as file:
                for row in file: # each row is a name of a wild pokemon
                    match poketype:
                        case "fire":
                            cls.wild_fire_pokemons.append(row.strip())
                        case "grass":
                            cls.wild_grass_pokemons.append(row.strip())
                        case "water":
                            cls.wild_water_pokemons.append(row.strip())
                        case _:
                            print("Type not supported")
                            break


    @classmethod
    def display_wild_pokemons(cls) -> None:
        """Displays all wild pokemon names"""
        def display(wild_pokemons: list[str], poketype: str):
            print(f"WILD {poketype.upper()} POKEMONS")
            for pokemon_name in wild_pokemons:
                print(pokemon_name)
            print("")

        os.system("cls")
        for poketype in cls.poketypes:
            match poketype:
                case "fire":
                    display(cls.wild_fire_pokemons, poketype)
                case "grass":
                    display(cls.wild_grass_pokemons, poketype)
                case "water":
                    display(cls.wild_water_pokemons, poketype)
                case _:
                    print("Type not supported")
                    break


    """INSTANCE METHODS"""

    def get_evolutions(self, species) -> list[str]:
        """Returns the list of evolutions a pokemon has"""
        """Always check if returned value is valid"""
        url = species["url"]
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Species URL Response Error {response.status_code}")
            return None
        species_data = response.json()
        evolution_chain_url = species_data["evolution_chain"]["url"]

        evolution_chain_response = requests.get(evolution_chain_url)
        if evolution_chain_response.status_code != 200:
            print(f"Evolution Chain URL Response Error {evolution_chain_response.status_code}")
            return None
        
        evolution_chain_data = evolution_chain_response.json()

        evolutions: list[str]= []
        current_pokemon = evolution_chain_data["chain"]

        while current_pokemon:
            species_name = current_pokemon["species"]["name"]
            evolutions.append(species_name)
            current_pokemon = current_pokemon["evolves_to"][0] if current_pokemon["evolves_to"] else None

        return evolutions
    
    def get_weaknesses(self, types: list[str]) -> list[str]:
        strength_to_weakness_map = {"fire": "water", "grass": "fire", "water": "grass"}
        weaknesses = []
        for poketype in types:
            if poketype in strength_to_weakness_map.keys():
                weaknesses.append(strength_to_weakness_map[poketype])
        return weaknesses

    def get_moves(self, moves_data: list) -> list[Move]:
        def get_main_type():
            for poketype in self.types:
                if poketype in Pokemon.poketypes:
                    return poketype
            else:
                print("Type Error")
                return None
        
        main_moves_count = 0
        normal_moves_count = 0
        MAIN_MOVES_LIMIT = 5
        NORMAL_MOVES_LIMIT = 3
        pokemon_moves: list[Pokemon.Move] = []
        POKEMON_MOVES_LIMIT = 8
        main_type = get_main_type()

        for move in moves_data:
            if len(pokemon_moves) >= POKEMON_MOVES_LIMIT:
                break

            move_url = move["move"]["url"]
            move_response = requests.get(move_url)
            if move_response.status_code != 200:
                print(f"Move URL Response Error {move_response.status_code}")
                continue
            move_data = move_response.json()

            if move_data["power"] is None:
                continue

            if move_data["type"]["name"] == main_type and main_moves_count < MAIN_MOVES_LIMIT:
                pokemon_moves.append(Pokemon.Move(name=move_data["name"], type=move_data["type"]["name"], power=move_data["power"]))
                main_moves_count += 1
            
            elif move_data["type"]["name"] == "normal" and normal_moves_count < NORMAL_MOVES_LIMIT:
                pokemon_moves.append(Pokemon.Move(name=move_data["name"], type=move_data["type"]["name"], power=move_data["power"]))
                normal_moves_count += 1
        
        return pokemon_moves
        

    def __str__(self) -> str:
        return (
            f"{self.name.upper()}\n"
            f"Level {self.level}\n"
            f"Types: {self.types}\n"
            f"HP: {self.hp}\n"
        )
    
    def __repr__(self) -> str:
        return (
            f"Name: {self.name.upper()}\n"
            f"Level: {self.level}\n"
            f"Species: {self.species['name']}\n"
            f"Evolutions: {self.evolutions}\n"
            f"Types: {self.types}\n"
            f"Weaknesses: {self.weaknesses}\n"
            f"Moves:\n" + '\n'.join([f"\t{str(move)}" for move in self.moves]) + "\n"  
            f"HP: {self.hp}\n"
            f"Base Damage: {self.base_dmg}\n"
        )
    

class TrainedPokemon(Pokemon):
    
    """Global Variables"""
    trained_pokemons: dict[int, "TrainedPokemon"] = {}
    unique_id_counter = 0

    def __init__(self, id=-1, trainer_id=-1, name="default", level=1, species="default", evolutions=[], types=[], weaknesses=[], moves=[], hp=Pokemon.HitPoints(), base_dmg=Pokemon.BaseDamage()) -> None:
        super().__init__(name, level, species, evolutions, types, weaknesses, moves, hp, base_dmg)
        self._id = id
        self.trainer_id = trainer_id

    
    @classmethod 
    def create_trained_pokemon(cls, pokemon: Pokemon, trainer_id: int) -> "TrainedPokemon":
        """Converts a Pokemon object to a TrainedPokemon object"""

        trained_pokemon = cls(
            name = pokemon.name,
            level = pokemon.level,
            species = pokemon.species,
            evolutions = pokemon.evolutions,
            types = pokemon.types,
            weaknesses = pokemon.weaknesses,
            moves = pokemon.moves,
            hp = pokemon.hp,
            base_dmg = pokemon.base_dmg
        )

        trained_pokemon._id = cls.unique_id_counter + 1
        trained_pokemon.trainer_id = trainer_id
        cls.add_to_trained_pokemons(trained_pokemon)

        return trained_pokemon


    @classmethod
    def add_to_trained_pokemons(cls, trained_pokemon: "TrainedPokemon") -> None:
        if trained_pokemon._id > cls.unique_id_counter:
            cls.unique_id_counter = trained_pokemon._id
        cls.trained_pokemons[trained_pokemon._id] = trained_pokemon
    

    @classmethod
    def get_pokemon_by_id(cls, id: int) -> "TrainedPokemon":
        return cls.trained_pokemons[id]
    
    

if __name__ == "__main__":
    main()