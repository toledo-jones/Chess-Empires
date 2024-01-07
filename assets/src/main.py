import sys

import pygame
from network.client import GameClient
from game.engine import GameEngine
from game.scene_manager import SceneManager
from game.state_manager import StateManager
from utilities.input_handler import InputHandler
from utilities.event_system import EventSystem


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

# Initialize the game engine
game_engine = GameEngine(SCREEN_WIDTH, SCREEN_HEIGHT)

# Initialize the event system
event_system = EventSystem()

# Initialize the scene manager
scene_manager = SceneManager(event_system)

# Initialize the state manager
state_manager = StateManager(event_system)

# Initialize the input handler with the state manager
input_handler = InputHandler(event_system)

# Initialize the game scene with the state manager
game_scene = scene_manager.set_scene("GameScene", state_manager)

# Initialize the game client
game_client = GameClient("127.0.0.1", 5555, event_system)
game_client.connect()
game_client.start_listening_thread()

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
    game_engine.update()

    # Clear the screen
    screen.fill((0, 0, 0))

    # Render game elements
    game_engine.render(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Close the game client
game_client.close()

# Quit Pygame
pygame.quit()

# Exit
sys.exit()
