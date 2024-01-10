import sys

import pygame

from src.game.game_manager import GameManager
from network.client import GameClient
from game.engine import GameEngine
from game.scene_manager import SceneManager
from game.state_manager import StateManager
from utilities.input_handler import InputHandler
from utilities.event_system import EventSystem
from utilities.sprite_factory import SpriteFactory


# Initialize Pygame
pygame.init()

# Set up window size and other configurations
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Empires")
clock = pygame.time.Clock()

# Initialize the event system
event_system = EventSystem()

# Initialize the game client
client = GameClient("192.168.1.149", 5555, event_system)
client.connect()
client.start_listening_thread()

# Get the player_id
player_id = client.get_player_id()

# Initialize the input handler with the state manager
input_handler = InputHandler(event_system, player_id)

# Initialize the state manager
state_manager = StateManager(event_system)

# Initialize the scene manager
scene_manager = SceneManager(event_system, state_manager)

# TODO: Move this to a more logical location like "Start Game"
# Initialize the game scene with the scene manager
scene_manager.set_scene("GameScene")
state_manager.set_state("TestState")

# Initialize Engine
engine = GameEngine(screen, input_handler, event_system, scene_manager, state_manager)

game_manager = GameManager(input_handler, event_system, scene_manager, state_manager, client, engine)

# Example sprite access
sprites = SpriteFactory.loaded_images

# Access images using keys
full_path = "assets/sprites/entities/units/white/builder.png"

# remember "assets/sprites" is implicit for all images, so we just use:
image_key = "entities/unused/white/boat.png"
if image_key in sprites:
    image = sprites[image_key]
    print(f"Image found: {image_key}")
    # Now 'image' contains the pygame surface for the specified image
else:
    print(f"Image not found: {image_key}")

# Main game loop
running = True
while running:
    for pygame_event in pygame.event.get():
        if pygame_event.type == pygame.QUIT:
            running = False
        # Handle input
        input_handler.handle_input(pygame_event)
        # game_client.send_string(player_input)

    # Update game logic
    game_manager.update()

    # Clear the screen
    screen.fill((0, 0, 0))

    # Render game elements
    game_manager.render()

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)


# Close the game client
client.close()

# Quit Pygame
pygame.quit()

# Exit
sys.exit()
