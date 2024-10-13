import pytest
from unittest.mock import patch
from .project import check_int_input, game_menu, auth_menu
from .game_classes import Trainer

def test_check_int_input():
    assert check_int_input("1", 1, 3) is True
    assert check_int_input("3", 1, 3) is True
    assert check_int_input("2", 1, 4) is True

    assert check_int_input("0", 1, 3) is False
    assert check_int_input("5", 1, 4) is False
    
    assert check_int_input("a", 1, 3) is False
    assert check_int_input("!", 1, 3) is False

def test_game_menu():
    # Create a mock Trainer object
    trainer = Trainer(username="TestUsername", password="TestPassword")

    with patch('builtins.input', side_effect=["1"]): 
        choice = game_menu(trainer)
        assert choice == 1  

    with patch('builtins.input', side_effect=["2"]): 
        choice = game_menu(trainer)
        assert choice == 2  

    # Test for a logged-out user
    with patch('builtins.input', side_effect=["1"]):
        choice = game_menu(None)  
        assert choice == -1  

def test_auth_menu():
    with patch('builtins.input', side_effect=["1"]):
        assert auth_menu() == 1

    with patch('builtins.input', side_effect=["2"]):
        assert auth_menu() == 2

    with patch('builtins.input', side_effect=["3"]):
        assert auth_menu() == 3