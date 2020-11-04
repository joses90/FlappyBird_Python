import pygame as ga
import sys, random

# Function to draw the floor by joining two floors side by side
def draw_floor():
    screen.blit(floor_surface,(floor_x_pos,450))
    screen.blit(floor_surface,(floor_x_pos + 288,450))

# Take the height of a pipe and create the bottom and top pipe for it
def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop = (350,random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (350,random_pipe_pos - 150))
    return bottom_pipe,top_pipe

# Move the pipes each turn and remove them from the list if they are outside
# of the screen at the left
def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 2.5
    visible_pipes = [pipe for pipe in pipes if pipe.right > -25]
    return visible_pipes

# For each pipe, if it is a bottom one, draw it and if it is a top one,
# flip it and draw it
def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 512:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = ga.transform.flip(pipe_surface,False,True)
            screen.blit(flip_pipe, pipe)

# If the bird collides with a pipe, return false and play a sound. Same if it
# hits the bottom or top of the screen. Else, return true
def check_collision(pipes):
    global can_score
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            death_sound.play()
            can_score = True
            return False
            
    if bird_rect.top <= -50 or bird_rect.bottom >= 450:
        death_sound.play()
        can_score = True
        return False
    
    return True

# Rotate the bird a certain amount
def rotate_bird(bird):
    new_bird = ga.transform.rotozoom(bird,-bird_movement*3,1)
    return new_bird

# Change the bird image and rectangle to show it flap
def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center = (50,bird_rect.centery))
    return new_bird, new_bird_rect

# Display the score if you are playing and both the score and the high score
# when you lose a game
def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)),True,(255,255,255))
        score_rect = score_surface.get_rect(center = (144,50))
        screen.blit(score_surface,score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}' ,True,(255,255,255))
        score_rect = score_surface.get_rect(center = (144,50))
        screen.blit(score_surface,score_rect)
        
        high_score_surface = game_font.render(f'High score: {int(high_score)}',True,(255,255,255))
        high_score_rect = high_score_surface.get_rect(center = (144,425))
        screen.blit(high_score_surface,high_score_rect)

# If the score is bigger than the high score, update it
def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score

# Increase the score by 1 when surpassing a pipe
def pipe_score_check():
    global score, can_score
    
    if pipe_list:
        for pipe in pipe_list:
            if 47.5 < pipe.centerx < 52.5 and can_score:
                score += 1
                score_sound.play()
                can_score = False
            if pipe.centerx < 0:
                can_score = True

#ga.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512)
# Initialise pygame, the screen size to be used, a clock and the game font
ga.init()
screen = ga.display.set_mode((288,512))
clock = ga.time.Clock()
game_font = ga.font.Font('04B_19.TTF',20)

## Game variables
# How fast the bird falls each turn
gravity = 0.125
# The vertical movement of the bird
bird_movement = 0
# Is the game going on or is it over?
game_active = True
# Initialise the score and high score
score = 0
high_score = 0
can_score = True

# Create background surface
bg_surface = ga.image.load('assets/background-day.png').convert()
#bg_surface = ga.transform.scale2x(bg_surface)

# Create floor surface
floor_surface = ga.image.load('assets/base.png').convert()
floor_x_pos = 0

# Create one bird surface per flap position and store them in a list. Also,
# create a rectangle for the bird
bird_downflap = ga.image.load('assets/bluebird-downflap.png').convert_alpha()
bird_midflap = ga.image.load('assets/bluebird-midflap.png').convert_alpha()
bird_upflap = ga.image.load('assets/bluebird-upflap.png').convert_alpha()
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center = (50,256))

# Create an event for flaps
BIRDFLAP = ga.USEREVENT + 1
ga.time.set_timer(BIRDFLAP,100)

# Variance where no flapping is recorded and the bird image is the same always
# bird_surface = ga.image.load('assets/bluebird-midflap.png').convert_alpha()
# bird_rect = bird_surface.get_rect(center = (50,256))

# Create a pipe surface
pipe_surface = ga.image.load('assets/pipe-green.png').convert()
pipe_list = []
# Create a pipe event to randomise the height of the pipe from a list
SPAWNPIPE = ga.USEREVENT
ga.time.set_timer(SPAWNPIPE,1200)
pipe_height = [200, 300, 400]

# Create a game over message
game_over_surface = ga.image.load('assets/message.png').convert_alpha()
game_over_rect = game_over_surface.get_rect(center = (144,256))

# Create the sounds for flapping, colliding and scoring points
flap_sound = ga.mixer.Sound('sound/sfx_wing.wav')
death_sound = ga.mixer.Sound('sound/sfx_hit.wav')
score_sound = ga.mixer.Sound('sound/sfx_point.wav')
score_sound_countdown = 100

# Game loop
while True:
    # Check which event happens
    for event in ga.event.get():
        # If the closing x button is pressed, close the game
        if event.type == ga.QUIT:
            ga.quit()
            sys.exit()
        # If a key is pressed
        if event.type == ga.KEYDOWN:
            # If the key is the spacebar and the game is on, stop the bird
            # vertical movement momentarily and move it up. Also, play a
            # flapping sound
            if event.key == ga.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 6
                flap_sound.play()
            # If the key is the spacebar and the game is over, start the game,
            # clear the list of pipes, reinitialise the position, rectangle and
            # center of the bird. Also, restart the score
            if event.key == ga.K_SPACE and game_active == False:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (50,256)
                bird_movement = 0
                score = 0

        # Create pipes
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())
        
        # Change the bird image
        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0
                
            bird_surface, bird_rect = bird_animation()
    
    # Draw background
    screen.blit(bg_surface,(0,0))
    
    # Draw surfaces only if game is active
    if game_active:
        # Bird
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird,bird_rect)
        game_active = check_collision(pipe_list)
        
        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
        
        # Score
        pipe_score_check()
        score_display('main_game')

    # Draw game over score
    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game_over')
    
    # Floor is shown independetky if the game is on or not
    floor_x_pos -= 0.5
    draw_floor()
    # Since it is moving to the left, at certain point, its position is reset
    # to show continuity
    if floor_x_pos <= -288:
        floor_x_pos = 0
    
    # Update the display with the previous instructions and use the clock
    ga.display.update()
    clock.tick(120)

# Close pygame
ga.quit()
