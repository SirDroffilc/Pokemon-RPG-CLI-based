# PokeRPG (CLI)

#### Video Demo

#### Description:

**PokeRPG** is a command-line based Pokémon RPG that integrates with the PokeAPI. In this game, players take on the role of Pokémon Trainers, allowing them to catch Pokémon, engage in battles, level up their Pokémon, evolve and train them, and challenge Gym Leaders.

## Key Features

### 1. PokeAPI

- This project uses the PokeAPI to retrieve the necessary information about all the pokemons to be used in this project.
- The 'requests' module is used for communicating with the API

### 2. User Authentication

- Users can sign up for a new account.
- Users can log in an existing account.
- Usernames have a fixed number of minimum and maximum characters. Usernames should be unique to every user. Sign up will be rejected if the username is already taken
- Passwords have a fixed number of minimum and maximum characters.
- This is a simple project, passwords are NOT hashed, so do not put similar passwords from your external online accounts.

### 3. Pokemon Battles

- Trainers can use their own pokemons to battle other wild pokemons or trained pokemons by Gym Leaders.
- In each pokemon battle, a trainer can choose which move of their pokemon to use.
- Each move varies in power, and the actual damage is dependent on this move power and the current base damage of the pokemon (scales with level)
- Types are also considered when inflicting damage. Each type may be weak or strong to another type.

### 4. Pokemon Training and Evolution

- Trainers can train their pokemons to increase their level. HP and Base Damage of each Pokemon scales with level.
- Trainers can choose to evolve their pokemons after reaching certain levels.
- A pokemon cannot evolve until they reach the required level.

### 5. Catch Wild Pokemons

- Trainers can explore maps wherein each map is unique to a specific pokemon type (fire, grass, water)
- Trainers can choose to battle a wild pokemon in order to catch it and train it as their own pokemon.
- Each trainer is limited to only 6 pokemons.

### 6. Choose Starter Pokemon

- When a user is newly signed-up, they will choose a starter pokemon, either a Charmander, Bulbasaur, or a Squirtle.
- This will be their first Pokemon to train in the game.

### 7. File Handling

- .csv and .txt files are used as makeshift databases
- All the registered Users/Trainers are saved to a CSV file 'trainers.csv'
- All trained pokemons owned by each Trainer are saved to a CSV file 'trained_pokemons.csv'
- All wild pokemons are saved to .txt files, respectively according to their pokemon type

### 8. Object-Oriented Programming

- This project is focused on implementing object-oriented programming.
- class 'Trainer' contains all code related to the users/trainers
- class 'Pokemon' contains all code related to pokemons
- class 'TrainedPokemon' inherits from class 'Pokemon' and extends attributes, class methods, and instances for Pokemons that are owned and trained by Trainer objects
- class 'Battle' contains all code related to pokemon battles, whether trainer-to-wild pokemon battles or trainer-to-trainer battles

### 9. Pretty-Print

- This game uses pyfiglet module, a module that pretty-prints text in the console by using ASCII art

## Installation Instructions

### 1. Clone the repository

- > git clone https://github.com/SirDroffilc/Pokemon-RPG-CLI-based.git

### 2. Install dependencies

- > pip install -r requirements.txt

### 3. Run

- Run 'project.py' to start the game

## Developer

### Ford Torion

- GitHub: https://github.com/SirDroffilc
- LinkedIn: https://www.linkedin.com/in/ford-torion/
