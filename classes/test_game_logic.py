import pytest
from unittest.mock import MagicMock, patch
from .player import Player, AIAbstraction
from .game import MafiaGame
from .roles import Alignment, TOWN, MAFIA, JESTER

@pytest.fixture
def mock_abstractor():
    abstractor = MagicMock()
    abstractor.bot = MagicMock()
    return abstractor

@pytest.fixture
def mock_scheduler():
    return MagicMock()

@pytest.fixture
def game(mock_abstractor, mock_scheduler):
    with patch("classes.game.AsyncOpenAI"):
        config = MagicMock()
        return MafiaGame(mock_abstractor, mock_scheduler, config)

def test_player_initialization():
    ai = AIAbstraction("gpt-4", "AI Player", "http://avatar.url")
    assert ai.name == "AI Player"
    assert ai.model == "gpt-4"
    assert ai.id == -1
    
    player = ai.player
    assert player.user == ai
    assert player.name == "AI Player"
    assert player.alive is True
    assert player.role is None

def test_get_alive_players(game):
    p1 = Player(AIAbstraction("m1", "P1"))
    p2 = Player(AIAbstraction("m2", "P2"))
    p3 = Player(AIAbstraction("m3", "P3"))
    
    game.players = [p1, p2, p3]
    assert len(game.get_alive_players()) == 3
    
    p2.alive = False
    alive = game.get_alive_players()
    assert len(alive) == 2
    assert p1 in alive
    assert p3 in alive
    assert p2 not in alive

def test_is_game_over_not_running(game):
    game.running = False
    assert game.is_game_over() == "No one"

def test_is_game_over_town_wins(game):
    game.running = True
    p1 = Player(AIAbstraction("m1", "Townie"))
    p1.role = TOWN
    p2 = Player(AIAbstraction("m2", "Dead Mafia"))
    p2.role = MAFIA
    p2.alive = False
    
    game.players = [p1, p2]
    assert game.is_game_over() == "Town"

def test_is_game_over_mafia_wins(game):
    game.running = True
    p1 = Player(AIAbstraction("m1", "Townie"))
    p1.role = TOWN
    p2 = Player(AIAbstraction("m2", "Mafia"))
    p2.role = MAFIA
    
    game.players = [p1, p2]
    # Mafia >= Town (1 >= 1)
    assert game.is_game_over() == "Mafia"

def test_is_game_over_jester_wins(game):
    game.running = True
    p1 = Player(AIAbstraction("m1", "Jester"))
    p1.role = JESTER
    
    # Mock jester win condition
    with patch.object(JESTER, "win_condition", return_value=True):
        game.players = [p1]
        assert game.is_game_over() == "Jester"

def test_is_game_over_still_going(game):
    game.running = True
    p1 = Player(AIAbstraction("m1", "T1"))
    p1.role = TOWN
    p2 = Player(AIAbstraction("m2", "T2"))
    p2.role = TOWN
    p3 = Player(AIAbstraction("m3", "M1"))
    p3.role = MAFIA
    
    game.players = [p1, p2, p3]
    # 1 Mafia, 2 Town. 1 < 2.
    assert game.is_game_over() is False
