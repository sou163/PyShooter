import pygame

WHITE = (255, 255, 255)

class Button:
    def __init__(self, img, scale, x, y):
        self.image = pygame.transform.scale(img, (int(scale * img.get_width()), int(scale * img.get_height())))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # getting current mouse position
        pos = pygame.mouse.get_pos()  
        action = False

        # checking whether button is clicked
        if self.rect.collidepoint(pos):
            pygame.draw.rect(screen, WHITE, (self.rect.x - 8, self.rect.y - 8, self.rect.w + 16, self.rect.h + 16), 3)
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False 

        return action