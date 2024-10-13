import pytest
from unittest.mock import patch
from .project import check_int_input, game_menu, auth_menu
from .game_classes import Trainer, Pokemon, TrainedPokemon, Battle

def test_check_int_input():
    assert check_int_input("1", 1, 3) is True
    assert check_int_input("3", 1, 3) is True
    assert check_int_input("2", 1, 4) is True

    assert check_int_input("0", 1, 3) is False
    assert check_int_input("5", 1, 4) is False
    
    assert check_int_input("a", 1, 3) is False
    assert check_int_input("!", 1, 3) is False
