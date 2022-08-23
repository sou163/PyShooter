import pygame
from button import Button
import csv, os

pygame.init()
clock = pygame.time.Clock()
FPS = 60

# game window variables
WIDTH, HEIGHT = 1100, 720
PANEL_WIDTH = 350
MARGIN = WIDTH - PANEL_WIDTH
ROWS, COLS = 16, 150

# set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))


# tile variables
TILE_SIZE = HEIGHT // ROWS
TILE_TYPES = 22
img_list, tile_list = [], []

# load tile images in a list
for n in range(TILE_TYPES):
	img = pygame.image.load(f'images/tiles/{n}.png').convert_alpha()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

# create a tile button list for the side-panel
btn_col, btn_row = 0, 0
for n in range(TILE_TYPES):
	x = (MARGIN + 20) + (70 * btn_col)
	y = 75 * btn_row + 30
	button = Button(img_list[n], 1, x, y)
	tile_list.append(button)

	btn_col += 1
	if btn_col == 3:
		btn_row += 1
		btn_col = 0


# load button images
save_img = pygame.image.load('images/buttons/save_btn.png').convert_alpha()
load_img = pygame.image.load('images/buttons/load_btn.png').convert_alpha()
exit_img = pygame.image.load('images/buttons/exit_btn2.png').convert_alpha()
clear_img = pygame.image.load('images/buttons/clear_btn.png').convert_alpha()

# load background images
pine1_img = pygame.image.load('images/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('images/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('images/background/mountain.png').convert_alpha()
sky_cloud_img = pygame.image.load('images/background/sky_cloud.png').convert_alpha()

# load game window logo
logo_img = pygame.image.load("images/logo.png").convert_alpha()


# colours
SKY_BLUE = (144, 211, 190)
WHITE = (255, 255, 255)
RED = (200, 25, 25)
BLACK = (0, 0, 0)

# font
font = pygame.font.SysFont('Impact', 25)


class LevelEditor():
	def __init__(self):
		# set the window caption
		pygame.display.set_caption('Level Editor')

		# set game window logo
		pygame.display.set_icon(logo_img)


	# display text onto the screen
	def draw_text(self, text, font, text_col, x, y):
		img = font.render(text, True, text_col)
		screen.blit(img, (x, y))


	# create background
	def draw_bg(self, scroll):
		width = sky_cloud_img.get_width()
		for n in range(5):
			x = n * width
			screen.blit(sky_cloud_img , (x - scroll * 0.5 , 0))
			screen.blit(mountain_img , (x - scroll * 0.6 , HEIGHT - mountain_img.get_height() - 300))
			screen.blit(pine1_img , (x - scroll * 0.7 , HEIGHT - pine1_img.get_height() - 130))
			screen.blit(pine2_img , (x - scroll * 0.8 , HEIGHT - pine2_img.get_height() + 30))


	# draw the grid for positioning of tiles
	def draw_grid(self, scroll):
		# vertical lines
		for col in range(COLS + 1):
			x = col * TILE_SIZE - scroll
			pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
		# horizontal lines
		for row in range(ROWS):
			y = row * TILE_SIZE
			pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))


	# draw the bottom ground for each new Level
	def create_base(self, data):
		# populate the tile matrix	
		for row in range(ROWS):
			r = [-1] * COLS
			data.append(r)

		for tile in range(COLS):
			data[ROWS - 1][tile] = 1

		return data


	# display each Level
	def draw_level(self, level_data, scroll):
		for y , row in enumerate(level_data):
			for x , tile in enumerate(row):
				if tile >= 0:
					screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))

		# draw the side panel
		pygame.draw.rect(screen, SKY_BLUE, (MARGIN + 1, 0, PANEL_WIDTH, HEIGHT))


	def create(self, data):
		# scroll variables
		scroll = 0
		scroll_speed = 15
		scroll_left, scroll_right = False, False

		# level variables
		level = -1
		level_data = data
		max_levels = len(os.listdir("levels"))
		
		change_level, new_level = False, False
		save_level, level_saved = False, False	
		level_loaded = False		
		text = ''
		current_tile = 0		

		# create buttons
		save_button = Button(save_img, 1, WIDTH - 110, 140)
		load_button = Button(load_img, 1, WIDTH - 110, 245)
		clear_button = Button(clear_img, 1, WIDTH - 115, 350)
		exit_button = Button(exit_img, 1, WIDTH - 110, 455)

		run = True
		while run:
			clock.tick(FPS)

			self.draw_bg(scroll)
			self.draw_grid(scroll)
			self.draw_level(level_data, scroll)	
			
			# draw the side panel
			pygame.draw.rect(screen, SKY_BLUE, (MARGIN + 1, 0, PANEL_WIDTH, HEIGHT))	
			# select a tile
			for n, tile in enumerate(tile_list):
				if tile.draw(screen):
					current_tile = n					

			# hightight the selected tile
			pygame.draw.rect(screen, RED, tile_list[current_tile].rect, 4)

			# save current level data
			if save_button.draw(screen) or save_level:
				save_level = False
				if level >= 0:
					with open(f'levels/level{level}.csv', 'w', newline = '') as csvfile:
						writer = csv.writer(csvfile, delimiter = ',')
						for row in level_data:
							writer.writerow(row)
					max_levels = len(os.listdir("levels"))
					level_saved = True	

			# load level data
			if load_button.draw(screen) or change_level:
				if level < 0:
					level += 1
					level_loaded = True
					
				scroll = 0
				change_level = False
				if level < max_levels:
					new_level = False
					level_saved = False
					with open(f'levels/level{level}.csv', newline = '') as csvfile:
						reader = csv.reader(csvfile, delimiter = ',')
						for x , row in enumerate(reader):
							for y , tile in enumerate(row):
								level_data[x][y] = int(tile)
				else:
					level_data = []
					level_data = self.create_base(level_data)
					new_level = True
					level_saved = False
					text = f'No Level {level} present!'

			# clear the entire current level data and start fresh
			if clear_button.draw(screen):
				level_data = []
				level_data = self.create_base(level_data)

			# close the level editor
			if exit_button.draw(screen):
				run = False


			if level >= 0:
				self.draw_text(f'Level : {level}', font, BLACK, WIDTH - 110, 70)
				self.draw_text('Press Up/ Down to change levels', font, BLACK, MARGIN + 10, HEIGHT - 105)
				self.draw_text('Press Left/ Right to scroll', font, BLACK, MARGIN + 50, HEIGHT - 60)
			else:
				self.draw_text('    Click Load to begin', font, BLACK, WIDTH - 300, HEIGHT - 90)

			if level_saved:
				text = '        Level Saved'		# space for centering
			elif new_level == False:
				text = ''

			self.draw_text(f'{text}', font, RED, MARGIN + 95, HEIGHT - 160)

			# check scroll limit
			if scroll_left and scroll > 0:
				scroll -= scroll_speed
			elif scroll_right and scroll < (COLS * TILE_SIZE - MARGIN):
				scroll += scroll_speed


			# check whether the mouse cursor is within the grid area
			pos = pygame.mouse.get_pos()
			x = (pos[0] + scroll) // TILE_SIZE
			y = pos[1] // TILE_SIZE

			if pos[0] < MARGIN and pos[1] < HEIGHT and level_loaded:
				# add the selected tile using left click
				if pygame.mouse.get_pressed()[0] == 1:
					if level_data[y][x] != current_tile:
						level_data[y][x] = current_tile
						level_saved = False

				# remove any tile using right click
				if pygame.mouse.get_pressed()[2] == 1:
					if level_data[y][x] != -1:
						level_data[y][x] = -1
						level_saved = False


			# check events
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False

				# when keys are pressed
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						run = False

					# save any level
					if event.key == pygame.K_s:
						save_level = True
					# load the initial level
					if event.key == pygame.K_l:
						change_level = True

					# press up arrow to go to next level
					if event.key == pygame.K_UP and level >= 0:
						level += 1
						change_level = True

					# press down arrow to go back to the previous level
					if event.key == pygame.K_DOWN and level >= 0:
						level -= 1
						change_level = True
						if level < max_levels:
							text = ''

					# for scrolling left and right
					if event.key == pygame.K_LEFT and level >= 0:
						scroll_left = True
					elif event.key == pygame.K_RIGHT and level >= 0:
						scroll_right = True

				# when keys are released
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_LEFT:
						scroll_left = False
					elif event.key == pygame.K_RIGHT:
						scroll_right = False

			pygame.display.update()

		return True
