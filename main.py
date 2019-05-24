# Josh Bothell
# Tank Game
import pygame as pg
import sys
import time
from os import  path
from settings import *
from sprites import *
from tilemap import *

font_name = pg.font.match_font('Arial')






class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()
        self.score = 0

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        self.map_folder = path.join(game_folder, 'maps')
        snd_folder = path.join(game_folder, 'snd')

        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.player_img = pg.transform.rotate(self.player_img, 90)
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_img = pg.transform.rotate(self.bullet_img, 90)
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.mob_img = pg.transform.rotate(self.mob_img, 90)
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.explosion_anim = {}
        self.explosion_anim['lg'] = []
        self.explosion_anim['sm'] = []
        self.explosion_anim['player'] = []
        for i in range(9):
            filename = 'regularExplosion0{}.png'.format(i)
            img = pg.image.load(path.join(img_folder, filename)).convert()
            img.set_colorkey(BLACK)
            img_lg = pg.transform.scale(img, (75, 75))
            self.explosion_anim['lg'].append(img_lg)
            img_sm = pg.transform.scale(img, (32, 32))
            self.explosion_anim['sm'].append(img_sm)
            filename = 'sonicExplosion0{}.png'.format(i)
            img = pg.image.load(path.join(img_folder, filename)).convert()
            img.set_colorkey(BLACK)
            self.explosion_anim['player'].append(img)
        self.repair_img = pg.image.load(path.join(img_folder, REPAIR_IMG)).convert_alpha()
        self.boost_img = pg.image.load(path.join(img_folder, BOOST_IMG)).convert_alpha()
        self.title_font = path.join(img_folder, 'BlackOpsOne-Regular.ttf')
        self.hud_font = path.join(img_folder, 'Blockletter.otf')
        # load sounds
        pg.mixer.music.load(path.join(snd_folder, 'commando_team.ogg'))
        pg.mixer.music.set_volume(0.4)
        pg.mixer.music.play(loops=-1)
        self.shoot_sound = pg.mixer.Sound(path.join(snd_folder, 'shoot.wav'))
        self.bullet_hit_sound = pg.mixer.Sound(path.join(snd_folder, 'bullet_hit.wav'))
        self.tank_explosion = pg.mixer.Sound(path.join(snd_folder, 'tank_explosion.wav'))
        self.mob_explosion = pg.mixer.Sound(path.join(snd_folder, 'mob_explosion.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(snd_folder, 'boost_sound.wav'))
        self.shield_sound = pg.mixer.Sound(path.join(snd_folder, 'shield_sound.wav'))

    def new(self, map_choice):
        # initialize map
        self.mob_total = 5
        self.current_level = 1
        if map_choice == "level1":
            self.map = TiledMap(path.join(self.map_folder, 'tiled2.tmx'))
        elif map_choice == "level2":
            self.map = TiledMap(path.join(self.map_folder, 'tiled3.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.player_bullets = pg.sprite.Group()
        self.mob_bullets = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        # for row, tiles in enumerate(self.map.data):
        #     for col, tile in enumerate(tiles):
        #         if tile == '1':
        #             Wall(self, col, row)
        #         if tile == 'P':
        #             self.player = Player(self, col, row)
        #         if tile == 'M':
        #             Mob(self, col, row)

        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x, tile_object.y)
            if tile_object.name == 'mob':
                Mob(self, tile_object.x, tile_object.y)
            if tile_object.name == 'tree':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'repair_powerup':
                HealthPowerup(self, tile_object.x, tile_object.y)
            if tile_object.name == 'boost_powerup':
                GunPowerup(self, tile_object.x, tile_object.y)
        self.camera = Camera(self.map.width, self.map.height)


    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True

        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        # check for level change
        if self.mob_total == 0 and self.current_level != 2:
            self.score += self.player.health
            self.level_up()
            self.new("level2")
            self.current_level = 2
        elif self.mob_total == 0 and self.current_level == 2:
            self.score += self.player.health
            self.you_win_screen()
            self.new("level1")
        print(self.score)

        # mobs bullet hit player
        hits = pg.sprite.spritecollide(self.player, self.mob_bullets, True, collide_hit_rect)
        for hit in hits:
            self.bullet_hit_sound.play()
            expl = Explosion(self, hit.pos, 'sm')
            self.all_sprites.add(expl)
            self.player.health -= BULLET_DAMAGE
            if self.player.health <= 0:
                self.tank_explosion.play()
                expl = Explosion(self, self.player.pos, 'player')
                self.all_sprites.add(expl)
                self.playing = False
        # print(self.player.health)
        # collision between tanks

        # player hits powerup
        hits = pg.sprite.spritecollide(self.player, self.powerups, True, collide_hit_rect)
        for hit in hits:
            print("collide")
            if hit.type == 'repair':
                self.shield_sound.play()
                hit.health_up()
            if hit.type == 'boost':
                self.boost_sound.play()
                self.player.boost()

        # bullet hits mobs
        hits = pg.sprite.groupcollide(self.mobs, self.player_bullets, False, True)
        for hit in hits:
            expl = Explosion(self, hit.pos, 'sm')
            self.all_sprites.add(expl)
            hit.health -= BULLET_DAMAGE
            hit.vel = vec(0, 0)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        # pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
        # HUD
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def show_start_screen(self):
        self.screen.fill(DARKGREY)
        file = open('highscore.txt', "r")
        line_List = file.readlines()
        file.close()
        high_score = line_List[-1]
        self.draw_text("TANX", self.title_font, 150, DARKGREEN,
                       WIDTH / 2, HEIGHT / 3, align="center")
        self.draw_text("By: Josh Bothell", self.hud_font, 25, WHITE,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("High Score: " + str(high_score), self.hud_font, 25, WHITE,
                       WIDTH / 2, HEIGHT / 2 + (HEIGHT / 10), align="center")
        self.draw_text("Press any key to start", self.title_font, 50, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        self.draw_text("Arrow Keys to move, Space to fire", self.hud_font, 25, WHITE,
                       WIDTH / 2, HEIGHT * 5 / 6, align="center")
        pg.display.flip()
        file.close()
        self.wait_for_key()

    def level_up(self):
        self.screen.fill(DARKGREY)
        self.draw_text("NEXT LEVEL", self.title_font, 100, YELLOW,
                       WIDTH / 2, HEIGHT / 3, align="center")
        self.draw_text("Score:" + str(self.score), self.hud_font, 25, WHITE,
                       WIDTH / 2, HEIGHT / 2, align="center")
        pg.display.flip()
        time.sleep(1.5)
        self.draw_text("Press any key to start", self.hud_font, 50, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        self.screen.fill(DARKGREY)
        file = open('highscore.txt', "r")
        line_List = file.readlines()
        file.close()
        high_score = line_List[-1]
        if self.score > int(high_score):
            file = open('highscore.txt', "w")
            file.write(str(self.score))
            file.close()
            file = open('highscore.txt', 'r')
            line_List = file.readlines()
            file.close()
            high_score = line_List[-1]
        self.draw_text("GAME OVER", self.title_font, 100, RED,
                       WIDTH / 2, HEIGHT / 3, align="center")
        self.draw_text("Score: " + str(self.score), self.hud_font, 25, WHITE,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("High Score: " + str(high_score), self.hud_font, 25, WHITE,
                       WIDTH / 2, HEIGHT * 5 / 6, align="center")
        pg.display.flip()
        time.sleep(1.5)
        self.draw_text("Press any key to restart", self.title_font, 50, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        self.score = 0
        pg.display.flip()
        self.wait_for_key()

    def you_win_screen(self):
        self.screen.fill(DARKGREY)
        self.screen.fill(DARKGREY)
        file = open('highscore.txt', "r")
        line_List = file.readlines()
        file.close()
        high_score = line_List[-1]
        if self.score > int(high_score):
            file = open('highscore.txt', "w")
            file.write(str(self.score))
            file.close()
            file = open('highscore.txt', 'r')
            line_List = file.readlines()
            file.close()
            high_score = line_List[-1]
        self.draw_text("You Win", self.title_font, 100, BLUE,
                       WIDTH / 2, HEIGHT / 3, align="center")
        self.draw_text("Score: " + str(self.score), self.hud_font, 25, WHITE,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("High Score: " + str(high_score), self.hud_font, 25, WHITE,
                       WIDTH / 2, HEIGHT * 5 / 6, align="center")
        pg.display.flip()
        time.sleep(1.5)
        self.draw_text("Press any key to play again", self.title_font, 50, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        self.score = 0
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False


# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new('level1')
    g.run()
    g.show_go_screen()