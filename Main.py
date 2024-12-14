import pygame

#pygame setup
pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
running = True

while running:
    #poll for eventy
    #pygame.Quit event close windows
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    #screen background
    screen.fill("purple")
    
    #RENDER GAME HERE
    
    #flip() the display to put your work on screen
    pygame.display.flip()
    
    clock.tick(60) #fps limit (60)

pygame.quit()