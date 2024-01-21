import sys

import pygame

from src.game.game_manager import GameManager
from network.client import GameClient
from game.engine import GameEngine
from game.scene_manager import SceneManager
from game.state_manager import StateManager
from utilities.input_handler import InputHandler
from utilities.event_system import EventSystem

# Initialize Pygame
pygame.init()

# Set up window size and other configurations
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 864
FPS = 60

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
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

# Initialize Game Manager
game_manager = GameManager(input_handler, event_system, scene_manager, state_manager, client, engine)

# pygame.mouse.set_visible(False)

# Main game loop
running = True
while running:
    print("======================== FRAME ========================")
    for pygame_event in pygame.event.get():
        if pygame_event.type == pygame.QUIT:
            running = False
        elif pygame_event.type == pygame.VIDEORESIZE:
            engine.handle_window_resize(new_size=pygame_event.size)
        # Handle input
        input_handler.handle_input(pygame_event)

    print("===== CLEAR =====")
    # Clear the screens
    engine.clear_screens()

    print("===== UPDATE =====")
    # Update game logic
    game_manager.update()

    print("===== RENDER =====")
    # Render game elements
    game_manager.render()

    print("===== UPDATE DISPLAY =====")
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
