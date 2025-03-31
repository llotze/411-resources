from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_boxer_by_id,
    get_boxer_by_name,
    update_boxer_stats,
    get_weight_class,
    get_leaderboard
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################


def test_create_boxer_success(mock_cursor):
    """Test creating a new boxer.

    """
    create_boxer("Ali", 180, 72, 74.0, 30)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Ali", 180, 72, 74.4, 30)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_boxer_duplicate_name(mock_cursor):
    """Test creating a duplicate boxer, should raise an error).

    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = [None, sqlite3.IntegrityError("UNIQUE constraint failed")]

    with pytest.raises(ValueError, match="Boxer with name 'Ali' already exists"):
        create_boxer("Ali", 180, 72, 74.0, 30)


def test_create_boxer_invalid_inputs():
    """Test error when trying to create a boxer with an invalid input (e.g., negative weight)

    """
    with pytest.raises(ValueError):
        create_boxer("Ali", 100, 72, 74.0, 30)  # Invalid weight
    with pytest.raises(ValueError):
        create_boxer("Ali", 180, 0, 74.0, 30)   # Invalid height
    with pytest.raises(ValueError):
        create_boxer("Ali", 180, 72, 0, 30)     # Invalid reach
    with pytest.raises(ValueError):
        create_boxer("Ali", 180, 72, 74.0, 17)  # Invalid age


def test_delete_song(mock_cursor):
    """Test deleting a boxer from the catalog by boxer ID.

    """
    # Simulate the existence of a boxer w/ id=1
    # We can use any value other than None
    mock_cursor.fetchone.return_value = (True)
    boxer_id = 1
    delete_boxer(boxer_id)


    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Grab the actual SQL statements used
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "SELECT query does not match expected."
    assert actual_delete_sql == expected_delete_sql, "DELETE query does not match expected."

    # Check arguments used in the SQL
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == (boxer_id,), f"Expected SELECT args {(boxer_id,)}, got {actual_select_args}"
    assert actual_delete_args == (boxer_id,), f"Expected DELETE args {(boxer_id,)}, got {actual_delete_args}"


def test_delete_boxer_not_found(mock_cursor):
    """Test error when trying to delete a non-existent song.

    """
    # Simulate that no boxer exists with the given ID
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        delete_boxer(999)


######################################################
#
#    Get Boxer
#
######################################################


def test_get_boxer_by_id_success(mock_cursor):
    """Test getting a boxer by id.

    """
    mock_cursor.fetchone.return_value = (1, "Ali", 180, 72, 74.0, 30)

    result = get_boxer_by_id(1)
    assert result == Boxer(id=1, name="Ali", weight=180, height=72, reach=74.0, age=30)
    assert result.weight_class == "LIGHTWEIGHT"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query

    assert mock_cursor.execute.call_args[0][1] == (1,)

def test_get_boxer_by_id_not_found(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 123 not found."):
        get_boxer_by_id(123)


def test_get_boxer_by_name_success(mock_cursor):
    """Test getting a boxer by name.

    """
    mock_cursor.fetchone.return_value = (1, "Ali", 180, 72, 74.0, 30)

    result = get_boxer_by_name("Ali")
    assert result == Boxer(id=1, name="Ali", weight=180, height=72, reach=74.0, age=30)

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query

    assert mock_cursor.execute.call_args[0][1] == ("Ali",)

def test_get_boxer_by_name_not_found(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer 'Ali' not found."):
        get_boxer_by_name("Ali")


def test_get_all_boxers(mock_cursor):
    """Test retrieving all boxers.

    """
    mock_cursor.fetchall.return_value = [
        (1, "Ali", 180, 72, 74.0, 30, 10, 9, 0.9),
        (2, "Tyson", 220, 70, 76.0, 28, 8, 7, 0.875),
        (3, "Holyfield", 200, 74, 78.0, 32, 9, 5, 0.555)
    ]

    result = get_leaderboard()  

    expected_result = [
        {
            'id': 1, 'name': 'Ali', 'weight': 180, 'height': 72, 'reach': 74.0, 'age': 30,
            'weight_class': 'MIDDLEWEIGHT', 'fights': 10, 'wins': 9, 'win_pct': 90.0
        },
        {
            'id': 2, 'name': 'Tyson', 'weight': 220, 'height': 70, 'reach': 76.0, 'age': 28,
            'weight_class': 'HEAVYWEIGHT', 'fights': 8, 'wins': 7, 'win_pct': 87.5
        },
        {
            'id': 3, 'name': 'Holyfield', 'weight': 200, 'height': 74, 'reach': 78.0, 'age': 32,
            'weight_class': 'MIDDLEWEIGHT', 'fights': 9, 'wins': 5, 'win_pct': 55.5
        }
    ]

    assert result == expected_result, f"Expected {expected_result}, but got {result}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query

def test_get_all_boxers_empty_catalog(mock_cursor, caplog):
    """Test that retrieving all boxers returns an empty list when none exist.

    """
    mock_cursor.fetchall.return_value = []

    result = get_leaderboard()

    assert result == []

    assert "Successfully fetched leaderboard with 0 entries" in caplog.text

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query

def test_get_boxers_ordered_by_win_pct(mock_cursor):
    """Test retrieving boxers ordered by win percentage.

    """
    mock_cursor.fetchall.return_value = [
        (2, "Tyson", 220, 70, 76.0, 28, 8, 7, 0.875),
        (1, "Ali", 180, 72, 74.0, 30, 10, 9, 0.9),
        (3, "Holyfield", 200, 74, 78.0, 32, 9, 5, 0.555)
    ]

    result = get_leaderboard(sort_by="win_pct")
    expected_result = [
        {
            'id': 1, 'name': 'Ali', 'weight': 180, 'height': 72, 'reach': 74.0, 'age': 30,
            'weight_class': 'MIDDLEWEIGHT', 'fights': 10, 'wins': 9, 'win_pct': 90.0
        },
        {
            'id': 2, 'name': 'Tyson', 'weight': 220, 'height': 70, 'reach': 76.0, 'age': 28,
            'weight_class': 'HEAVYWEIGHT', 'fights': 8, 'wins': 7, 'win_pct': 87.5
        },
        {
            'id': 3, 'name': 'Holyfield', 'weight': 200, 'height': 74, 'reach': 78.0, 'age': 32,
            'weight_class': 'MIDDLEWEIGHT', 'fights': 9, 'wins': 5, 'win_pct': 55.5
        }
    ]

    assert result == expected_result

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY win_pct DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query




######################################################
#
#    Boxer Stats
#
######################################################


def test_update_boxer_stats_win(mock_cursor):
    "Tests updating a boxers win stat"
    mock_cursor.fetchone.return_value = (1,)
    update_boxer_stats(1, "win")

    update_sql = normalize_whitespace("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_query == update_sql

def test_update_boxer_stats_loss(mock_cursor):
    "Tests updating a boxers loss stat"
    mock_cursor.fetchone.return_value = (1,)
    update_boxer_stats(1, "loss")

    update_sql = normalize_whitespace("UPDATE boxers SET fights = fights + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_query == update_sql

def test_update_boxer_stats_invalid_result():
    "Tests invalid result ending in a draw"
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_boxer_stats(1, "draw")

def test_update_boxer_stats_missing_boxer(mock_cursor):
    "Testing trying to add stats to a nonexistent boxer"
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Boxer with ID 1 not found."):
        update_boxer_stats(1, "win")