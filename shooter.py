import pygame
from pygame import mixer
from button import Button
from level_editor import LevelEditor
from transition import Transition
from world import World
from soldier import Soldier
from assets import Grenade 
import csv, json
import os, random

pygame.init()
mixer.init()
clock = pygame.time.Clock()
FPS = 60

# game window variables
WIDTH, HEIGHT = 1100, 720 
MIDWIDTH, MIDHEIGHT = WIDTH // 2, HEIGHT // 2
ROWS, COLS = 16, 150
TILE_SIZE = HEIGHT // ROWS

# set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyShooter")

# set game window logo
logo_img = pygame.image.load("images/logo.png").convert_alpha()
pygame.display.set_icon(logo_img)



# initial setup variables
run = True
game_opening = True
start_menu, start_intro = False, False
game_paused = False
option_screen, name_screen, help_screen = False, False, False
level_intro, editor_intro = False, False
pause_menu = False
set_music, set_sound, fx_on = False, False, True
changed = False
fade_timer, n = 100, 0
scroll, bg_scroll = 0, 0
player_name = ""
level = 0
lives = 3
max_score, high_score = 0, False
tilelist = []
clicked_enter, clicked_esc = False, False


# player action variables
move_left, move_right = False, False
fire_bullet = False
throw_bomb = False
thrown = False


# colours
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (90, 94, 91)
LIGHT_GREEN = (144, 201, 120)


# load music and sounds
pygame.mixer.music.load("musics/bg_music.mp3")         # background music
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(loops = -1, fade_ms = 5000)			# -1 to loop indefinitely

jump_fx = pygame.mixer.Sound("musics/jump.wav")
jump_fx.set_volume(1)


# load background images
pine1_img = pygame.image.load("images/background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("images/background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("images/background/mountain.png").convert_alpha()
sky_img = pygame.image.load("images/background/sky_cloud.png").convert_alpha()


# load button images
start_btn_img = pygame.image.load("images/buttons/start_btn.png").convert_alpha()
create_btn_img = pygame.image.load("images/buttons/create_btn.png").convert_alpha()
options_btn_img = pygame.image.load("images/buttons/options_btn.png").convert_alpha()

music_btn_img = pygame.image.load("images/buttons/music_btn.png").convert_alpha()
sound_btn_img = pygame.image.load("images/buttons/sound_btn.png").convert_alpha()
on_btn_img = pygame.image.load("images/buttons/on_btn.png").convert_alpha()
off_btn_img = pygame.image.load("images/buttons/off_btn.png").convert_alpha()

help_btn_img = pygame.image.load("images/buttons/help_btn.png").convert_alpha()
resume_btn_img = pygame.image.load("images/buttons/resume_btn.png").convert_alpha()
restart_btn_img = pygame.image.load("images/buttons/restart_btn.png").convert_alpha()
exit_btn_img = pygame.image.load("images/buttons/exit_btn.png").convert_alpha()


# load icon images
heart_img = pygame.transform.scale(pygame.image.load("images/icons/heart.png").convert_alpha(), (23, 25))
bullet_img = pygame.image.load("images/icons/bullet.png").convert_alpha()
grenade_img = pygame.transform.scale(pygame.image.load("images/icons/grenade.png").convert_alpha(), (14, 18))



# display text onto the screen
def draw_text(text, colour, pos, size):
	font = pygame.font.SysFont("Arial", size, True)
	font_img = font.render(text, True, colour)		# True for anti-aliasing 
	screen.blit(font_img, pos)

	return font_img.get_width()


# take player's name
def take_name(name, x, y):
	name_entered = False

	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_BACKSPACE:
				name = name[:-1]
			elif event.key == pygame.K_RETURN:
				name_entered = True
			else:
				name += event.unicode

	width = draw_text(name, WHITE, (x, y), 28)

	if name_entered:
		return name, width, True

	return name, width, False


# display the Help window
def show_help():
	# main menu
	draw_text("M A I N    M E N U", WHITE, (MIDWIDTH - 110, 20), 30)
	draw_text("_ _ _ _ _ _ _ _ _ _ _", WHITE, (MIDWIDTH - 120, 30), 30)
	draw_text("Click  START  to  play  the  Game", WHITE, (50, 80), 25)
	draw_text("Click  CREATE  to  create  and  edit  Levels", WHITE, (50, 115), 25)
	draw_text("Click  OPTIONS  to  open  the  Settings", WHITE, (50, 150), 25)
	# gameplay 
	draw_text("G A M E P L A Y", WHITE, (MIDWIDTH - 100, 190), 30)
	draw_text("_ _ _ _ _ _ _ _ _ _", WHITE, (MIDWIDTH - 110, 200), 30)
	draw_text("Press  A / D  or  LEFT / RIGHT  arrow  keys  to  Move  Left / Right", WHITE, (40, 250), 25)
	draw_text("Press  W / UP  arrow  key  to  Jump", WHITE, (40, 285), 25)
	draw_text("Press  S / RCTRL  to  shoot  Bullets : Player  deals  more  damage  than  Enemies", WHITE, (40, 320), 25)
	draw_text("Press  B  to  throw  Grenades : Both  Player  and  Enemies  suffer  50%  damage", WHITE, (40, 355), 25)
	draw_text("Player  dies  on  falling  into  Water  or  off  the  Screen  or  stepping  on  Landmines", WHITE, (40, 390), 25)
	draw_text("Press  ESC  to  Pause  the  game  and  ENTER  to  Resume  the  game", WHITE, (40, 425), 25)
	# score
	draw_text("S C O R E", WHITE, (MIDWIDTH - 90, 465), 30)
	draw_text("_ _ _ _ _ _ _", WHITE, (MIDWIDTH - 105, 475), 30)
	draw_text("You  score  + 20  on  shooting  down  an  enemy  soldier", WHITE, (40, 525), 25)
	draw_text("You  score  + 15  on  collecting  any  ItemBox : -  Health Box /  Ammo Box /  Grenade Box", WHITE, (40, 560), 25)
	draw_text("The  score  resets  to  0  once  you  die  or  after  completing  all  the  Levels", WHITE, (40, 595), 25)
	draw_text("High  Score  records  the  Highest  Score  you  made  in  one  go", WHITE, (40, 630), 25)

	draw_text("Press  ESC  to  return  to  Main  Menu..", WHITE, (MIDWIDTH + 200, HEIGHT - 40), 22)


# display the Options window
def show_options():
	global set_music, set_sound, changed, fx_on

	if music.draw(screen):
		set_music = True
		set_sound = False

	if sound.draw(screen):
		set_sound = True
		set_music = False
						
	if set_music and not changed:
		if music_on.draw(screen):
			# resume the background music
			mixer.music.unpause()
			changed = True

		if music_off.draw(screen):
			# pause the background music
			mixer.music.pause()
			changed = True								

		if changed:
			set_music = False
			changed = False

	elif set_sound and not changed:
		if sound_on.draw(screen):
			# play game sounds
			fx_on = True
			changed = True

		if sound_off.draw(screen):
			# stop game sounds
			fx_on = False
			changed = True								

		if changed:
			set_sound = False
			changed = False


# display player properties on the screen
def draw_assets(name):	
	draw_text("Health : ", RED, (30, 15), 35)
	
	draw_text("Ammo : ", RED, (30, 50), 35)
	for x in range(player.bullets):
		screen.blit(bullet_img, ((150 + x * 10), 70))

	draw_text("Grenades : ", RED, (30, 85), 35)
	for x in range(player.grenades):
		screen.blit(grenade_img, ((190 + x * 20), 100))
	
	draw_text("Lives : ", RED, (30, 120), 35)
	for x in range(lives):
		screen.blit(heart_img, ((130 + x * 30), 135))
	
	draw_text(f"Level : {level}", RED, (MIDWIDTH - 50, 15), 35)
	
	# display  player's current score 
	draw_text(f"Score : {player.score}", RED, (MIDWIDTH - 50, 50), 35)
	
	# display player's highest score
	with open("high score.json", "a+") as scorefile:
		filesize = os.path.getsize("high score.json")
		if filesize != 0:
			scorefile.seek(0)
			scores = json.load(scorefile)

			for key in scores:
				if key == name:
					max_score = scores[name]
				else:
					max_score = 0
		# if the file is empty
		else:
			max_score = 0
	draw_text(f"Your Highest Score : {max_score}", RED, (MIDWIDTH + 180, 15), 35)

	return max_score


# create background
def draw_background():
	width = sky_img.get_width()
	# offset the images by 'bg_scroll' for opposite direction movement
	# multiply 'bg_scroll' with a factor for parallax(uneven) scrolling effect
	for n in range(5):
		x = n * width
		screen.blit(sky_img, (x - bg_scroll * 0.5, 0))
		screen.blit(mountain_img, (x - bg_scroll * 0.6, HEIGHT - mountain_img.get_height() - 300))
		screen.blit(pine1_img, (x - bg_scroll * 0.7, HEIGHT - pine1_img.get_height() - 130))
		screen.blit(pine2_img, (x - bg_scroll * 0.8, HEIGHT - pine2_img.get_height() + 30))


# update high score file
def change_score(name, score):
	# read or create the high score file
    with open("high score.json", "a+") as scorefile:
        filesize = os.path.getsize("high score.json")
        if filesize != 0:
            scorefile.seek(0)
            scores = json.load(scorefile)

            not_found = False
            for key in scores:
                if key == name:
                    scores[name] = score
                else:
                    not_found = True

            # if the player's name does not exist, create new key:value pair 
            if not_found:
                scores[name] = score
        # if the file is empty
        else:
            scores = {name : score}

    # write to the high score file
    with open("high score.json", "w") as scorefile:
        json.dump(scores, scorefile)


def update_all():
	# update player and enemies
	player.update()
	player.draw(screen)
	player.draw_healthbar(screen)
	for enemy in groups[0]:
		enemy.control(player, groups, scroll, bg_scroll, tilelist, fx_on)
		enemy.update()
		enemy.draw_healthbar(screen)
		enemy.draw(screen)
	
	# update the sprite groups
	bullet_grp.update(scroll, player, groups, tilelist)
	grenade_grp.update(scroll, player, groups, tilelist, fx_on)
	explosion_grp.update(scroll)
	item_grp.update(scroll, player, fx_on)
	decorate_grp.update(scroll)
	water_grp.update(scroll)
	sign_grp.update(scroll)
	mine_grp.update(scroll, player, groups, fx_on)

	for n in range(1, len(groups)):
		groups[n].draw(screen)


def empty_groups():
	# reset the sprite groups
	for n in range(len(groups)):
		groups[n].empty()


def load_level():
	# empty all existing groups 
	empty_groups()
	# create empty level map
	data = []
	for i in range(ROWS):
		row = [-1] * COLS
		data.append(row)

	# load level data
	with open(f"levels/level{level}.csv", newline = "") as datafile:
		reader = csv.reader(datafile, delimiter = ",")
		for x, row in enumerate(reader):
			for y, tile in enumerate(row):
				data[x][y] = int(tile)

	return data


# create transitions : Transition(type, offset-speed, colour)
opening_fade = Transition("gameover", 3, BLACK)
intro_fade = Transition("intro", 3, BLACK)
death_fade = Transition("death", 4, BLACK)
newlevel_fade = Transition("levelup", 4, LIGHT_GREEN)
gameover_fade = Transition("gameover", 3, BLACK)
editor_fade = Transition("editor", 4, LIGHT_GREEN)


# create buttons : Button(image, scale-factor, x, y)
start = Button(start_btn_img, 0.7, MIDWIDTH - 100, 100)
create = Button(create_btn_img, 0.7, MIDWIDTH - 105, 200)
options = Button(options_btn_img, 0.7, MIDWIDTH - 135, MIDHEIGHT - 65)

music = Button(music_btn_img, 0.7, 250, 195)
music_on = Button(on_btn_img, 0.6, MIDWIDTH + 20, 200)
music_off = Button(off_btn_img, 0.6, MIDWIDTH + 160, 200)

sound = Button(sound_btn_img, 0.7, 250, MIDHEIGHT - 15)
sound_on = Button(on_btn_img, 0.6, MIDWIDTH + 20, MIDHEIGHT - 10)
sound_off = Button(off_btn_img, 0.6, MIDWIDTH + 160, MIDHEIGHT - 10)

helps = Button(help_btn_img, 0.7, MIDWIDTH - 93, MIDHEIGHT + 30)

resume = Button(resume_btn_img, 0.7, MIDWIDTH - 120, 150)
restart = Button(restart_btn_img, 0.7, MIDWIDTH - 135, MIDHEIGHT - 95)
options2 = Button(options_btn_img, 0.7, MIDWIDTH - 135, MIDHEIGHT + 15)
exit = Button(exit_btn_img, 0.7, MIDWIDTH - 88, MIDHEIGHT + 125)


# create sprite groups
enemy_grp = pygame.sprite.Group()			# 0
item_grp = pygame.sprite.Group()			# 1
decorate_grp = pygame.sprite.Group()		# 2
water_grp = pygame.sprite.Group()			# 3
sign_grp = pygame.sprite.Group()			# 4
mine_grp = pygame.sprite.Group()			# 5
bullet_grp = pygame.sprite.Group()			# 6
grenade_grp = pygame.sprite.Group()			# 7
explosion_grp = pygame.sprite.Group()		# 8

groups = [enemy_grp, item_grp, decorate_grp, water_grp, sign_grp, mine_grp, bullet_grp, grenade_grp, explosion_grp]


# main game loop
while run:
	# total levels
	max_levels = len(os.listdir("levels"))

	# display opening screen
	if game_opening:
		screen.fill(BLACK)
		for x in range(20):
			screen.blit(bullet_img, ((0 + x * 16 + n), 70))

		draw_text("Welcome  To", WHITE, (MIDWIDTH - 105, MIDHEIGHT - 85), 45)
		draw_text("PyShooter", WHITE, (MIDWIDTH - 130, MIDHEIGHT - 25), 65)
		
		for x in range(20):
			screen.blit(bullet_img, ((WIDTH - x * 16 - n), HEIGHT - 70))

		if fade_timer > 0:
			fade_timer -= 1
			n += 4
		else:			
			if opening_fade.fadein(screen):
				game_opening = False
				start_menu = True
				fade_timer = 100
				opening_fade.offset = 0

	# display menu screen
	elif start_menu:
		screen.fill(BLACK)
		draw_text("Click    START    to    play  ..", WHITE, (MIDWIDTH - 120, HEIGHT - 80), 25)

		# start button		
		if start.draw(screen) or clicked_enter:
			start_menu = False
			clicked_enter = False
			game_paused = True
			name_screen = True
			player_name = ""
			textbox = pygame.Rect(MIDWIDTH + 20, MIDHEIGHT - 25, 180, 45)
			box_selected, high_score = False, False
			level, score = 0, 0						
			lives = 3
			pygame.display.set_caption("PyShooter")
			lvl_data = load_level()
			world = World()
			player, tilelist = world.create(lvl_data, score, groups)

		# create button
		if create.draw(screen):
			start_menu = False
			game_paused = True
			level_intro = False
			editor_intro = True
			editor = LevelEditor()

		# options button
		if options.draw(screen):
			start_menu = False
			game_paused = True
			option_screen = True

		# help button
		if helps.draw(screen):
			start_menu = False
			game_paused = True
			help_screen = True
		
		# exit button				
		if exit.draw(screen) or clicked_esc:
			run = False
			clicked_esc = False		
	
	else:			
		if not game_paused:
			draw_background()
			world.draw(screen, scroll)

			update_all()	
			max_score = draw_assets(player_name)
			
			# play opening transition
			if start_intro:				
				if intro_fade.fadein(screen):
					start_intro = False
					intro_fade.offset = 0

			if player.alive:
				# check for player actions
				if fire_bullet:
					player.shoot(bullet_grp, fx_on)

				elif throw_bomb and not thrown and player.grenades > 0:
					x = player.rect.centerx + (0.6 * player.rect.size[0] * player.direction)
					y = player.rect.top
					grenade = Grenade(grenade_img, x, y, player.direction)
					grenade_grp.add(grenade)
					player.grenades -= 1
					thrown = True
					
				if move_left or move_right:
					player.change_action(1)		# running
				elif player.in_air:
				 	player.change_action(2)		# jumping
				else:
					player.change_action(0)		# standing
				
				scroll, level_over = player.move(move_left, move_right, groups, tilelist, bg_scroll)
				bg_scroll -= scroll			# total scroll offset

				# when player completes a level
				if level_over:
					scroll = 0
					bg_scroll = 0
					if level < max_levels - 1:
						level += 1
						game_paused = True
						level_intro = True
						score = player.score				
						# update level					
						lvl_data = load_level()
						world = World()
						player, tilelist = world.create(lvl_data, score, groups)
						
					# when all levels are cleared
					else:
						# check high score
						if player.score > max_score:
							high_score = True
							change_score(player_name, player.score)

						# play gameover transition
						if gameover_fade.fadein(screen):
							screen.fill(BLACK)
							draw_text("CONGRATS !", WHITE, (MIDWIDTH - 85, MIDHEIGHT - 95), 40)
							draw_text("Y O U  W O N !!", WHITE, (MIDWIDTH - 130, MIDHEIGHT - 25), 50)
							draw_text("All  levels  cleared!", WHITE, (MIDWIDTH - 100, MIDHEIGHT + 45), 30)
							if high_score:
								draw_text("** You have set a new High Score! **", WHITE, (MIDWIDTH - 180, MIDHEIGHT + 100), 30)
							draw_text("Press  ENTER  to  continue..", WHITE, (MIDWIDTH - 120, HEIGHT - 80), 25)
							if clicked_enter:								
								start_menu = True
								clicked_enter = False
								gameover_fade.offset = 0

			# when player dies
			else:
				scroll = 0
				bg_scroll = 0
				# make enemies idle
				for enemy in groups[0]:
					enemy.change_action(0)

				# check high score
				if player.score > max_score:
					high_score = True
					change_score(player_name, player.score)

				if lives > 1:
					# play death transition
					if death_fade.fadein(screen):
						draw_text("Press  ENTER  to  restart..", WHITE, (MIDWIDTH - 130, HEIGHT - 80), 25)
						if high_score:
							draw_text("** You have set a new High Score! **", WHITE, (MIDWIDTH - 225, MIDHEIGHT + 75), 30)

						# restart level if the player has lives left
						if restart.draw(screen) or clicked_enter:
							start_intro = True
							clicked_enter = False
							lives -= 1
							score, high_score = 0, False													
							lvl_data = load_level()
							world = World()
							player, tilelist = world.create(lvl_data, score, groups)
							death_fade.offset = 0	

				# when player has no lives left
				elif lives == 1:
					# play gameover transition
					if gameover_fade.fadein(screen):
						screen.fill(BLACK)
						draw_text("O O P S !!", WHITE, (MIDWIDTH - 65, MIDHEIGHT - 95), 40)
						draw_text("G A M E  O V E R", WHITE, (MIDWIDTH - 150, MIDHEIGHT - 25), 50)
						draw_text("No  more  Lives  left!", WHITE, (MIDWIDTH - 100, MIDHEIGHT + 45), 30)
						if high_score:
							draw_text("** You have set a new High Score! **", WHITE, (MIDWIDTH - 180, MIDHEIGHT + 100), 30)
						draw_text("Press  ENTER  to  continue..", WHITE, (MIDWIDTH - 120, HEIGHT - 80), 25)
						if clicked_enter:
							start_menu = True
							clicked_enter = False
							gameover_fade.offset = 0

		else:
			# play new level transition 
			if level_intro:
				if newlevel_fade.fadein(screen):
					if player_name != "":
						draw_text(f"Let's  Play  {player_name} !!", BLACK, (MIDWIDTH - 100, 30), 30)
					draw_text(f"LEVEL : {level}", BLACK, (MIDWIDTH - 75, MIDHEIGHT - 20), 40)
					fade_timer -= 1
					if fade_timer == 0:						
						start_intro = True
						game_paused = False
						level_intro = False
						fade_timer = 100
						newlevel_fade.offset = 0

			# play level editor open transition
			elif editor_intro:
				scroll, editor_data = 0, []
				editor.draw_bg(scroll)
				editor.draw_grid(scroll)
				editor_data = editor.create_base(editor_data)
				editor.draw_level(editor_data, scroll)

				if editor_fade.fadein(screen):
					editor_intro = False
					game_paused = False
					editor_fade.offset = 0
					done = editor.create(editor_data)
					if done:
						start_menu = True
						done = False		
			
			# game pause screen
			else:
				screen.fill(BLACK)
				# enter player name
				if name_screen:
					draw_text("Enter  your  name  : ", WHITE, (200, MIDHEIGHT - 30), 40)
					
					# check mouse pointer position
					if textbox.collidepoint(pygame.mouse.get_pos()):
						if pygame.mouse.get_pressed()[0] == 1:
							box_selected = True

					if box_selected:
						pygame.draw.rect(screen, WHITE, textbox, 3)
						player_name, width, done = take_name(player_name, textbox.x + 10, textbox.y + 3)
						textbox.w = max(180, width + 20)

						if len(player_name) > 0:
							draw_text("Press  ENTER  to  submit ..", WHITE, (MIDWIDTH + 200, HEIGHT - 40), 22)
						
						if done:
							name_screen = False
							clicked_enter = False
							level_intro = True						
					else:
						draw_text("Click  the  box  to  start  typing ..", WHITE, (MIDWIDTH + 200, HEIGHT - 40), 22)
						pygame.draw.rect(screen, GRAY, textbox, 3)

				# show help screen
				elif help_screen:
					show_help()
					if clicked_esc:
						help_screen = False
						start_menu = True
						clicked_esc = False
				
				# show options screen
				elif option_screen:
					draw_text("Press  ESC  to  return  to  Main  Menu..", WHITE, (MIDWIDTH + 200, HEIGHT - 40), 22)
					show_options()
					if clicked_esc:
						option_screen = False
						start_menu = True
						clicked_esc = False	

				# show pause menu			
				else:
					if pause_menu:
						text = "Press   ENTER   to   resume  or  ESC  to  quit .."
						draw_text(text, WHITE, (MIDWIDTH - 240, HEIGHT - 80), 25)
						clicked_esc = False
						
						# resume button
						if resume.draw(screen) or clicked_enter:
							game_paused = False
							clicked_enter = False
						
						# restart button
						if restart.draw(screen):
							game_paused = False
							if lives > 1:
								start_intro = True							
								lives -= 1
								score = 0												
								lvl_data = load_level()
								world = World()
								player, tilelist = world.create(lvl_data, score, groups)
							else:
								player.alive = False

						# options button
						if options2.draw(screen):
							pause_menu = False

						# exit button
						if exit.draw(screen) or clicked_esc:
							game_paused = False
							start_menu = True
							clicked_esc = False
					else:
						draw_text("Press  ESC  to  return  to  Pause  Menu..", WHITE, (MIDWIDTH + 200, HEIGHT - 40), 22)
						show_options()
						if clicked_esc:
							game_paused = True
							pause_menu = True
							clicked_esc = False
	

	# search for events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		# key down events
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				clicked_esc = True
				game_paused = True
			elif event.key == pygame.K_RETURN:
				clicked_enter = True

			if not game_paused:
				# get player actions
				if event.key == pygame.K_LEFT or event.key == pygame.K_a:
					move_left = True
				if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
					move_right = True	
				if event.key == pygame.K_UP or event.key == pygame.K_w:
					player.jump = True
					if fx_on:
						jump_fx.play()
				
				if event.key == pygame.K_RCTRL or event.key == pygame.K_s:
					fire_bullet = True
				elif event.key == pygame.K_b or event.key == pygame.K_q:
					throw_bomb = True

				
		# key release events
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT or event.key == pygame.K_a:
				move_left = False
			if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
				move_right = False
			if event.key == pygame.K_RCTRL or event.key == pygame.K_s:
				fire_bullet = False
			if event.key == pygame.K_b or event.key == pygame.K_q:
				throw_bomb = False
				thrown = False
				
	pygame.display.update()
	clock.tick(FPS)			# set the frame-rate for the game

pygame.quit()