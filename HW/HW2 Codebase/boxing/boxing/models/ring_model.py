import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to manage a ring of boxers.

    Attributes:
        ring (List[Boxer]: The list of Boxers in the ring.)

    """
    def __init__(self):
        """Initializes the RingModel with an empty list of boxers.

        """
        self.ring: List[Boxer] = []

    ##################################################
    # RingModel Management Functions
    ##################################################

    def fight(self) -> str:
        """Simulates a fight between the two boxers in the ring.

        Returns:
            winner.name (String): String of the name of the winner of the match

        Raises:
            ValueError: If there are not two boxers in the ring
        
        """
        logger.info("Attempting to begin a fight")
        if len(self.ring) < 2:
            logger.error("There were less than two boxers in the ring when starting a fight")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info(f"Boxers {boxer_1.name} and {boxer_2.name} will be fighting")
        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1
        logger.info(f"Successfully simulated match. Winner - {winner.name} Loser - {loser.name}")
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()
        logger.info(f"Match between {boxer_1.name} and {boxer_2.name} has fully concluded")
        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring.

        Clears all boxers from the ring. If the ring is already empty, logs a warning.

        """
        logger.info("Received request to clear the ring")
        try:
            if self.check_if_empty():
                pass
        except ValueError:
            logger.warning("Clearing an empty ring")

        self.ring.clear()
        logger.info("Successfully cleared the ring")

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add to the ring.

        Raises:
            TypeError: If the boxer is not a valid Boxer instance.
            ValueError: If the ring is already full.
            ValueError: If the boxer is already in the ring

        """
        logger.info("Received request to add a boxer to the ring")
        if not isinstance(boxer, Boxer):
            logger.error("Invalid type: boxer is not a valid Boxer instance")
            raise TypeError(f"Invalid type: Expected 'Boxer'")

        if len(self.ring) >= 2:
            logger.error(f"Could not add boxer {boxer.name} to the ring, ring is already full")
            raise ValueError("Ring is full, cannot add more boxers.")
        if len(self.ring) > 0:
            if self.ring[0].id == boxer.id:
                logger.error(f"boxer {boxer.name} is already in the ring, cannot add again.")
                raise ValueError(f"Boxer with ID {boxer.id} already exists in the ring")
            if len(self.ring) > 1:
                if self.ring[1].id == boxer.id:
                    logger.error(f"boxer {boxer.name} is already in the ring, cannot add again.")
                    raise ValueError(f"Boxer with ID {boxer.id} already exists in the ring")


        self.ring.append(boxer)
        logger.info(f"Successfully added boxer {boxer.name} to the ring")

    ##################################################
    # Boxer Management Functions
    ##################################################

    def get_boxers(self) -> List[Boxer]:
        """Returns a list of all boxers in the ring.

        Returns:
            List[Boxers]: A list of all boxers in the ring.

        Raises:
            ValueError: If ring is empty
        """
        self.check_if_empty()
        logger.info("Retrieving all songs in the playlist")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Retrieves the fighting skill of the inputted Boxer.
        
        Args:
            boxer (Boxer): The boxer whose skill is to be calculated

        Returns: 
            skill (int): The calculated fighting skill

        """
        logger.info(f"Received request to get fighting skill of {boxer.name}")
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.info(f"Successfully retrieved fighting skill {skill} of {boxer.name}")
        return skill

    def check_if_empty(self) -> None:
        """
        Checks if the ring is empty and raises a ValueError if it is.

        Raises:
            ValueError: If the ring is empty.

        """
        if not self.ring:
            logger.error("Ring is empty")
            raise ValueError("Ring is empty")
