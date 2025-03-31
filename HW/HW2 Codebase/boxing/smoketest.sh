#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Boxer Management
#
##########################################################

create_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Creating boxer: $name"
  response=$(curl -s -X POST "$BASE_URL/create-boxer" -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\", \"weight\": $weight, \"height\": $height, \"reach\": $reach, \"age\": $age}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer '$name' created."
  else
    echo "Failed to create boxer '$name'."
    print_json "$response"
    exit 1
  fi
}

delete_boxer_by_id() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID ($boxer_id)."
  else
    echo "Failed to delete boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxers() {
  echo "Getting all boxers in the database..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxers."
    exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1

  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (ID $boxer_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_name() {
  name=$1

  echo "Getting song by compound key (Artist: '$artist', Title: '$title', Year: $year)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name?name=$(echo $name | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name."
    exit 1
  fi
}

get_weight_class() {
  weight=$1

  echo "Getting weight class for (Weight: '$weight')..."
  response=$(curl -s -X POST "$BASE_URL/get-weight-class/$weight")
  echo "$response" | grep -q '"status": "success"'; then
      echo "Weight class received successfully."
      if [ "$ECHO_JSON" = true ]; then
        echo "Boxer JSON:"
        echo "$response" | jq .
      fi
    else
      echo "Failed to find weight class."
      exit 1
    fi
  }

update_boxer_stats() {
  boxer_id=$1
  result=$2

  echo "Updating boxer stats for (ID: '$boxer_id', result: '$result')..."
  response=$(curl -s -X POST "$BASE_URL/update-boxer-stats" \
    -H "Content-Type: application/json" \
    -d "{\"boxer_id\": \"$boxer_id\", \"result\": \"$result}")
  echo "$response" | grep -q '"status": "success"'; then
      echo "Boxer stats updated successfully."
      if [ "$ECHO_JSON" = true ]; then
        echo "Boxer JSON:"
        echo "$response" | jq .
      fi
    else
      echo "Failed to update boxer stats."
      exit 1
    fi
  }

############################################################
#
# Ring Management
#
############################################################

enter_ring() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Adding boxer to ring: $name..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer added to ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add boxer to ring."
    exit 1
  fi
}

get_fighting_skill() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Getting fighting skill of boxer: $name..."
  response=$(curl -s -X POST "$BASE_URL/get-fighting-skill" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Received boxer's fighting skill successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer's fighting skill."
    exit 1
  fi
}

clear_ring() {
  echo "Clearing ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-ring")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully."
  else
    echo "Failed to clear ring."
    exit 1
  fi
}





############################################################
#
# Simulate Fight
#
############################################################

fight() {
  echo "Initiating fight..."
  response=$(curl -s -X POST "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Fight concluded successfully"
  else
    echo "Failed to process fight."
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

# Function to get the song leaderboard sorted by play count
get_song_leaderboard() {
  echo "Getting song leaderboard sorted by play count..."
  response=$(curl -s -X GET "$BASE_URL/song-leaderboard?sort=play_count")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by play count):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get song leaderboard."
    exit 1
  fi
}

# Initialize the database
sqlite3 db/playlist.db < sql/init_db.sql

# Health checks
check_health
check_db

# Create songs
create_song "The Beatles" "Hey Jude" 1968 "Rock" 180
create_song "The Rolling Stones" "Paint It Black" 1966 "Rock" 180
create_song "The Beatles" "Let It Be" 1970 "Rock" 180
create_song "Queen" "Bohemian Rhapsody" 1975 "Rock" 180
create_song "Led Zeppelin" "Stairway to Heaven" 1971 "Rock" 180

delete_song_by_id 1
get_all_songs

get_song_by_id 2
get_song_by_compound_key "The Beatles" "Let It Be" 1970
get_random_song

add_song_to_playlist "The Rolling Stones" "Paint It Black" 1966
add_song_to_playlist "Queen" "Bohemian Rhapsody" 1975
add_song_to_playlist "Led Zeppelin" "Stairway to Heaven" 1971
add_song_to_playlist "The Beatles" "Let It Be" 1970

remove_song_from_playlist "The Beatles" "Let It Be" 1970
remove_song_by_track_number 2

get_all_songs_from_playlist
get_random_song_from_playlist

add_song_to_playlist "Queen" "Bohemian Rhapsody" 1975
add_song_to_playlist "The Beatles" "Let It Be" 1970

move_song_to_beginning "The Beatles" "Let It Be" 1970
move_song_to_end "Queen" "Bohemian Rhapsody" 1975
move_song_to_track_number "Led Zeppelin" "Stairway to Heaven" 1971 2
swap_songs_in_playlist 1 2

get_all_songs_from_playlist
get_song_from_playlist_by_track_number 1

get_playlist_length_duration

play_current_song
rewind_playlist

play_entire_playlist
play_current_song
go-go_to_random_track
play_rest_of_playlist

get_song_leaderboard

echo "All tests passed successfully!"
