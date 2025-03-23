import random
import Constant


class Sounds:
    def __init__(self):
        """
        Initializes the Sounds class by setting up sound effects and volume.

        The sound effects are mapped from the constants defined in the Constant module.
        """
        # Set the volume for the sound effects
        self.volume = Constant.SOUND_EFFECT_VOLUME

        # Initialize sound lists for different actions
        self.BUILDING_SPAWNING_SOUNDS = Constant.BUILDING_SPAWNING_SOUNDS
        self.CAPTURE_SOUNDS = Constant.CAPTURE_SOUNDS
        self.HARVESTING_ROCK_SOUNDS = Constant.HARVESTING_ROCK_SOUNDS
        self.HARVESTING_WOOD_SOUNDS = Constant.HARVESTING_WOOD_SOUNDS
        self.MOVE_SOUNDS = Constant.MOVE_SOUNDS
        self.PIECE_SPAWNING_SOUNDS = Constant.PIECE_SPAWNING_SOUNDS
        self.PURCHASE_SOUNDS = Constant.PURCHASE_SOUNDS
        self.PRAYER_RITUAL_SOUNDS = Constant.PRAYER_RITUAL_SOUNDS
        self.GENERATE_RESOURCES_SOUNDS = Constant.GENERATE_RESOURCES_SOUNDS
        self.PRAY_SOUNDS = Constant.PRAY_SOUNDS
        self.CHANGE_TURN_SOUNDS = Constant.CHANGE_TURN_SOUNDS
        self.START_GAME_SOUNDS = Constant.START_GAME_SOUNDS

        # Map sound effects to actions for easy lookup
        self.SOUNDS = {
            "spawn_building": self.BUILDING_SPAWNING_SOUNDS,
            "capture": self.CAPTURE_SOUNDS,
            "mine_stone": self.HARVESTING_ROCK_SOUNDS,
            "mine_gold": self.HARVESTING_ROCK_SOUNDS,
            "mine_wood": self.HARVESTING_WOOD_SOUNDS,
            "move": self.MOVE_SOUNDS,
            "spawn_piece": self.PIECE_SPAWNING_SOUNDS,
            "purchase": self.PURCHASE_SOUNDS,
            "ritual": self.PRAYER_RITUAL_SOUNDS,
            "create_resource": self.GENERATE_RESOURCES_SOUNDS,
            "pray": self.PRAY_SOUNDS,
            "change_turn": self.CHANGE_TURN_SOUNDS,
            "start_game": self.START_GAME_SOUNDS,
        }

    def play(self, sound_effect: str) -> None:
        """
        Plays the selected sound effect if sound effects are enabled.

        :param sound_effect: The name of the sound effect to play.
        """
        # Only play the sound if sound effects are enabled
        if Constant.SOUND_EFFECTS_ON:
            # Select a random sound from the list of available sounds
            i = random.randint(0, len(self.SOUNDS[sound_effect]) - 1)

            # Set the volume for the selected sound
            self.SOUNDS[sound_effect][i].set_volume(self.volume)

            # Play the selected sound effect
            self.SOUNDS[sound_effect][i].play()
