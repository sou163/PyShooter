import pygame
from pygame import mixer

# game window variables
WIDTH, HEIGHT = 1100, 720
ROWS, COLS = 16, 150
TILE_SIZE = HEIGHT // ROWS			# 45		

pygame.display.set_mode((WIDTH, HEIGHT))

# music and sounds
mixer.init()
explode_fx = pygame.mixer.Sound("musics/grenade.wav")
explode_fx.set_volume(1)


class Bullet(pygame.sprite.Sprite):
	def __init__(self, image, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction
		self.speed = 8

	def update(self, scroll, player, groups, tilelist):
		self.rect.x += (self.direction * self.speed) + scroll
		
		# if bullets collide with tiles
		for tile in tilelist:
			if tile[1].colliderect(self.rect):
				self.kill()

		# if bullets exit screen window
		if self.rect.right < 0 or self.rect.left > WIDTH:
			self.kill()				# remove the bullet instance
				
		# on hitting the enemies 
		for enemy in groups[0]:
			if pygame.sprite.spritecollide(enemy, groups[6], False):
				if enemy.alive:
					self.kill()
					enemy.health -= 15
					if enemy.health <= 0:
						player.score += 20
		# on hitting the player
		if pygame.sprite.spritecollide(player, groups[6], False):
			if player.alive:
				self.kill()
				player.health -= 10


class Grenade(pygame.sprite.Sprite):
	def __init__(self, image, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction
		self.speed = 7
		self.y_vel = -10
		self.timer = 80
		self.bounce = 1 			# adding bounce 

	def update(self, scroll, player, groups, tilelist, fx_on):
		GRAVITY = 0.75
		self.y_vel += GRAVITY
		dx = self.speed * self.direction
		dy = self.y_vel

		# if grenades exit screen window
		if self.rect.right < 0 or self.rect.left > WIDTH:
			self.kill()				# remove the grenade instance

		# collisions with tiles
		for tile in tilelist:
			# horizontally
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1				# changing the direction of the grenade
				dx = self.speed * self.direction
			# vertically
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				# in mid-air
				if self.y_vel < 0:
					dy = tile[1].bottom - self.rect.top
					self.y_vel = 0
				# when falling
				elif self.y_vel >= 0:
					if self.bounce > 0:
						dy = tile[1].top - self.rect.bottom
						self.y_vel = -5
						self.speed = 3
						self.bounce -= 1
					else:
						self.y_vel = 0
						self.speed = 0
					
		# update coordinates
		self.rect.x += dx + scroll
		self.rect.y += dy

		# countdown to explosion
		self.timer -= 1
		if self.timer == 0:
			explode = Explosion(self.rect.x, self.rect.y, 1)
			groups[8].add(explode)
			if fx_on:
				explode_fx.play()
			self.kill()
				
			# inflict damage within an explosion radius
			if abs(self.rect.centerx - player.rect.centerx) < (TILE_SIZE * 2) \
						and abs(self.rect.centery - player.rect.centery) < (TILE_SIZE * 2):
				player.health -= 50

			for enemy in groups[0]:
				if abs(self.rect.centerx - enemy.rect.centerx) < (TILE_SIZE * 2) \
						and abs(self.rect.centery - enemy.rect.centery) < (TILE_SIZE * 2):
					if enemy.alive:
						enemy.health -= 50
						if enemy.health <= 0:
							player.score += 20


class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		# load all images
		for i in range(5):
			img = pygame.image.load(f"images/explosion/{i}.png").convert_alpha()
			img = pygame.transform.scale(img, (int(scale * img.get_width()), int(scale * img.get_height())))
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0

	def update(self, scroll):
		# add scroll
		self.rect.x += scroll
		
		# update explosion animation
		EXPLOSION_REFRESH = 4
		self.counter += 1
		if self.counter >= EXPLOSION_REFRESH:
			self.counter = 0
			self.index += 1
			if self.index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.index]