import pygame
import random
import sys
from settings import *
from sprites import *


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.spritesheet = Spriteshet(SPRITESHEET)
        self.running = True
        self.show = True
        self.platformCounter = 0
        self.score = 0
        self.maxScore = 0

        self.gameoverSound = pygame.mixer.Sound("sounds/gameover.mp3")
        self.jumpSound = pygame.mixer.Sound("sounds/jump.mp3")
        self.jumpSound.set_volume(0.5)

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.boosts = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        p1 = Platform(self,0, HEIGHT - 30)
        p2 = Platform(self,WIDTH / 2 - 50,350)
        p3 = Platform(self,400, 300)
        p4 = Platform(self,300,20)
        p5 = Platform(self,100, 200)
        p6 = Platform(self,50, 500)

        self.platforms.add(p1)
        self.platforms.add(p2)
        self.platforms.add(p3)
        self.platforms.add(p4)
        self.platforms.add(p5)
        self.platforms.add(p6)

        self.player = Player(self)

        self.all_sprites.add(self.player)

        self.all_sprites.add(p1)
        self.all_sprites.add(p2)
        self.all_sprites.add(p3)
        self.all_sprites.add(p4)
        self.all_sprites.add(p5)
        self.all_sprites.add(p6)

        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()
            self.update()

    def update(self):
        self.all_sprites.update()

        if self.player.speed.y > 0:
            collisions = pygame.sprite.spritecollide(self.player, self.platforms, dokill=False)

            if collisions :
                durum = self.player.rect.midbottom[0] <= collisions[0].rect.left or self.player.rect.midbottom[0] >= collisions[0].rect.right
                if collisions[0].rect.center[1] + 7 > self.player.rect.bottom and not durum:
                    self.player.jumping = True
                    self.player.speed.y = 0
                    self.player.rect.bottom = collisions[0].rect.top

        if self.player.rect.top < HEIGHT / 4:
            self.player.rect.y += max(abs(self.player.speed.y),3)
            for platform in self.platforms:
                platform.rect.y += max(abs(self.player.speed.y),3)
                if platform.rect.top >= HEIGHT:
                    platform.kill()
                    self.score += 10

        if self.player.rect.top > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.speed.y, 15)
                if sprite.rect.bottom < 0:
                    sprite.kill()

        if len(self.platforms) == 0:
            try:
                with open("scores/score.txt", "r") as scoreTxt:
                    savedScore = int(scoreTxt.read())
                    if self.score > savedScore:
                        with open("scores/score.txt", "w") as scoreTxt:
                            scoreTxt.write(str(self.score))
                        self.maxScore = self.score
                    else :
                        with open("scores/score.txt","r") as scoreTxt :
                            score = str(scoreTxt.read())
                            self.maxScore = score
            except FileNotFoundError:
                with open("scores/score.txt","w") as scoreTxt:
                    scoreTxt.writelines(str(self.score))
                    self.maxScore = score

            self.score = 0
            self.playing = False

        while len(self.platforms) < 6:
            if self.platformCounter == 0:
                width = random.randrange(50, 100)
                platform = Platform(self, random.randrange(0, WIDTH - width), random.randrange(-2, 0))
            else:
                width = random.randrange(50, 100)
                platform = Platform(self,random.randrange(0, WIDTH - width), random.randrange(-42, -2))

            self.platformCounter += 1

            if len(self.platforms) == 5:
                self.platformCounter = 0

            self.platforms.add(platform)
            self.all_sprites.add(platform)

            if random.randint(1,15) == 1:
                boost = Boost(self,platform)
                self.boosts.add(boost)
                self.all_sprites.add(boost)

            if platform.rect.width > 100 :
                if random.randint(1,10) % 2 == 1:
                    enemy = Enemy(self,platform)
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)


        boostControl = pygame.sprite.spritecollide(self.player,self.boosts,True)
        if boostControl :
            self.player.speed.y -= 25

        enemyContanct = pygame.sprite.spritecollide(self.player,self.enemies,False,pygame.sprite.collide_mask)
        if enemyContanct:
            self.playing= False

        pygame.display.update()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.jump()

    def draw(self):
        self.screen.fill((246, 173, 113))
        self.ScoreText("Skor : {}".format(self.score))
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image,self.player.rect)

    def finishScreen(self):
        finishScreen = pygame.image.load("screens/finish.jpg")
        self.screen.blit(finishScreen, finishScreen.get_rect())
        font = pygame.font.SysFont("Century Gothic", 25)
        text = font.render("En Yüksek Skor : {} ".format(self.maxScore), True, (255, 255, 255))
        self.screen.blit(text, (WIDTH / 2 - (text.get_size()[0] / 2), 300))
        self.gameoverSound.play()
        pygame.display.update()
        self.tusBekleme()

    def startScreen(self):
        startScreen = pygame.image.load("screens/start.jpg")
        self.screen.blit(startScreen, startScreen.get_rect())
        pygame.display.update()
        self.tusBekleme()

    def tusBekleme(self):
        bekleme = True
        while bekleme:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    bekleme = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    bekleme = False

    def ScoreText(self, score):
        font = pygame.font.SysFont("Century Gothic", 25)
        text = font.render(score, True, (255, 255, 255))
        self.screen.blit(text, (WIDTH / 2 - (text.get_size()[0] / 2), 0))


game = Game()
game.startScreen()

while game.running:
    game.new()
    game.finishScreen()
