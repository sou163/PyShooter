import pygame
from pygame import mixer
from assets import Explosion


# game window variables
WIDTH, HEIGHT = 900, 720
ROWS, COLS = 16, 150
TILE_SIZE = HEIGHT // ROWS			# 45


# music and sounds
mixer.init()
collect_fx = pygame.mixer.Sound("musics/box.wav")
collect_fx.set_volume(1)
explode_fx = pygame.mixer.Sound("musics/grenade.wav")
explode_fx.set_volume(1)


# decoration class
class Decorate(pygame.sprite.Sprite):
	def __init__(self, x, y, img):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, scroll):
		self.rect.x += scroll


# water tile class
class Water(pygame.sprite.Sprite):
	def __init__(self, x, y, img):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, scroll):
		self.rect.x += scroll


# next level sign class
class LevelSign(pygame.sprite.Sprite):
	def __init__(self, x, y, img):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, scroll):
		self.rect.x += scroll


# landmine tile class
class Mine(pygame.sprite.Sprite):
	def __init__(self, x, y, img):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, scroll, player, groups, fx_on):
		self.rect.x += scroll

		if pygame.sprite.collide_rect(self, player):
			# inflict damage within the explosion radius
			if abs(self.rect.centerx - player.rect.centerx) < (TILE_SIZE * 1.5) \
						or abs(self.rect.centery - player.rect.centery) < (TILE_SIZE * 1.5):
				explode = Explosion(self.rect.x, self.rect.y, 1.5)
				groups[8].add(explode)
				if fx_on:
					explode_fx.play()		# play explosion sound
				player.health = 0
				self.kill()


# itembox class
class Item(pygame.sprite.Sprite):
	def __init__(self, x, y, item_type, images):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = images[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self, scroll, player, fx_on):
		self.rect.x += scroll

		# when player collides with an item-box
		if pygame.sprite.collide_rect(self, player):
			player.score += 15
			if fx_on:
				collect_fx.play()		# play collect sound
			
			# health box
			if self.item_type == "health":
				player.health += 50
				if player.health > 100:
					player.health = 100
			
			# ammo box
			if self.item_type == "ammo":
				player.bullets += 15
				if player.bullets > 30:
					player.bullets = 30
			
			# grenade box
			if self.item_type == "grenades":
				player.grenades += 5
				if player.grenades > 10:
					player.grenades = 10

			# remove the box
			self.kill()
