# Josh Bothell
# Tank Game
import pygame as pg
import sys
from os import  path
from settings import *
from sprites import *
from tilemap import *


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        map_folder = path.join(game_folder, 'maps')
        snd_folder = path.join(game_folder, 'snd')
        self.map = TiledMap(path.join(map_folder, 'tiled2.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
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
        # load sounds
        pg.mixer.music.load(path.join(snd_folder, 'commando_team.ogg'))
        pg.mixer.music.set_volume(0.4)
        pg.mixer.music.play(loops=-1)
        self.shoot_sound = pg.mixer.Sound(path.join(snd_folder, 'shoot.wav'))
        self.bullet_hit_sound = pg.mixer.Sound(path.join(snd_folder, 'bullet_hit.wav'))
        self.tank_explosion = pg.mixer.Sound(path.join(snd_folder, 'tank_explosion.wav'))
        self.mob_explosion = pg.mixer.Sound(path.join(snd_folder, 'mob_explosion.wav'))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.player_bullets = pg.sprite.Group()
        self.mob_bullets = pg.sprite.Group()
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
        pass

    def show_go_screen(self):
        pass


# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()