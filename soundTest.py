import os, pygame.mixer
import time
pygame.mixer.init(11025,8,1,4096)

file = os.path.join('data','c.mp3')
a = pygame.mixer.Sound(file)

a.play(5)
time.sleep(10)