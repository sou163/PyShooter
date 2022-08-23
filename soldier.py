import pygame
from pygame import mixer
from assets import Bullet, Grenade
import os, random


# game window variables
WIDTH, HEIGHT = 1100, 720
ROWS, COLS = 16, 150
TILE_SIZE = HEIGHT // ROWS			# 45
LEVELSIZE = TILE_SIZE * COLS

pygame.display.set_mode((WIDTH, HEIGHT))

# colours
RED = (255, 0, 0)
GREEN = (0, 128, 0)
YELLOW = (255, 128, 0)

# music and sounds
mixer.init()
shoot_fx = pygame.mixer.Sound("musics/shoot.wav")
shoot_fx.set_volume(1)

# load icon images
bullet_img = pygame.image.load("images/icons/bullet.png").convert_alpha()

# constants
GRAVITY = 0.75
REFRESH_TIME = 100
SCROLL_THRESHOLD = 200


class Soldier(pygame.sprite.Sprite):
	def __init__(self, kind, x, y, speed, bullets, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.kind = kind			# player or enemy
		self.image_list = []		
		self.index = 0
		self.action = 0
		animation_states = ["idle", "run", "jump", "death"]
		scale = 1.5
		for state in animation_states:
			temp_list = []
			frames = len(os.listdir(f"images/{self.kind}/{state}"))		# length of a list containing all files in the directory
			for i in range(frames):
				img = pygame.image.load(f"images/{self.kind}/{state}/{i}.png").convert_alpha()
				img = pygame.transform.scale(img, (int(scale * img.get_width()), int(scale * img.get_height())))
				temp_list.append(img)
			self.image_list.append(temp_list)
		
		self.image = self.image_list[self.action][self.index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.update_time = pygame.time.get_ticks()		# initial time-stamp
		self.speed = speed
		self.direction = 1
		self.flip = False
		self.jump = False
		self.in_air = True
		self.jump_vel = 0
		self.cooldown = 0 			# shoot cooldown
		self.bullets = bullets
		self.grenades = grenades
		self.alive = True
		self.full_health = 100
		self.health = self.full_health
		self.timelapsed = 0
		self.score = 0
		
		# enemy-only variables
		self.move_counter = 0
		self.idle = False
		self.idle_counter = 0
		self.sight = pygame.Rect(0, 0, 180, 20)	


	def move(self, move_left, move_right, groups, tilelist, bg_scroll):
		dx, dy = 0, 0
		screen_scroll = 0
		
		if move_left:
			dx = -self.speed
			self.direction = -1
			self.flip = True
		if move_right:
			dx = self.speed
			self.direction = 1
			self.flip = False

		# when jumping
		if self.jump and not self.in_air:
			self.jump_vel = -12
			self.jump = False
			self.in_air = True
		
		# apply gravity
		self.jump_vel += GRAVITY
		if self.jump_vel > 10:
			self.jump_vel = 10 		# cap at a max value
			self.in_air = True
		dy += self.jump_vel

		# on collision with tiles
		for tile in tilelist:
			if self.kind == "enemy":
				# horizontal collision
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
					self.direction *= -1
					self.move_counter = 0
				# vertical collision
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					# when an enemy is falling
					if self.jump_vel >= 0:
						dy = tile[1].top - self.rect.bottom
						self.in_air = False
					self.jump_vel = 0	

			if self.kind == "player" and tile[2] != 21:			# if the tile is not a landmine
				# horizontal collision
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				# vertical collision
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					# when player is jumping
					if self.jump_vel < 0:
						dy = tile[1].bottom - self.rect.top
					# when player is falling
					elif self.jump_vel >= 0:
						dy = tile[1].top - self.rect.bottom
						self.in_air = False
					self.jump_vel = 0


		level_over = False
		if self.kind == "player":

			# on collision with water tiles
			if pygame.sprite.spritecollide(self, groups[3], False):
				self.health = 0

			# on collision with level signs		
			if pygame.sprite.spritecollide(self, groups[4], False):
				level_over = True

			# when player tries to go past the horizontal screen edges
			if self.rect.left + dx < 0 or self.rect.right + dx > WIDTH:
				dx = 0

		# when the player or enemies fall below the screen
		if self.rect.bottom + dy > HEIGHT:
			dy = 0
			self.health = 0


		# update co-ordinates on screen
		self.rect.x += dx
		self.rect.y += dy

		# update the scrolling based on the player's position
		if self.kind == "player":
			if (self.rect.right > WIDTH - SCROLL_THRESHOLD and bg_scroll < LEVELSIZE - WIDTH) \
					or (self.rect.left < SCROLL_THRESHOLD and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx			# screen moves opposite to the player

		return screen_scroll, level_over


	def reset_animation(self):
		self.image = self.image_list[self.action][self.index]
		# check time passed between updates
		if (pygame.time.get_ticks() - self.update_time) > REFRESH_TIME:
			self.update_time = pygame.time.get_ticks()		# reset update timer
			self.index += 1
			if self.index >= len(self.image_list[self.action]):
				if self.action != 3:
					self.index = 0
				else:
					self.index = len(self.image_list[self.action]) - 1


	def change_action(self, new_move):
		# check if new action is different
		if new_move != self.action:
			self.action = new_move
			self.index = 0
			self.update_time = pygame.time.get_ticks()


	def update(self):
		if self.health <= 0:
			self.alive = False
			self.health = 0					
			self.speed = 0
			self.timelapsed += 1
			self.change_action(3)
		self.reset_animation()
		
		# update shoot cooldown
		if self.cooldown > 0:
			self.cooldown -= 1


	def shoot(self, bullet_grp, fx_on):
		# allow firing bullets only after certain time interval
		if self.cooldown == 0 and self.bullets > 0:
			if fx_on:
				shoot_fx.play()

			x = self.rect.centerx + (0.7 * self.rect.size[0] * self.direction)
			y = self.rect.centery
			bullet = Bullet(bullet_img, x, y, self.direction)
			bullet_grp.add(bullet)
			self.bullets -= 1
			self.cooldown = 15
			
		elif self.bullets <= 0:
			if self.kind == "player":
				self.bullets = 0
			else:
				self.bullets = 100	


	def control(self, player, groups, scroll, bg_scroll, tilelist, fx_on):
		if player.alive and self.alive:
			# make an enemy randomly pause while patrolling
			if not self.idle and random.randint(1, 200) == 1:
				self.idle = True
				self.idle_counter = 0
				self.change_action(0)

			# if player comes within an enemy's line of sight, the enemy stops and shoots
			if self.sight.colliderect(player.rect):
				self.change_action(0)
				self.shoot(groups[6], fx_on)		# groups[6] is bullet group
			else:
				if not self.idle:
					# when player crosses an enemy midway, the enemy flips towards the player
					if self.rect.colliderect(player.rect):
						if self.direction == 1 and player.rect.centerx < self.rect.centerx:
							self.flip = True
							self.direction *= -1
							self.move_counter *= -1 
						elif self.direction == -1 and player.rect.centerx > self.rect.centerx:
							self.flip = False
							self.direction *= -1
							self.move_counter *= -1

					if self.direction == 1:
						move_right = True
					else:
						move_right = False
					move_left = not move_right
					self.move(move_left, move_right, groups, tilelist, bg_scroll)
					self.change_action(1)
					
					# update enemy's line of sight
					self.sight.center = (self.rect.centerx + 100 * self.direction, self.rect.centery - 10)
					
					# make the enemy patrol
					self.move_counter += 1
					if self.move_counter >= TILE_SIZE:
						self.direction *= -1		# flip-over
						self.move_counter *= -1				
				else:				
					self.idle_counter += 1
					if self.idle_counter >= TILE_SIZE:
						self.idle = False

		# scroll the enemy positions with the screen
		self.rect.x += scroll	


	def draw_healthbar(self, screen):
		img_width = self.image.get_width()
		# show player health bar
		if self.kind == "player":
			bar_width = int(self.health / self.full_health * 100) + 15
			if self.health > 50:			
				pygame.draw.rect(screen, GREEN, (150, 25, bar_width, 25))
			elif self.health > 25:
				pygame.draw.rect(screen, YELLOW, (150, 25, bar_width, 25))
			elif self.health > 0:
				pygame.draw.rect(screen, RED, (150, 25, bar_width, 25))
		# show enemy health bars
		else:
			bar_width = int(self.health / self.full_health * img_width) + 10
			if self.health > 50:			
				pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 15, bar_width, 10))
			elif self.health > 25:
				pygame.draw.rect(screen, YELLOW, (self.rect.x, self.rect.y - 15, bar_width, 10))
			elif self.health > 0:
				pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 15, bar_width, 10))


	def draw(self, screen):
		if self.timelapsed <= 180:
			# draw the player and enemies on screen
			self.image = pygame.transform.flip(self.image, self.flip, False)
			screen.blit(self.image, self.rect)
		else:
			# remove the dead bodies from screen after certain time
			self.kill()