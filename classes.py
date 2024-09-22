import csv
import json
import os
import random
import requests
from sortedcontainers import SortedSet
import time


def main() -> None:
    Trainer.retrieve()
    Pokemon.retrieve()
    TrainedPokemon.retrieve_trained_pokemons()

    Trainer.log_in()
    trainer = Trainer.current_user
    # starter_pokemon = Pokemon.create_pokemon_from_name("squirtle")
    # starter_pokemon.level = 2
    # starter_pokemon.hp.update_base_hp(2, starter_pokemon.get_evolution_chain_position())
    # starter_pokemon.base_dmg.update_base_dmg(2, starter_pokemon.get_evolution_chain_position())
    # starter_pokemon.hp.current = round(0.3 * starter_pokemon.hp.base)
    # trainer.catch_and_train_pokemon(starter_pokemon)

    trained_pokemon = TrainedPokemon.get_pokemon_by_id(2)
    trained_pokemon.evolve()
    trained_pokemon.train()

    
    TrainedPokemon.save_trained_pokemons()
    Trainer.save()

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
        print("ALL TRAINERS")
        for i, trainer in enumerate(cls.trainers):
            print(f"{i+1}.) {trainer}")
        input("Press enter to continue...")

    
    """Instance Methods"""
    def catch_and_train_pokemon(self, pokemon: "Pokemon") -> bool:
        """Catches a Pokemon object, converts it into a TrainedPokemon object, and adds the id to self.pokemons"""

        if self.pokeballs_count <= 0:
            print(f"No Poke Balls left to catch this pokemon.")
            return
        
        if pokemon.hp.current > (0.4 * pokemon.hp.base):
            print(f"{pokemon.name.capitalize()} got out of the Poke Ball. Catching failed!")
            print(f"Try weakening {pokemon.name.capitalize()} first!\n")
            return False
        
        trained_pokemon = TrainedPokemon.create_trained_pokemon(pokemon, self._id)
        self.pokemons.append(trained_pokemon._id)
        self.pokeballs_count -= 1
        return True
    
    def evolve_pokemon(self, pokemon: "TrainedPokemon") -> None:
        """TO DO"""

        pokemon.evolve()
        ...

    
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
            return f"\t- {self.name} | Type: {self.type}"
        
        def __repr__(self) -> str:
            return f"- {self.name} | Type: {self.type} | Power: {self.power}"
        
    class HitPoints:
        def __init__(self, base=50, current=50) -> None:
            self.base = base
            self.current = current

        def update_base_hp(self, level: int, evolution_chain_position: int):
            base_hp = 50 * (level + evolution_chain_position)
            self.base = base_hp
            self.current = base_hp

        def __str__(self) -> str:
            return f"{self.current}/{self.base}"
    
    class BaseDamage:
        def __init__(self, dmg=10) -> None:
            self.dmg = dmg
        
        def update_base_dmg(self, level: int, evolution_chain_position: int):
            base_dmg = 10  * (level + evolution_chain_position)
            self.dmg = base_dmg

        
        
        def __str__(self) -> str:
            return f"{self.dmg}"


    """Class Variables"""
    wild_fire_pokemons = []
    wild_grass_pokemons = []
    wild_water_pokemons = []
    poketypes = ["fire", "grass", "water"]
    strength_to_weakness_map = {"fire": "water", "grass": "fire", "water": "grass"}


    def __init__(self, name="default", level=1, species={}, evolutions=[], types=[], weaknesses=[], moves=[], hp=None, base_dmg=None)-> None:
        self.name = name
        self.level = level
        self.species = species # a dict with keys "name" and "url"
        self.evolutions = evolutions
        self.types = types
        self.weaknesses = weaknesses
        self.moves = moves # list of Move objects
        self.hp = hp if hp is not None else Pokemon.HitPoints()
        self.base_dmg = base_dmg if base_dmg is not None else Pokemon.BaseDamage()
        self.is_awake = True

    
    @classmethod
    def create_pokemon_from_name(cls, pokemon_name: str) -> "Pokemon":
        """Creates a Pokemon Object from a string (pokemon_name) using PokeAPI"""
        """Always check if returned value is valid"""

        print("Loading Pokemon... ")

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
        pokemon.moves = pokemon.get_moves(pokemon_data["moves"])
        pokemon.hp.update_base_hp(pokemon.level, pokemon.get_evolution_chain_position())
        pokemon.base_dmg.update_base_dmg(pokemon.level, pokemon.get_evolution_chain_position())

        if not pokemon.evolutions or not pokemon.weaknesses or not pokemon.moves:
            print(f"Create Pokemon Error. Evolutions/Weaknesses/Moves assignment failed.")
            return None

        return pokemon
    
    @classmethod
    def generate_random_wild_pokemon(cls, poketype) -> "Pokemon":
        """Returns a random, low-level, catchable, wild pokemon of type 'poketype'"""

        if poketype not in cls.poketypes:
            print("Generate Random Wild Pokemon failed. Type not supported.")
            return None
        
        pokemon_name = ""
        match poketype:
            case "fire":
                pokemon_name = random.choice(cls.wild_fire_pokemons)
            case "grass":
                pokemon_name = random.choice(cls.wild_grass_pokemons)
            case "water":
                pokemon_name = random.choice(cls.wild_water_pokemons)
            case _:
                return None
            
        pokemon = cls.create_pokemon_from_name(pokemon_name)
        if not pokemon:
            return None
        
        pokemon.level = random.randint(1, 3)
        pokemon.hp.update_base_hp(pokemon.level, pokemon.get_evolution_chain_position())
        pokemon.base_dmg.update_base_dmg(pokemon.level, pokemon.get_evolution_chain_position())

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
        
        weaknesses = []
        for poketype in types:
            if poketype in Pokemon.strength_to_weakness_map.keys():
                weaknesses.append(Pokemon.strength_to_weakness_map[poketype])
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
    
    def state(self) -> str:
        return "Awake" if self.is_awake else "Fainted"

    def update_is_awake(self) -> None:
        self.is_awake = False if self.hp.current <= 0 else True
    
    def get_evolution_chain_position(self):
        for i, evolution in enumerate(self.evolutions):
            if evolution == self.name:
                return i
        

    def __str__(self) -> str:
        return (
            f"  {self.name.upper()}\n"
            f"\tLevel {self.level}\n"
            f"\tTypes: {self.types}\n"
            f"\tHP: {self.hp}\n"
            f"\tBase Damage: {self.base_dmg.dmg}\n"
            f"\tMoves:\n" + '\n'.join([f"  {str(move)}" for move in self.moves]) + "\n" 
        )
    
    def __repr__(self) -> str:
        return (
            f"Name: {self.name.upper()}\n"
            f"Level: {self.level}\n"
            f"Species: {self.species['name']}\n"
            f"Evolutions: {self.evolutions}\n"
            f"Types: {self.types}\n"
            f"Weaknesses: {self.weaknesses}\n"
            f"Moves:\n" + '\n'.join([f"\t{repr(move)}" for move in self.moves]) + "\n"  
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

    
    """Class Methods"""
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
    

    @classmethod
    def save_trained_pokemons(cls) -> None:
        with open("database/all_pokemons/trained_pokemons.csv", "w", newline="") as file:
            fieldnames = ["id", "trainer_id", "name", "level", "species", "evolutions", "types", "weaknesses", "moves", "hp", "base_dmg"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for pokemon in cls.trained_pokemons.values():
                writer.writerow({
                    "id": pokemon._id,
                    "trainer_id": pokemon.trainer_id,
                    "name": pokemon.name,
                    "level": pokemon.level,
                    "species": json.dumps(pokemon.species),
                    "evolutions": json.dumps(pokemon.evolutions), 
                    "types": json.dumps(pokemon.types),
                    "weaknesses": json.dumps(pokemon.weaknesses),
                    "moves": json.dumps([move.__dict__ for move in pokemon.moves]),
                    "hp": json.dumps(pokemon.hp.__dict__),
                    "base_dmg": json.dumps(pokemon.base_dmg.__dict__)
                })

    @classmethod
    def retrieve_trained_pokemons(cls):
        with open("database/all_pokemons/trained_pokemons.csv", "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader: # each row is a TrainedPokemon object
                moves = [Pokemon.Move(**move) for move in json.loads(row["moves"])]
                hp = Pokemon.HitPoints(**json.loads(row["hp"]))
                base_dmg = Pokemon.BaseDamage(**json.loads(row["base_dmg"]))

                trained_pokemon = cls(
                    id = int(row["id"]),
                    trainer_id = int(row["trainer_id"]),
                    name = row["name"],
                    level = int(row["level"]),
                    species = json.loads(row["species"]),
                    evolutions = json.loads(row["evolutions"]),
                    types = json.loads(row["types"]),
                    weaknesses = json.loads(row["weaknesses"]),
                    moves = moves,
                    hp = hp,
                    base_dmg = base_dmg
                )
                cls.add_to_trained_pokemons(trained_pokemon)

    @classmethod
    def display_trained_pokemons(cls):
        os.system("cls")
        print("ALL TRAINED POKEMONS")
        for _id, pokemon in cls.trained_pokemons.items():
            print(f"#{_id}")
            print(repr(pokemon))


    """Instance Methods"""

    def evolve(self) -> bool:
        chain_position = self.get_evolution_chain_position()

        if chain_position == len(self.evolutions) - 1: # if last evolution
            print("Cannot evolve further")
            return False
        
        next_chain_position = chain_position + 1
        
        print(f"Next Evolution: {self.evolutions[next_chain_position].capitalize()}")
        required_level = 1 + (3 * next_chain_position)
        print(f"Required Level: {required_level}")

        if self.level < required_level:
            print("Current level too low. Train Pokemon first. It must be at least the required level.\n")
            return False
        
        prev_name = self.name.capitalize()
        prev_hp = self.hp.base
        prev_base_dmg = self.base_dmg.dmg
        
        next_evolution_pokemon= Pokemon.create_pokemon_from_name(self.evolutions[chain_position+1])

        self.name = next_evolution_pokemon.name
        self.species = next_evolution_pokemon.species
        self.types = next_evolution_pokemon.types
        self.weaknesses = next_evolution_pokemon.weaknesses
        self.moves = next_evolution_pokemon.moves

        # Bonus HP and Damage for evolving
        self.hp.update_base_hp(self.level, next_chain_position)
        self.base_dmg.update_base_dmg(self.level, next_chain_position)

        print(f"{prev_name} evolved to {self.name.capitalize()}.")
        print(f"HP: {prev_hp} -> {self.hp.base} | Base Damage: {prev_base_dmg} -> {self.base_dmg.dmg}\n")

        return True


    def train(self) -> None:
        """Trains a TrainedPokemon object. Generates a random enemy pokemon. TrainedPokemon will level up if it achieves total victory over the random enemy pokemon"""
        poketype = random.choice(Pokemon.poketypes)
        random_pokemon = Pokemon.generate_random_wild_pokemon(poketype)
        
        close_gap_level = self.level + random.randint(-2, 2)
        random_pokemon.level = min(max(close_gap_level, 1), 10)

        random_pokemon.hp.update_base_hp(random_pokemon.level, random_pokemon.get_evolution_chain_position())
        random_pokemon.base_dmg.update_base_dmg(random_pokemon.level, random_pokemon.get_evolution_chain_position())

        Battle.reset_hp(self)
        Battle.reset_hp(random_pokemon)
        total_victory = Battle.initiate_pokemon_battle(self, random_pokemon)

        if total_victory:
            level_gap = random_pokemon.level - self.level
            self.level_up(level_gap)
            
        else:
            print(f"{self.name.capitalize()} lost. Try again!")


    def level_up(self, level_gap=0):
        """Levels up a TrainedPokemon object based on level_gap between the pokemon and its enemy"""
        os.system("cls")
        if self.level == 10:
            print(f"{self.name.capitalize()} reached the maximum level.")
            return
        
        prev_hp = self.hp.base
        prev_base_dmg = self.base_dmg.dmg

        if level_gap > 1:
            self.level += 2 
        else:
            self.level += 1
        
        self.hp.update_base_hp(self.level, self.get_evolution_chain_position())
        self.base_dmg.update_base_dmg(self.level, self.get_evolution_chain_position())
        print(f"Leveled up! {self.name.capitalize()} reached level {self.level}.")
        print(f"HP: {prev_hp} -> {self.hp.base} | Base Damage: {prev_base_dmg} -> {self.base_dmg.dmg}\n")


    def __repr__(self) -> str:
        return (
            f"Name: {self.name.upper()}\n"
            f"ID: {self._id}\n"
            f"Trainer ID: {self.trainer_id}\n"
            f"Level: {self.level}\n"
            f"Species: {self.species['name']}\n"
            f"Evolutions: {self.evolutions}\n"
            f"Types: {self.types}\n"
            f"Weaknesses: {self.weaknesses}\n"
            f"Moves:\n" + '\n'.join([f"{repr(move)}" for move in self.moves]) + "\n"  
            f"HP: {self.hp}\n"
            f"Base Damage: {self.base_dmg}\n"
        )


class Battle:

    @classmethod
    def trainer_to_wild_battle(cls, trainer : Trainer, wild_pokemon: Pokemon) -> None:
        victory = False
        cls.reset_all_hp(trainer.pokemons)
        while(True):
            if cls.trainer_pokemons_all_fainted(trainer.pokemons):
                victory = False
                break
            if not wild_pokemon.is_awake:
                victory = True
                break

            current_trainer_pokemon = cls.choose_pokemon_from_team(trainer)
            catch_status= cls.initiate_pokemon_battle(current_trainer_pokemon, wild_pokemon, is_wild_battle=True)
            if catch_status == "catch_success":
                return
        
        message = "You won!" if victory else "All of your pokemons fainted. You lost!"
        print(message)


    @classmethod
    def initiate_pokemon_battle(cls, user_pokemon: Pokemon, enemy_pokemon: Pokemon, is_wild_battle=False) -> bool | str:
        """Returns True if user_pokemon won; returns False if lost; returns a string 'catch_success' if caught"""
        
        def choose_user_move(pokemon_moves: list[Pokemon.Move]) -> Pokemon.Move | str:
            while True:
                choice = input("Move Name: ").lower()
                for move in pokemon_moves:
                    if choice == move.name:
                        return move
                print("Invalid move")

        def inflict_damage(attacker: Pokemon, move: Pokemon.Move, opponent: Pokemon) -> None:
            """Reduces the opponent_pokemon.hp.current based on the move.type, move.power, opponent_pokemon.types, and opponent_pokemon.weaknesses. Damage is rounded"""

            damage = (attacker.base_dmg.dmg / 100) * move.power

            effect = "normal"
            effect_message = {
                "normal": "The attack was effective.",
                "super": "The attack was super effective",
                "ineffective": "The attack was super ineffective",
                "same": "The attack was ineffective because of similar types"
        
            }
            
            if move.type in opponent.types:
                damage *= 0.5
                effect = "same"
            elif move.type in opponent.weaknesses: 
                damage *= 2
                effect = "super"
            elif move.type == "normal":
                damage *= 1
                effect = "normal"
            elif Pokemon.strength_to_weakness_map[move.type] in opponent.types: 
                damage *= 0.25
                effect = "ineffective"
            else:
                damage *= 1
                effect = "normal"

            damage = round(damage)

            opponent.hp.current -= damage
            opponent.update_is_awake()

            print(f"\n{attacker.name.capitalize()} used {move.name} and dealt {damage}HP damage to {opponent.name.capitalize()}")
            print(effect_message[effect])
            return 

        def prompt_catch() -> bool:
            """Returns True if trainer wants to catch, else False"""
            while True:
                choice = input(f"Use a Poke Ball to catch {enemy_pokemon.name.capitalize()} (y/n): ").lower()
                if choice in ("y", "yes"):
                    print("")
                    return True
                elif choice in ("n", "no"):
                    print("")
                    return False
                else:
                    print("Invalid Input: Enter 'yes', 'no', 'y', or 'n' only.")
                    continue

        while user_pokemon.is_awake and enemy_pokemon.is_awake:
            os.system("cls")
            print("WILD POKEMON")
            print(enemy_pokemon)
            print("--------------------------------------------------")
            print("YOUR POKEMON")
            print(user_pokemon)
            
            if is_wild_battle:
                catch = prompt_catch()
                if catch:
                    catch_result = Trainer.current_user.catch_and_train_pokemon(enemy_pokemon)
                    if catch_result:
                        print(f"You have a new Pokemon! You have successfully catched {enemy_pokemon.name.capitalize()}!")
                        return "catch_success"

            user_move = choose_user_move(user_pokemon.moves)
            enemy_move = random.choice(enemy_pokemon.moves)

            os.system("cls")
            print(f"{Trainer.current_user.username}: {user_pokemon.name.capitalize()}, use {user_move.name}!")
            time.sleep(1.5)
            inflict_damage(user_pokemon, user_move, enemy_pokemon)
            inflict_damage(enemy_pokemon, enemy_move, user_pokemon)
            input("\n\nPress Enter to continue...")

        total_victory = True
        if not user_pokemon.is_awake:
            print(f"\n{user_pokemon.name.capitalize()} fainted.")
            total_victory = False
        if not enemy_pokemon.is_awake:
            print(f"\n{enemy_pokemon.name.capitalize()} fainted.")

        input("\n\nPress Enter to continue...")
        
        return total_victory
            

    @classmethod
    def reset_all_hp(cls, trainer_pokemon_ids: list[int]) -> None:
        for pokemon_id in trainer_pokemon_ids:
            pokemon = TrainedPokemon.get_pokemon_by_id(pokemon_id)
            pokemon.hp.current = pokemon.hp.base
        
    @classmethod
    def reset_hp(cls, pokemon: Pokemon) -> None:
        pokemon.hp.current = pokemon.hp.base

    @classmethod
    def choose_pokemon_from_team(cls, trainer: Trainer) -> TrainedPokemon:
        print("Choose Your Pokemon:")
        for i, pokemon_id in enumerate(trainer.pokemons):
            pokemon = TrainedPokemon.get_pokemon_by_id(pokemon_id)
            print(f"  {i+1}. {pokemon.name} | Level: {pokemon.level} | Type: {pokemon.types} | State: {pokemon.state()}")

        while(True):
            try:
                choice = int(input("Choose Pokemon Number: "))
            except ValueError:
                print("Invalid Input. Input a valid integer.")
                continue
            if 1 <= choice <= len(trainer.pokemons):
                break
            else:
                print(f"Invalid Input. Available Pokemon Numbers: 1 to {len(trainer.pokemons)}")

        chosen_pokemon_id = trainer.pokemons[choice-1]
        return TrainedPokemon.get_pokemon_by_id(chosen_pokemon_id)
            
    @classmethod
    def trainer_pokemons_all_fainted(cls, trainer_pokemon_ids: list[int]) -> bool:
        for pokemon_id in trainer_pokemon_ids:
            pokemon = TrainedPokemon.get_pokemon_by_id(pokemon_id)
            if pokemon.is_awake:
                return False
        else:
            return True

if __name__ == "__main__":
    main()