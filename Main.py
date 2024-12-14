import pygame
#CONSTANTS

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
PLAYER_RADIUS = 40
PLAYER_COLOR = "black"
BACKGROUND_COLOR = "pink"
SPEED = 300

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0
player_pos = pygame.Vector2(screen.get_width()/2 , screen.get_height()/2)

#Handles player movement, limitaions and velocity
def playerMovement(keys,dt):
    global player_pos
    velocity = pygame.Vector2(0, 0)
    if keys[pygame.K_w]:
        velocity.y -= SPEED * dt
    if keys[pygame.K_s]:
        velocity.y += SPEED * dt
    if keys[pygame.K_a]:
        velocity.x -= SPEED * dt
    if keys[pygame.K_d]:
        velocity.x += SPEED * dt

    if velocity.length() > 0:
        velocity = velocity.normalize() * SPEED * dt

    player_pos += velocity
    player_pos.x = max(PLAYER_RADIUS, min(player_pos.x, SCREEN_WIDTH - PLAYER_RADIUS))
    player_pos.y = max(PLAYER_RADIUS, min(player_pos.y, SCREEN_HEIGHT - PLAYER_RADIUS))

#Handles basic events
def basicEvents(keys):
    global player_pos
    #Restart player position clicking F1
    if keys[pygame.K_F1]:
        player_pos = pygame.Vector2(screen.get_width()/2 , screen.get_height()/2)
        
    #Allowes pressing F11
    if keys[pygame.K_F11]:
        pygame.display.toggle_fullscreen()
    

while running:
    #poll for event
    
    #Pygame.QUIT event closes the window - Graceful exit on ALT+F4
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    
    #Screen background
    screen.fill(BACKGROUND_COLOR)
    
    #Draw player
    pygame.draw.circle(screen, PLAYER_COLOR, player_pos, PLAYER_RADIUS)
    
    #Reading input
    keys = pygame.key.get_pressed() 
    
    #Set player movement with limitations to screen
    playerMovement(keys,dt)
    
    #Handles basic events 
    basicEvents(keys)
        
    
    #flip() the display to put your work on screen
    pygame.display.flip()
    
    dt = clock.tick(60)/1000 #fps limit (60)

    
    
pygame.quit()