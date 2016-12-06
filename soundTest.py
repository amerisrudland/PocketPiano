import os, pygame.mixer
import time
pygame.mixer.init(11025,8,1,4096)

file = os.path.join('data','c.mp3')
c = pygame.mixer.Sound(file)
d = os.path.join('data','d4.mp3')
e = os.path.join('data','e4.mp3')
#f = os.path.join('data','f4.mp3')
g = os.path.join('data','g4.mp3')
a = os.path.join('data','a4.mp3')
b = os.path.join('data','b4.mp3')

aa = pygame.mixer.Sound(a)
bb = pygame.mixer.Sound(b)
cc = pygame.mixer.Sound(c)
dd = pygame.mixer.Sound(d)
ee = pygame.mixer.Sound(e)
#ff = pygame.mixer.Sound(f)
gg = pygame.mixer.Sound(g)


aaa = pygame.mixer.Channel(0)
bbb = pygame.mixer.Channel(1)
ccc = pygame.mixer.Channel(2)
ddd = pygame.mixer.Channel(3)
eee = pygame.mixer.Channel(4)
#fff = pygame.mixer.Channel(5)
ggg = pygame.mixer.Channel(6)

ccc.play(cc)
time.sleep(10)
ddd.play(dd)
eee.play(ee)
#fff.play(ff)
ggg.play(gg)
aaa.play(aa)
bbb.play(bb)