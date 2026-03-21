import pytest
from .player import Player, AIAbstraction
from .roles import TOWN, MAFIA, DOCTOR, SHERIFF, VIGILANTE, JESTER

def test_vigilante_can_act():
    p = Player(AIAbstraction("m1", "Vig"))
    p.role = VIGILANTE
    
    # Can act initially
    assert VIGILANTE.can_act(p) is True
    
    # Cannot act after shooting
    p.role_state["has_shot"] = True
    assert VIGILANTE.can_act(p) is False

def test_jester_win_condition():
    p = Player(AIAbstraction("m1", "Jester"))
    p.role = JESTER
    
    # Not won yet
    assert JESTER.win_condition(p, []) is False
    
    # Won if lynched
    p.death_reason = "lynch"
    assert JESTER.win_condition(p, []) is True
    
    # Not won if killed by mafia
    p.death_reason = "mafia"
    assert JESTER.win_condition(p, []) is False

def test_generic_role_properties():
    assert TOWN.alignment.value == "Town"
    assert MAFIA.alignment.value == "Mafia"
    assert JESTER.alignment.value == "Neutral"
    
    assert TOWN.is_special() is False
    assert DOCTOR.is_special() is True
    assert SHERIFF.is_special() is True
    assert VIGILANTE.is_special() is True
    assert MAFIA.is_special() is False # Mafia kill is handled by game, not role special action

def test_role_equality():
    from .roles.townsperson import Town
    another_town = Town()
    assert TOWN == another_town
    assert TOWN != MAFIA
    assert TOWN != "Town"
