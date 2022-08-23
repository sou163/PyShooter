import pygame

# game window variables
WIDTH, HEIGHT = 1100, 720
MIDWIDTH, MIDHEIGHT = WIDTH // 2, HEIGHT // 2


class Transition():
	def __init__(self, occur, speed, colour):
		self.occur = occur
		self.speed = speed 
		self.colour = colour
		self.offset = 0

	def fadein(self, screen):
		self.offset += self.speed
		fade_complete = False
		
		# when each new level begins
		if self.occur == "intro":
			pygame.draw.rect(screen, self.colour, (0 - self.offset, 0, MIDWIDTH, HEIGHT))
			pygame.draw.rect(screen, self.colour, (MIDWIDTH + self.offset, 0, MIDWIDTH, HEIGHT))
		
		# when the player dies
		elif self.occur == "death":
			pygame.draw.rect(screen, self.colour, (0, 0, WIDTH, 0 + self.offset))

		# when the player has finished all his lives
		elif self.occur == "gameover":
			pygame.draw.rect(screen, self.colour, (0 - WIDTH + self.offset, 0, WIDTH, HEIGHT))
			pygame.draw.rect(screen, self.colour, (WIDTH - self.offset, 0, WIDTH, HEIGHT))
		
		# when the player completes a level
		elif self.occur == "levelup":
			pygame.draw.rect(screen, self.colour, (0, 0 - HEIGHT + self.offset, WIDTH, HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, HEIGHT - self.offset, WIDTH, HEIGHT))
		
		# when the editor is opened
		elif self.occur == "editor":
			pygame.draw.rect(screen, self.colour, (0 - self.offset, 0, MIDWIDTH, HEIGHT))
			pygame.draw.rect(screen, self.colour, (MIDWIDTH + self.offset, 0, MIDWIDTH, HEIGHT))

		
		# when transition is complete
		if self.offset >= HEIGHT:
			fade_complete = True

		return fade_complete