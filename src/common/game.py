import pygame
from common.managers import EventManager

FRAMERATE = 50 # 1000 // FRAMERATE = FPS

class ChainStrike:
  @staticmethod
  def go():
    pygame.init()
    eventManager = EventManager()

    resetCounter = 0
    resetTimer = 20
  
    i = 0

    # set frame rate
    REFRESH = pygame.USEREVENT + 1
    pygame.time.set_timer(REFRESH, FRAMERATE)
    running = True
    while running:
      for event in pygame.event.get():
        if event.type == REFRESH:
          if eventManager.RESET:
            if resetCounter >= resetTimer:
              eventManager.reset()
              resetCounter = 0
            else:
              resetCounter += 1
          eventManager.event_scan()
          eventManager.refresh()
        elif event.type == pygame.MOUSEBUTTONDOWN:
          eventManager.click(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
          eventManager.key_press(event.key)
          if event.key == pygame.K_0:
            pygame.image.save(eventManager._environmentManager._window.window, "image" + str(i) + ".png")
            i += 1
        elif event.type == pygame.KEYUP:
          eventManager.key_release(event.key)
        elif event.type == pygame.VIDEORESIZE:
          eventManager.resize()
        elif event.type == pygame.QUIT:
          eventManager.quit()
          running = False
    pygame.quit()