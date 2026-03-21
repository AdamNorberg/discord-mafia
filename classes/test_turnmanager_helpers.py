import pytest
import re
from .turnmanager import TurnManager
from .player import Player, AIAbstraction

class MockUser:
    def __init__(self, name, id):
        self.name = name
        self.id = id

from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_players():
    p1 = Player(AIAbstraction("gpt-4", "Alice"))
    p2 = Player(AIAbstraction("gpt-4", "Bob"))
    p3 = Player(AIAbstraction("gpt-4", "Charlie"))
    return [p1, p2, p3]

@pytest.fixture
def turn_manager():
    # We mock OpenAI and data loading to prevent side effects/errors during __init__
    import json
    models_json = json.dumps({"models": [], "avatar_template": "{}", "discussion_analyser": "gpt-4"})
    with patch("classes.turnmanager.AsyncOpenAI"), \
         patch("classes.turnmanager.data.load", return_value={"profiles": {}}), \
         patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value=models_json)))))):
        return TurnManager([], MagicMock(), MagicMock(), MagicMock())

def test_clean_ai_content(turn_manager):
    assert turn_manager._clean_ai_content("<think>some thought</think>Hello") == "Hello"
    assert turn_manager._clean_ai_content("<think>multi\nline</think> World ") == "World"
    assert turn_manager._clean_ai_content("No think tags") == "No think tags"
    assert turn_manager._clean_ai_content("<THINK>capitalized</THINK>Text") == "Text"
    assert turn_manager._clean_ai_content("<think>unclosed tag") == ""
    assert turn_manager._clean_ai_content("") == ""
    assert turn_manager._clean_ai_content(None) == ""

def test_candidate_by_name(turn_manager, mock_players):
    # Perfect match
    assert turn_manager._candidate_by_name(mock_players, "Alice") == mock_players[0]
    assert turn_manager._candidate_by_name(mock_players, "alice") == mock_players[0]
    
    # Word boundary match
    mock_players[0].name = "Alice Smith"
    assert turn_manager._candidate_by_name(mock_players, "Alice") == mock_players[0]
    
    # Substring match
    assert turn_manager._candidate_by_name(mock_players, "lice") == mock_players[0]
    
    # No match
    assert turn_manager._candidate_by_name(mock_players, "David") is None
    assert turn_manager._candidate_by_name(mock_players, "") is None
    assert turn_manager._candidate_by_name(mock_players, None) is None

def test_format_vote_details(turn_manager, mock_players):
    voter_names = {1: "User1", 2: "User2", 3: "User3"}
    votes = {1: "Alice", 2: "Alice", 3: "Bob"}
    
    expected = "- Alice: User1, User2 (2)\n- Bob: User3 (1)"
    # Note: formatting might depend on candidate order in mock_players
    result = turn_manager._format_vote_details(votes, mock_players, voter_names)
    assert result == expected

def test_format_vote_details_empty(turn_manager, mock_players):
    assert turn_manager._format_vote_details({}, mock_players, {}) == "No votes yet."

def test_format_vote_details_abstain(turn_manager, mock_players):
    voter_names = {1: "User1"}
    votes = {1: "Abstain"}
    
    # allow_abstain=True
    result = turn_manager._format_vote_details(votes, mock_players, voter_names, allow_abstain=True)
    assert result == "- Abstain: User1 (1)"
    
    # allow_abstain=False
    result = turn_manager._format_vote_details(votes, mock_players, voter_names, allow_abstain=False)
    assert result == "No votes yet."
