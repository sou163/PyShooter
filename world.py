import pygame
from soldier import Soldier
from elements import Decorate, Water, LevelSign, Item, Mine

# game window variables
WIDTH, HEIGHT = 1100, 720
ROWS, COLS = 16, 150
TILE_SIZE = HEIGHT // ROWS

pygame.display.set_mode((WIDTH, HEIGHT))

# create a list of tile images
TILE_TYPES = 22
tile_images = []
for num in range(TILE_TYPES):
	img = pygame.image.load(f"images/tiles/{num}.png").convert_alpha()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	n = (num, img)			# tuple of tile number and images
	tile_images.append(n)


# load itembox images
healthbox_img = pygame.image.load("images/icons/health_box.png").convert_alpha()
ammobox_img = pygame.image.load("images/icons/ammo_box.png").convert_alpha()
grenadebox_img = pygame.image.load("images/icons/grenade_box.png").convert_alpha()

item_boxes = {"health" : healthbox_img, "ammo" : ammobox_img, "grenades" : grenadebox_img}


class World():
	def __init__(self):
		self.tilelist = []

	def create(self, data, score, groups):
		player = None
		# iterate through the world data and create all the game objects
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				
				if tile >= 0:
					x2 = x * TILE_SIZE
					y2 = y * TILE_SIZE
					tup = tile_images[tile]
					img = tup[1]
					rect = img.get_rect()
					rect.x = x2
					rect.y = y2
					tile_data = (img, rect, tup[0])

					if tile >= 0 and tile <= 8:					# dirt blocks
						self.tilelist.append(tile_data)		
					elif tile >= 9 and tile <= 10:				# water
						water = Water(x2, y2, img)
						groups[3].add(water)			
					elif tile >= 11 and tile <= 14:				# decoration
						decorate = Decorate(x2, y2, img)
						groups[2].add(decorate)			
					elif tile == 15:							# player
						player = Soldier("player", x2, y2, 4, 20, 5)
						player.score = score
					elif tile == 16:							# enemy
						enemy = Soldier("enemy", x2, y2, 2, 50, 0)	
						groups[0].add(enemy)
					elif tile == 17:							# ammobox
						item = Item(x2, y2, "ammo", item_boxes)
						groups[1].add(item)
					elif tile == 18:							# grenadebox
						item = Item(x2, y2, "grenades", item_boxes)
						groups[1].add(item)
					elif tile == 19:							# healthbox
						item = Item(x2, y2, "health", item_boxes)
						groups[1].add(item)
					elif tile == 20:							# level sign
						sign = LevelSign(x2, y2, img)
						groups[4].add(sign)
					elif tile == 21:							# landmine
						mine = Mine(x2, y2, img)
						groups[5].add(mine)
						self.tilelist.append(tile_data)
						
		return player, self.tilelist


	def draw(self, screen, scroll):
		for tile in self.tilelist:
			tile[1][0] += scroll			# adding scroll
			screen.blit(tile[0], tile[1])