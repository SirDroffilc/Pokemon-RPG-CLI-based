from .game_classes import Trainer, Pokemon, TrainedPokemon, Battle
import pyfiglet
import os
import requests_cache

def main() -> None:
    Trainer.retrieve()
    Pokemon.retrieve()
    TrainedPokemon.retrieve_trained_pokemons()
    requests_cache.install_cache("pokemon_cache")

    if not Trainer.are_gym_trainers_generated():
        print("GENERATING GYM TRAINERS. PLEASE WAIT.")
        Trainer.generate_gym_trainers()
        input("Press Enter to continue...")

    os.system("cls")

    welcome_text = pyfiglet.figlet_format("Welcome to PokeRPG", font="doom")
    developer_text = pyfiglet.figlet_format("by 4rd", font="small")
    thank_you_text = pyfiglet.figlet_format("Thank you for using PokeRPG!", font="doom")

    print(welcome_text, developer_text)
    input("Press Enter to continue...")

    while True:
        choice = auth_menu()
        match choice:
            case 1:
                Trainer.log_in()
                start_game()
            case 2:
                trainer = Trainer.sign_up()
                trainer.choose_starter_pokemon()
                start_game()
            case 3:
                os.system("cls")
                print(thank_you_text)
                print(developer_text)

                break
            case _:
                continue
        
    TrainedPokemon.save_trained_pokemons()
    Trainer.save()
    
    return None


def auth_menu() -> int:
    auth_menu_text = pyfiglet.figlet_format("Log In or Sign Up", font="rectangles")
    while True:
        os.system("cls")
        print(auth_menu_text)
        print("1. Log In")
        print("2. Sign Up")
        print("3. Exit")
        choice = input("Choose an option (1-3): ")
        is_valid = check_int_input(choice, 1, 3)
        if is_valid:
            break
        else:
            input("Press Enter to continue...")
            continue

    return int(choice)

def start_game() -> None:
    trainer: Trainer = Trainer.current_user

    while(True):
        Battle.reset_all_hp_and_awake_state(trainer.pokemons)
        choice = game_menu(trainer)
        match choice:
            case 1:
                trainer.explore_maps()
            case 2:
                trainer.gym_battle()
            case 3:
                trainer.your_pokemons()
            case 4:
                Trainer.log_out()
                break
        input("Press Enter to continue...")
    return

def game_menu(current_user: Trainer) -> int:
    if not current_user:
        print("Error: User not logged in.")
        return -1
        
    game_menu_text = pyfiglet.figlet_format(f"Welcome, {current_user.username}", font="rectangles")
    while True:
        os.system("cls")
        print(game_menu_text)
        print("1. Catch a Wild Pokemon")
        print("2. Gym Battle")
        print("3. Your Pokemons")
        print("4. Log Out")
        choice = input("Choose an option (1-4): ")
        is_valid = check_int_input(choice, 1, 4)
        if is_valid:
            break
        else:
            input("Press Enter to continue...")
            continue

    return int(choice)


def check_int_input(choice, min: int, max: int) -> bool:
    if not choice.isdigit() or int(choice) < min or int(choice) > max:
        print(f"Please enter a valid integer ({min}-{max}).\n")
        return False
    else:
        return True
        


if __name__ == "__main__":
    main()