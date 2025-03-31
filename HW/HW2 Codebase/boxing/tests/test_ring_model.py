from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

@pytest.fixture
def mock_update_boxer_stats(mocker):
    """Mock the update_boxer_stats function for testing purposes."""
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")

"""Fixtures providing sample boxers for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer('Boxer 1', 150, 60, 12.5, 87)

@pytest.fixture
def sample_boxer2():
    return Boxer('Boxer 2', 200, 100, 10.2, 5)

def sample_boxer3():
    return Boxer('Boxer 3', 300, 200, 4.1, 2)

@pytest.fixture
def sample_ring(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]


##################################################
# Add / Remove Boxer Management Test Cases
##################################################


def test_enter_ring(ring_model, sample_boxer1):
    """Test adding a boxer to the ring.

    """
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == 'Boxer 1'


def test_add_duplicate_boxer_to_ring(ring_model, sample_boxer1):
    """Test error when adding a duplicate boxer to the ring by ID.

    """
    ring_model.enter_ring(sample_boxer1)
    with pytest.raises(ValueError, match="Boxer with ID 1 already exists in the ring"):
        ring_model.enter_ring(sample_boxer1)


def test_add_bad_boxer_to_ring(ring_model, sample_boxer1):
    """Test error when adding a duplicate boxer to the ring.

    """
    with pytest.raises(TypeError, match=f"Invalid type: Expected 'Boxer', got {type(asdict(sample_boxer1)).__name__}"):
        ring_model.enter_ring(asdict(sample_boxer1))

def test_add_third_boxer_to_ring(ring_model, sample_boxer1, sample_boxer2, sample_boxer3):
    """Test error when adding a third boxer to the ring.

    """
    ring.model.enter_ring(sample_boxer1)
    ring.model.enter_ring(sample_boxer2)
    with pytest.raises(TypeError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(sample_boxer3)


def test_clear_ring(ring_model, sample_boxer1, sample_boxer2):
    """Test clearing the entire ring.

    """
    ring_model.ring.append(sample_boxer1)

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "ring should be empty after clearing"

    ring_model.ring.append(sample_boxer1)
    ring_model.ring.append(sample_boxer2)
    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "ring should be empty after clearing"

##################################################
# Boxer Retrieval Test Cases
##################################################

def test_get_boxers(ring_model, sample_ring):
    """Test successfully retrieving all boxers from the ring.

    """
    ring_model.ring.extend(sample_ring)

    all_boxers = ring_model.get_boxers()
    assert len(all_boxers) == 2
    assert all_boxers[0].id == 1
    assert all_boxers[1].id == 2

def test_get_boxers_empty(ring_model):
    """Test successfully retrieving all boxers from the ring.

    """
    with pytest.raises(ValueError, match="Ring is empty"):
        ring_model.get_boxers()

def test_get_fighting_skill(ring_model, sample_boxer1):
    """Test getting the fighting skill of a boxer.

    """
    assert ring_model.get_fighing_skill(sample_boxer1) == 1050.25, "Expected fighting skill to be 1050.25"


##################################################
# Utility Function Test Cases
##################################################


def test_check_if_empty_non_empty_ring(ring_model, sample_boxer1):
    """Test check_if_empty does not raise error if ring is not empty.

    """
    ring_model.ring.append(sample_boxer1)
    try:
        ring_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty ring")


def test_check_if_empty_empty_ring(ring_model):
    """Test check_if_empty raises error when ring is empty.

    """
    ring_model.clear_ring()
    with pytest.raises(ValueError, match="Ring is empty"):
        ring_model.check_if_empty()

##################################################
# Fight Test Cases
##################################################


def test_fight_current_boxers(ring_model, sample_boxer1, sample_boxer2, mock_update_boxer_stats):
    """Test fighting the current boxers.

    """
    ring_model.ring.append(sample_boxer1)
    ring_model.ring.append(sample_boxer2)

    winner = ring_model.fight()

    # Assert that update_play_count was called with the id of the first boxer
    mock_update_boxer_stats.assert_called_once_with(1)

    assert winner == "Boxer 2", f"expected Boxer 2 to win, but got {winner}"

    # Assert that update_play_count was called with the id of the second boxer
    mock_update_boxer_stats.assert_called_with(2)

    assert sample_boxer1.wins == 0, f"Expected Boxer 1's wins to be 0, instead got {sample_boxer1.wins}"
    assert sample_boxer1.losses == 1, f"Expected Boxer 1's losses to now be 1, instead got {sample_boxer1.losses}"
    assert sample_boxer2.wins == 1, f"Expected Boxer 2's wins to now be 1, instead got {sample_boxer1.wins}"
    assert sample_boxer2.losses == 0, f"Expected Boxer 2's losses to be 0, instead got {sample_boxer1.losses}"