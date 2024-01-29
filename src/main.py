import sys
import pygame
from src.game.game_manager import GameManager
from src.network.client import GameClient
from src.game.engine import GameEngine
from src.game.scene_manager import SceneManager
from src.game.state_manager import StateManager
from src.game.event_manager import EventManager

# Initialize Pygame
pygame.init()


def main():
    # Set up window size and other configurations
    SCREEN_WIDTH = 1536
    SCREEN_HEIGHT = 864
    FPS = 60

    # Set up the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Chess Empires")
    clock = pygame.time.Clock()

    # Initialize the event system
    event_manager = EventManager()

    # Initialize the game client
    client = GameClient("192.168.1.149", 5555, event_manager)
    client.connect()
    client.start_listening_thread()

    # Get the player_id
    player_id = client.get_player_id()

    # Initialize the state manager
    state_manager = StateManager(event_manager)

    # Initialize the scene manager
    scene_manager = SceneManager(event_manager, state_manager)

    # Initialize Engine
    engine = GameEngine(screen, player_id, event_manager, scene_manager, state_manager)

    # Initialize Game Manager
    game_manager = GameManager(event_manager, scene_manager, state_manager, client, engine)

    # pygame.mouse.set_visible(False)

    game_manager.start_game()

    running = True
    while running:
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                running = False
            elif pygame_event.type == pygame.VIDEORESIZE:
                engine.handle_window_resize(new_size=pygame_event.size)
            # Handle input
            engine.handle_input(pygame_event)

        # Clear the screens
        engine.clear_screens()

        # Update game logic
        game_manager.update()

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


if __name__ == '__main__':
    main()
