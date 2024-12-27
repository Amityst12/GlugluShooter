import pygame
import time
import random
import json
from game_config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS ,SPEED, SPAWNRATE, HEALTH

print("-----------------------------------------------------")
# Open JSON
with open("Game/Changes.json") as file:
    config = json.load(file)
    DEFAULTVOLUME = config["Volume"]
    HIGHSCORE = config["HIGHSCORE"]
print(config)


# Makes animation
def load_frames(spritesheet, frame_width, frame_height, num_frames, flip =0):
        """Load animation frames from a sprite sheet."""
        frames = []

        for i in range(num_frames):
            x = i * frame_width
            y =frame_height
            frame = spritesheet.subsurface((x, y, frame_width, frame_height))
            if flip == 1:
                frame = pygame.transform.flip(frame,True,False)
            frames.append(frame)
        return frames
    
# Write to json file
def write_to_JSON(Catagory, Value):
    config[Catagory] = Value
    out_file = open("Game/Changes.json",'w')
    json.dump(config, out_file, indent= 6)
    print(f"New json: {config}")


# Base class for all game states
class GameState:
    def __init__(self, manager):
        self.manager = manager

    def handle_events(self):
        """Handle events specific to this state."""
        pass

    def update(self, dt):
        """Update logic specific to this state."""
        pass

    def render(self, screen):
        """Render the state to the screen."""
        pass

# Enemy class
class Enemy:
    def __init__(self, x, y, speed, frames):
        self.x = x
        self.y = y
        self.speed = speed
        self.frames = frames
        self.current_frame = 0
        self.animation_speed = 0.13  # Adjust to control animation speed
        self.animation_timer = 0
        self.pos = pygame.Vector2(x,y)
        self.image_width = 124  # Match your frame width
        self.image_height = 128
        self.radius = self.image_height // 2
        

    def update(self, dt):
        """Update enemy logic, including animation."""
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)


    def collides_with(self, bullet_pos, bullet_radius=5):
        """Check if a bullet collides with the enemy using circular hit detection."""
        # Center of the collision circle
        center = pygame.Vector2(
            self.pos.x + self.image_width / 2,
            self.pos.y + self.image_height / 2
        )
        # Distance between bullet and enemy center
        distance = center.distance_to(bullet_pos)
        return distance < self.radius + bullet_radius
    
    def move_towards(self, target_pos, dt):
        """Move the enemy towards the target position."""
        direction = target_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * self.speed * dt
        
    def render(self, screen):
        """Draw the enemy."""
        current_image = self.frames[self.current_frame]
        screen.blit(current_image, (self.pos.x, self.pos.y))
        """pygame.draw.circle(
            screen,  # Surface to draw on
            "red",   # Hitbox color (use transparent color if distracting)
            (int(self.pos.x + self.image_width / 2), int(self.pos.y + self.image_height / 2)),  # Center of the circle
            self.radius,  # Radius of the hitbox
            2  # Line width (set to 0 for filled circle if needed)
        )""" #debug

# PowerUp class
class PowerUp:
    def __init__(self, x ,y ,type_):
        self.pos = pygame.Vector2(x,y)
        self.type = type_
        self.radius = 20 #Size for collision
        self.color_map = {1: "Shield.png", 2: "Acceleration.png" , 3 :"Coin.png" ,4 : "Heart.png"}
        self.active = True
        self.Powerup_sprite = pygame.image.load("Assets/Sprites/"+self.color_map[self.type])
        self.Powerup_sprite = pygame.transform.scale(self.Powerup_sprite, (40,40))
        
    def update(self, dt):
        """Floating animation for power up"""
        self.pos.y += 100 * dt  # Move power-up down at 100 pixels/second
        if self.pos.y > SCREEN_HEIGHT:  # Remove if it moves out of bounds
            self.active = False
        
    def render(self,screen):
        if self.active:
            screen.blit(self.Powerup_sprite,(int(self.pos.x)-20, int(self.pos.y)-20))
        """pygame.draw.circle(
            screen,  # Surface to draw on
            "red",   # Hitbox color (use transparent color if distracting)
            (self.pos.x, self.pos.y),  # Center of the circle
            self.radius,  # Radius of the hitbox
            2  # Line width (set to 0 for filled circle if needed)
        )""" # Drawing for debug
     
    def collides_with(self,player_pos, player_radius):
        Fixedpos = pygame.Vector2(player_pos.x +40, player_pos.y +40)
        return self.pos.distance_to(Fixedpos) < self.radius+ player_radius    
            



# Gameplay State
class GameplayState(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.player_pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.speed = SPEED
        self.player_radius = 45
        self.bullets = []
        self.health = HEALTH
        
        self.score = 0
        self.clockActive = False
        
        # Sprites
        self.hero = pygame.image.load("Assets/Sprites/Hero.png")
        self.hero = pygame.transform.scale(self.hero, (90,90))
        self.hero_right = pygame.transform.flip(self.hero,True,False)
        self.facing_right = False
        self.bubble = pygame.image.load("Assets/Sprites/Bubble.png")
        self.bubble = pygame.transform.scale(self.bubble, (30,30))
        self.shield = pygame.image.load("Assets/Sprites/Bubble_1.png")
        self.shield = pygame.transform.scale(self.shield, (125,125))
        self.shield.set_alpha(80)
        
        self.chosen_background = "Assets/Sprites/"+ str(random.randint(1,3)) +"_game_background.png"
        self.background = pygame.image.load(self.chosen_background)
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Enemies
        self.enemies = []
        self.spawn_rate = 0
        self.spawn_timer = 0
        self.flip = 0
        
        self.shark_spritesheet = pygame.image.load('assets/sprites/shark1.png').convert_alpha()
        self.shark_frames = load_frames(self.shark_spritesheet, frame_width=136, frame_height=128 , num_frames=4)
        self.shark_frames_rev = load_frames(self.shark_spritesheet, frame_width=136, frame_height=128 , num_frames=4, flip = 1)
        
        self.shark_spritesheet = pygame.image.load('assets/sprites/shark2.png').convert_alpha()
        self.shark_frames2 = load_frames(self.shark_spritesheet, frame_width=152, frame_height=128 , num_frames=4)
        self.shark_frames2_rev = load_frames(self.shark_spritesheet, frame_width=152, frame_height=128 , num_frames=4, flip = 1)
        
        # Power ups
        self.power_ups = []
        self.power_up_spawn_timer = 0
        self.power_up_spawn_rate = 14 # Spawn a power up once in X seconds
        
        self.shield_timer = 0
        self.bullet_speed_timer = 0
        self.bullet_speed_multiplier = 1  # Default bullet speed multiplier
        
        # Glu sounds
        self.glues = {
            1 : "Assets/Music/Glu1.ogg",
            2 : "Assets/Music/Glu2.ogg",
            3 : "Assets/Music/Glu3.ogg",
            4 : "Assets/Music/Glu4.ogg",
            5 : "Assets/Music/Glu4.ogg"
        }
        

    def activate_clock(self):
        self.clockActive = True
    def deactivate_clock(self):
        self.clockActive = False
    def game_reset(self):
        print("Game has been reset")
        self.score = 0
        self.health = HEALTH
        self.player_pos = pygame.Vector2(SCREEN_WIDTH/2 , SCREEN_HEIGHT/2)
        self.enemies = []
        self.bullets = []
        self.power_ups = []
        self.power_up_spawn_timer = 0
        self.spawn_rate = 0
        self.spawn_timer = 0
        self.chosen_background = "Assets/Sprites/"+ str(random.randint(1,3)) +"_game_background.png"
        self.background = pygame.image.load(self.chosen_background)
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
    def get_score(self):
        return self.score
               
    def shoot_bullet(self):
        """shoots bullet toward the mouse cursor"""
        player_center = pygame.Vector2(
        self.player_pos.x + self.player_radius,
        self.player_pos.y + self.player_radius)
        mouse_pos = pygame.mouse.get_pos() #Get mouse position
        direction = pygame.Vector2(mouse_pos[0] - player_center.x, mouse_pos[1] - player_center.y)  # Calculate the direction from the player to the mouse
        if direction.length() > 0 :
            direction = direction.normalize()
        bullet = {
            "pos": pygame.Vector2(self.player_pos.x+45, self.player_pos.y+45),  #Start at player position
            "dir" : direction                                                   #Bullet direction
        }
        sound = pygame.mixer.Sound(self.glues[random.randint(1,5)])
        sound.set_volume(0.20)
        sound.play()
        self.bullets.append(bullet)

    def handle_events(self):
        """Handle gameplay-specific events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.change_state("pause", 0.1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button ==1:
                self.shoot_bullet()
        
        # Checking if player lost
        if self.health == 0:
            print("Game over")
            self.manager.change_state("over", 1.5)

    def update(self, dt):
        """Update gameplay logic."""
        keys = pygame.key.get_pressed()
        velocity = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            velocity.y -= self.speed * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocity.y += self.speed * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            velocity.x -= self.speed * dt
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            velocity.x += self.speed * dt
            self.facing_right = True

        if velocity.length() > 0:
            velocity = velocity.normalize() * self.speed * dt

        self.player_pos += velocity
        self.player_pos.x = max(0, min(self.player_pos.x, SCREEN_WIDTH - 90))
        self.player_pos.y = max(0, min(self.player_pos.y, SCREEN_HEIGHT - 90))
        
        
        # Updating score ON TIME
        if self.clockActive:
            self.score += dt*5
            
        # Update bullets, update score on hit
        for bullet in self.bullets[:]: 
            bullet["pos"] += bullet["dir"] * 1200 * self.bullet_speed_multiplier * dt #Move bullet 1200px/sec
            rem = 0
            
            if(bullet["pos"].x < 0 or bullet["pos"].x > SCREEN_WIDTH or #X
               bullet["pos"].y < 0 or bullet["pos"].y > SCREEN_HEIGHT   #Y
               ): 
                self.bullets.remove(bullet)
                rem = 1
            for enemy in self.enemies[:]:
                if enemy.collides_with(bullet["pos"],25) and rem == 0:
                    print("Bullet hit an enemy!")
                    self.score += random.randint(6,23)
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    break
            
        
        # Spawn enemies
        self.spawn_rate = max(270, 2200 - int(self.score // 10) * SPAWNRATE) #MORE SPAWNRATE MAKES THE GAME HARDER
        self.spawn_timer += dt * 1000
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer -= self.spawn_rate
            if random.randint(0,1) == 0:  # X
                x = random.randint(0,1) * SCREEN_WIDTH
                y= random.randint(0,SCREEN_HEIGHT)
                if x == 0: 
                    self.flip = 1
                else: self.flip = 0
            else:                         # Y
                x = random.randint(0, SCREEN_WIDTH)
                y= random.randint(0,1) * SCREEN_HEIGHT
                if(x > SCREEN_WIDTH/2):
                    self.flip = 0
                else: self.flip = 1 
                
            speed = random.randint(120, 170) + int(self.score // 35)
            if self.bullet_speed_timer > 0:
                speed = speed/2
            if random.randint(0,1):
                if self.flip == 0: self.enemies.append(Enemy(x, y, speed, self.shark_frames2))
                else :
                    self.enemies.append(Enemy(x, y, speed, self.shark_frames2_rev))
            else: 
                if self.flip == 0: self.enemies.append(Enemy(x, y, speed, self.shark_frames))
                else :
                    self.enemies.append(Enemy(x, y, speed, self.shark_frames_rev))
            print(f"Enemy spawned at {x} , {y} , speed: {speed}")
            
         
        # Power-up spawn logic
        self.power_up_spawn_timer += dt
        if self.power_up_spawn_timer >= self.power_up_spawn_rate:
            self.power_up_spawn_timer = 0
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = -30  # Spawn slightly above the screen
            if self.health == HEALTH :
                power_type = random.randint(1, 3)  # Randomize type - wont spawn health if full HP
            else: power_type = random.randint(1, 4)
            self.power_ups.append(PowerUp(x, y, power_type))
            print(f"Drawing Power-Up: Type= {power_type}")
            
        # Shield effect
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_timer = 0
                print("Shield expired!")

        # Acceleration
        if self.bullet_speed_timer > 0:
            self.bullet_speed_timer -= dt
            if self.bullet_speed_timer <= 0:
                self.bullet_speed_multiplier = 1  # Reset bullet speed
                self.speed = SPEED # Reset speed
                print("Bullet speed boost expired!")

        
        # Check for power-up collisions
        for power_up in self.power_ups[:]:
            power_up.update(dt)
            if power_up.collides_with(self.player_pos, self.player_radius):
                print(f"Collected Power-Up: {power_up.type}")
                if power_up.type == 1:  # Shield
                    self.shield_timer = 5  # Shield lasts for 5 seconds
                    sound = pygame.mixer.Sound("Assets/Music/Shield.mp3")
                    sound.set_volume(0.20)
                    sound.play()
                    
                elif power_up.type == 2:  # Bullet Speed
                    self.bullet_speed_timer = 7  # Faster bullets for 7 seconds
                    self.bullet_speed_multiplier = 1.8
                    self.speed = SPEED + 150 # Faster movement
                    sound = pygame.mixer.Sound("Assets/Music/Boost.mp3")
                    sound.set_volume(0.30)
                    sound.play()                    
                    
                elif power_up.type == 3:  # Bonus coins 
                    self.score += random.randint(300,500)
                    sound = pygame.mixer.Sound("Assets/Music/Bonus.mp3")
                    sound.set_volume(0.20)
                    sound.play()
                    
                elif power_up.type == 4:  # Health Up
                    self.health = min(self.health + 1, HEALTH)  # Max health is 3
                    sound = pygame.mixer.Sound("Assets/Music/Health.mp3")
                    sound.set_volume(0.40)
                    sound.play()
                    
                self.power_ups.remove(power_up)
                
        # Move enemies
        for enemy in self.enemies:
            enemy.move_towards(self.player_pos, dt)
            enemy.update(dt)
            if enemy.collides_with((self.player_pos.x+40,self.player_pos.y+40), self.player_radius -5) and self.shield_timer == 0:
                sound = pygame.mixer.Sound("Assets/Music/Hit.mp3")
                sound.set_volume(0.30)
                sound.play()
                print(f"Enemy hit the player HP: {self.health -1}")
                self.health -=1
                self.enemies.remove(enemy)

    def render(self, screen):
        """Render gameplay elements."""
        screen.blit(self.background, (0, 0))
        screen.blit(self.hero,(self.player_pos))
        
        # Display score
        font = pygame.font.Font("Assets/Font/soupofjustice.ttf", 74)
        text = font.render(f"Score: {int(self.score)}", True, "white")
        screen.blit(text, (SCREEN_WIDTH // 2.5, SCREEN_HEIGHT // 12.9))
        
        # Draw & Flip hero sprite
        if self.facing_right == False:
            self.hero_right.set_alpha(0)
            self.hero.set_alpha(255)
            screen.blit(self.hero, self.player_pos)
        else:
            self.hero_right.set_alpha(255)
            self.hero.set_alpha(0)
            screen.blit(self.hero_right, self.player_pos)
            
        #Draw shield
        if self.shield_timer > 0:
            screen.blit(self.shield,(self.player_pos.x - 20, self.player_pos.y - 20))
        
        #Display HP
        health_text = font.render(f"Health: {self.health}", True,"red")
        screen.blit(health_text, (20,20))
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.render(screen)
        
        # Draw bullets
        for bullet in self.bullets:
            screen.blit(self.bubble , bullet["pos"])
            
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.render(screen)


# Game over State        
class GameoverState(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.finalScore =0
        self.background = pygame.image.load("Assets/Sprites/MainBackground.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
    def handle_events(self):
        """Handle gameplay-specific events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                self.manager.change_state("menu")
    
    def render(self, screen):
        """Render pause screen."""
        screen.blit(self.background, (0,0))
        font = pygame.font.Font("Assets/Font/soupofjustice.ttf", 150)
        HIGHSCORE = config["HIGHSCORE"]
        if (HIGHSCORE < self.finalScore): 
            write_to_JSON("HIGHSCORE", self.finalScore)
        if (HIGHSCORE <= self.finalScore):
            text = font.render("NEW HIGH SCORE!!",True,"red")
            screen.blit(text, ((SCREEN_WIDTH // 6.7)-100, SCREEN_HEIGHT // 40))
        text = font.render("Game over!", True, "black")
        screen.blit(text, ((SCREEN_WIDTH // 4)-50, SCREEN_HEIGHT // 5.7))
        text = font.render(f"Your score: {self.finalScore}",True, "black")
        screen.blit(text, ((SCREEN_WIDTH // 9) -20, SCREEN_HEIGHT // 3.2))
        text = font.render(f"Highscore: {HIGHSCORE}",True,"black")
        screen.blit(text, ((SCREEN_WIDTH // 9) -20, SCREEN_HEIGHT // 2))
        font = pygame.font.Font("Assets/Font/soupofjustice.ttf", 70)
        text = font.render("Press B to go back to menu", True ,"black")
        screen.blit(text, ((SCREEN_WIDTH // 4)-100, SCREEN_HEIGHT // 1.2))
        

# Pause State
class PauseState(GameState):
    def handle_events(self):
        """Handle pause-specific events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.change_state("gameplay",0.1)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                self.manager.change_state("menu")

    def render(self, screen):
        """Render pause screen."""
        self.background = pygame.image.load("Assets/Sprites/MainBackground.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(self.background, (0,0))
        font = pygame.font.Font("Assets/Font/soupofjustice.ttf", 74)
        text = font.render("Paused - Press ESC to Resume", True, "white")
        screen.blit(text, ((SCREEN_WIDTH // 5.5)-50, SCREEN_HEIGHT // 2.4))
        text = font.render("Press B to go back to menu", True ,"white")
        screen.blit(text, ((SCREEN_WIDTH // 5.5)-50, SCREEN_HEIGHT // 1.9))


# Menu State
class MenuState(GameState): 
    def __init__(self, manager):
        super().__init__(manager)
        self.options = ["Start Game", "Options", "Quit"]
        self.current_option = 0
        self.background = pygame.image.load("Assets/Sprites/MainBackground.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.current_option = (self.current_option + 1) % len(self.options)
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.current_option = (self.current_option - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.current_option == 0:  # Start Game
                        self.manager.change_state("gameplay")
                    elif self.current_option ==1:
                        self.manager.change_state("options", 0.1)
                    elif self.current_option == 2:  # Quit
                        self.manager.running = False

    def render(self, screen):
        screen.blit(self.background, (0,0))
        font = pygame.font.Font("Assets/Font/soupofjustice.ttf", 74)
        for i, option in enumerate(self.options):
            color = "white" if i == self.current_option else "gray"
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4 + i * 100))


# Options State
class OptionsState(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.options = [f"Music: {DEFAULTVOLUME}%", "Fullscreen: OFF", "Back to Menu"]
        self.current_option = 0
        self.volume = DEFAULTVOLUME  # Starting volume
        self.fullscreen = False
        self.background = pygame.image.load("Assets/Sprites/MainBackground.png")
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def handle_events(self):
        """Handle input for the options menu."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.running = False

            elif event.type == pygame.KEYDOWN:
                # Navigate options
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.current_option = (self.current_option + 1) % len(self.options)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.current_option = (self.current_option - 1) % len(self.options)

                # Select option with ENTER
                elif event.key == pygame.K_RETURN:
                    self.select_option()

                # Adjust volume only if the "Volume" option is selected
                elif self.current_option == 0:
                    if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_RIGHT, pygame.K_d):
                        self.volume = min(100, self.volume + 5)
                        pygame.mixer.music.set_volume(self.volume / 100)
                        print(f"Volume increased: {self.volume}%")
                        self.options[0] = f"Music: {self.volume}%"
                        write_to_JSON("Volume", self.volume)
                        DEFAULTVOLUME = self.volume
                    elif event.key in (pygame.K_MINUS, pygame.K_LEFT, pygame.K_a):
                        self.volume = max(0, self.volume - 5)
                        pygame.mixer.music.set_volume(self.volume / 100)
                        print(f"Volume decreased: {self.volume}%")
                        self.options[0] = f"Music: {self.volume}%"
                        write_to_JSON("Volume", self.volume)
                        DEFAULTVOLUME = self.volume


    def select_option(self):
        """Execute the selected option."""
        if self.current_option == 1:  # Fullscreen toggle
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                self.options[1] = "Fullscreen: ON"
                print("Fullscreen: ON")
            else:
                pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.options[1] = "Fullscreen: OFF"
                print("Fullscreen: OFF")
                
        elif self.current_option == 2:  # Back to menu
            self.manager.change_state("menu", fade_duration=0.5)

    def render(self, screen):
        """Render the options menu."""
        screen.blit(self.background, (0,0))
        font = pygame.font.Font("Assets/Font/soupofjustice.ttf", 74)
        for i, option in enumerate(self.options):
            color = "white" if i == self.current_option else "gray"
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4 + i * 100))




# Game Manager
class GameManager:
    def __init__(self):
        # Setting up pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GlugluShooter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0 #Delta time - time not related to frames
        
        # Initialize background music
        try:
            # Load and play background music
            pygame.mixer.music.load("Assets/Music/pokemonBackgroundMusic.mp3")
            pygame.mixer.music.play(loops=-1)
            pygame.mixer.music.set_volume(DEFAULTVOLUME/100)
        except pygame.error as e:
            print(f"Error loading background music: {e}")
        time.sleep(0.1)  # Small delay to ensure music has started

        if not pygame.mixer.music.get_busy():
            print("Music is not playing!")
        else:
            print("Music is playing correctly.")
            
        # Making starting fade
        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill("black")
        self.fade_alpha = 0

        # Initialize states
        self.states = {
            "gameplay": GameplayState(self),
            "pause": PauseState(self),
            "menu" : MenuState(self),
            "options" : OptionsState(self),
            "over" : GameoverState(self)
        }
        
        self.current_state = self.states["menu"]
        print("-----------------------------------------------------")
    def fade_to_black(self, duration):
        """perform a fade-to-black transition"""
        fade_time = 0
        while fade_time< duration:
            fade_time += self.clock.tick(FPS) /1000
            self.fade_alpha = min(255, int(255*(fade_time/ duration)))
            self.fade_surface.set_alpha(self.fade_alpha)
            self.current_state.render(self.screen)
            self.screen.blit(self.fade_surface, (0,0)) #Fade overlay
            pygame.display.flip()

    def change_state(self, state_name, fade_duration =0.7):
        """Switch to a different game state."""
        self.fade_to_black(fade_duration)
        
        if isinstance(self.current_state, PauseState) and state_name == "menu":
            gameplay_state = self.states["gameplay"]
            gameplay_state.player_pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        
        print(f"| From-{type(self.current_state).__name__} Jumped to-{state_name}  |")
        
        if state_name == "gameplay":
            if isinstance(self.current_state, MenuState):
                self.states["gameplay"].game_reset()
            self.states["gameplay"].activate_clock()
        else:
            self.states["gameplay"].deactivate_clock()
            
        if state_name == "over":
            if isinstance(self.current_state, GameplayState):
                self.states["over"].finalScore = int(self.states["gameplay"].get_score())
        
        self.current_state = self.states[state_name]

    def run(self):
        """Main game loop."""
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.current_state.handle_events()
            self.current_state.update(self.dt)
            self.current_state.render(self.screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    game = GameManager()
    game.run()
    