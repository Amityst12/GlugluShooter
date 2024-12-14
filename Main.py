import pygame

#pygame setup
pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width()/2 , screen.get_height()/2)

while running:
    #poll for event
    #pygame.Quit event close windows
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    #screen background
    screen.fill("pink")
    
    pygame.draw.circle(screen, "black" , player_pos, 40)
    
    
    #Set player movement with limitations to screen
    keys = pygame.key.get_pressed()
    if(player_pos.y >= 40):
        if keys[pygame.K_w]:  #up W  -- UP LIMIT
            player_pos.y -= 300 *dt
            
    if(player_pos.y <= 680):
        if keys[pygame.K_s]:  # down S -- DOWN LIMIT
            player_pos.y += 300 *dt

    if(player_pos.x <= 1240):
        if keys[pygame.K_d]: # left D -- LEFT LIMIT
            player_pos.x += 300 *dt
            
    if(player_pos.x >= 40):
        if keys[pygame.K_a]: # right A -- RIGHT LIMIT
            player_pos.x -= 300 *dt
    
    #Restart player position clicking F1
    if keys[pygame.K_F1]:
        player_pos = pygame.Vector2(screen.get_width()/2 , screen.get_height()/2)
        
    
    #flip() the display to put your work on screen
    pygame.display.flip()
    
    dt = clock.tick(60)/1000 #fps limit (60)

pygame.quit()