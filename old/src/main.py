from Engine import Engine
from State import *
import pygame


def main():
    pygame.init()
    Constant.load_images()
    Constant.load_music()
    Constant.load_sounds()
    pygame.mixer.music.set_volume(.1)
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)
    clock = pygame.time.Clock()
    # Begin first turn
    engine = Engine()
    state = MainMenu(Constant.win, engine)
    engine.set_state(state)
    pygame.display.set_caption("Chess-Empires")
    pygame.display.set_icon(Constant.IMAGES['icon'])
    # MAIN LOOP
    while engine.running:
        # EVENT LOOP
        for event in pygame.event.get():
            # LEFT CLICK x
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                engine.state[-1].left_click()

            # QUIT
            elif event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # MOUSE MOVE:
            elif event.type == pygame.MOUSEMOTION:
                engine.state[-1].mouse_move()
            # RIGHT CLICK
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                engine.state[-1].right_click()

            # TAB
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_TAB):
                engine.state[-1].tab()

            # SPACE / ENTER
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE):
                engine.state[-1].enter()
            # M
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_m):
                engine.state[-1].m()

            # SONG END
            elif event.type == MUSIC_END:
                Constant.load_music()

        engine.update()
        # DRAW GAME STATES:
        engine.state[-1].draw()
        # UPDATE DISPLAY
        pygame.display.update()
        # CLICK CLOCK
        clock.tick(Constant.MAX_FPS)

    if not engine.running:
        main()


if __name__ == "__main__":
    main()
