import pygame
from settings import *
from random import choice
vector = pygame.math.Vector2

class Spriteshet:
    def __init__(self,images):
        self.spritesheet = pygame.image.load(images)

    def get_image(self,x,y,width,height):
        image = pygame.Surface((width,height))
        image.blit(self.spritesheet,(0,0),(x,y,width,height))
        image = pygame.transform.scale(image,(width // 2 , height // 2))
        image.set_colorkey((0,0,0))
        return image


class Player(pygame.sprite.Sprite) :
    def __init__(self,game):
        super().__init__()
        self.game = game
        self.load_images()
        self.lastTime = 0
        self.counter = 0
        self.jumping = False
        self.walking = False
        self.image = self.waiting[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2,HEIGHT/2)
        self.speed = vector(0,0)
        self.acceleration = vector(0,0.5)

    def load_images(self):
        self.waiting = [self.game.spritesheet.get_image(581,1265,121,191) , self.game.spritesheet.get_image(584,0,121,201)]

        self.right_walking = [self.game.spritesheet.get_image(584,203,121,201) , self.game.spritesheet.get_image(678,651,121,207)]

        self.left_walking = []

        for walking in self.right_walking :
            self.left_walking.append(pygame.transform.flip(walking,True,False))


    def jump(self):
        self.rect.y += 1
        touch = pygame.sprite.spritecollide(self,self.game.platforms,False)
        if touch and self.jumping:
            self.game.jumpSound.play()
            self.speed.y -= 15
            self.jumping = False


    def update(self, *args):

        self.animation()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] :
            if keys[pygame.K_RIGHT] :
                if self.speed.x < 7 :
                    self.acceleration.x = 0.5
                else :
                    self.acceleration.x = 0

            if keys[pygame.K_LEFT] :
                if self.speed.x > -7 :
                    self.acceleration.x = -0.5
                else :
                    self.acceleration.x = 0

            self.speed.x += self.acceleration.x
        else:
            if self.speed.x > 0 :
                self.speed.x -= 0.3
            if self.speed.x < 0 :
                self.speed.x += 0.3

        self.speed.y += self.acceleration.y

        if abs(self.speed.x) < 0.2:
            self.speed.x = 0

        self.rect.x += self.speed.x
        self.rect.y += self.speed.y


        if self.rect.x > WIDTH :
            self.rect.x = 0 - self.rect.width

        if self.rect.right < 0 :
            self.rect.right = WIDTH + self.rect.width

        self.mask = pygame.mask.from_surface(self.image)

    def animation(self):
        currentTime = pygame.time.get_ticks()

        if self.speed.x != 0 :
            self.walking = True
        else:
            self.walking = False

        if self.walking :
            if currentTime - self.lastTime > 150 :
                self.lastTime = currentTime
                if self.speed.x > 0 :
                    bottom = self.rect.midbottom
                    self.image = self.right_walking[self.counter % 2]
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = bottom
                    self.counter += 1
                else :
                    bottom = self.rect.midbottom
                    self.image = self.left_walking[self.counter % 2]
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = bottom
                    self.counter += 1



        if not self.walking :
            if currentTime - self.lastTime > 350:
                self.lastTime = currentTime
                bottom = self.rect.midbottom
                self.image = self.waiting[self.counter % 2]
                self.rect = self.image.get_rect()
                self.rect.midbottom = bottom
                self.counter += 1


class Platform(pygame.sprite.Sprite):
    def __init__(self,game,x,y):
        super().__init__()
        self.game = game
        self.image = choice([self.game.spritesheet.get_image(0,576,380,94),self.game.spritesheet.get_image(218,1456,201,100)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Boost(pygame.sprite.Sprite):
    def __init__(self,game,platform):
        super().__init__()
        self.game = game
        self.platform = platform
        self.image = self.game.spritesheet.get_image(820,1805,71,70)
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.platform.rect.midtop

    def update(self, *args):
        self.rect.midbottom = self.platform.rect.midtop

        if not self.game.platforms.has(self.platform) :
            self.kill()

class  Enemy(pygame.sprite.Sprite):
    def __init__(self,game,platform):
        super().__init__()
        self.game = game
        self.platform = platform
        self.upload_images()
        self.image = self.wait
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.platform.rect.midtop
        self.lastTime = 0
        self.counter = 0

        self.vx = 2 # düşmanın yatay düzlemdeki hareket hızı


    def upload_images(self):
        self.wait = self.game.spritesheet.get_image(814,1417,90,155)

        self.rightWalk = [self.game.spritesheet.get_image(704,1256,120,159),self.game.spritesheet.get_image(812,296,90,155)]

        self.leftWalk = []

        for walks in self.rightWalk :
            self.leftWalk.append(pygame.transform.flip(walks,True,False))

    def update(self, *args):
        self.rect.bottom = self.platform.rect.top

        if not self.game.platforms.has(self.platform) :
            self.kill()

        self.rect.x += self.vx

        if self.rect.right + 5 > self.platform.rect.right or self.rect.x - 5 < self.platform.rect.left :
            savedVx = self.vx
            self.vx = 0

            bottom = self.rect.midbottom
            self.image = self.wait
            self.rect = self.image.get_rect()
            self.rect.midbottom = bottom

            self.vx = savedVx * -1

        if self.vx > 0 :
            current = pygame.time.get_ticks()
            if current - self.lastTime > 250 :
                self.lastTime = current
                bottom = self.rect.midbottom
                self.image = self.rightWalk[self.counter % 2]
                self.rect = self.image.get_rect()
                self.rect.midbottom = bottom
                self.counter += 1
        else :
            current = pygame.time.get_ticks()
            if current - self.lastTime > 250 :
                self.lastTime = current
                bottom = self.rect.midbottom
                self.image = self.leftWalk[self.counter % 2]
                self.rect = self.image.get_rect()
                self.rect.midbottom = bottom
                self.counter += 1

        self.mask = pygame.mask.from_surface(self.image)