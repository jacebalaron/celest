import pygame
import random
import time

fine = False
inAir = False
cyan = (41, 173, 255, 255)
checkPoint = 0


class Ground(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0):
        pygame.sprite.Sprite.__init__(self)
        # Load the image with alpha channel
        original_image = pygame.image.load("ground.png").convert_alpha()

        # Get original dimensions
        original_width = original_image.get_width()
        original_height = original_image.get_height()

        # Scale down the image
        scale_factor = 0.5
        new_width = int(original_width)
        new_height = int(original_height * scale_factor)

        # Create the scaled image
        self.image = pygame.transform.scale(original_image, (new_width, new_height))

        # Get the rectangle for the scaled image and position it
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Spike(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0):
        pygame.sprite.Sprite.__init__(self)
        # Load the image with alpha channel
        original_image = pygame.image.load("spike.png").convert_alpha()

        # Get original dimensions
        original_width = original_image.get_width()
        original_height = original_image.get_height()

        # Scale down the image
        scale_factor = 0.5
        scale_factor_x = 0.5
        new_width = int(original_width * scale_factor_x)
        new_height = int(original_height * scale_factor)

        # Create the scaled image
        self.image = pygame.transform.scale(original_image, (new_width, new_height))

        # Get the rectangle for the scaled image and position it
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Wall(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0):
        pygame.sprite.Sprite.__init__(self)
        # Load the image with alpha channel
        original_image = pygame.image.load("wall.png").convert_alpha()

        # Get original dimensions
        original_width = original_image.get_width()
        original_height = original_image.get_height()

        # Scale down the image
        scale_factor = 0.05
        scale_factor_y = 0.235
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor_y)

        # Create the scaled image
        self.image = pygame.transform.scale(original_image, (new_width, new_height))

        # Get the rectangle for the scaled image and position it
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def setHeight(self, height):
        original_image = pygame.image.load("wall.png").convert_alpha()
        original_width = original_image.get_width()
        scale_factor = 0.1
        new_width = int(original_width * scale_factor)
        self.image = pygame.transform.scale(original_image, (new_width, height))


class DisBlock(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0):
        pygame.sprite.Sprite.__init__(self)
        self.original_images = {
            0: pygame.transform.scale(pygame.image.load("disintegratingBlock1.png").convert_alpha(), (40, 40)),
            1: pygame.transform.scale(pygame.image.load("disintegratingBlock2.png").convert_alpha(), (40, 40)),
        }
        self.empty_image = pygame.Surface((40, 40), pygame.SRCALPHA)

        self.image = self.original_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.player_on_block = False
        self.disintegration_started = False
        self.start_time = 0
        self.stage = 0  # 0: solid, 1: cracking, 2: disintegrated
        self.active = True  # For collision

    def update(self):
        current_time = time.time()

        if self.disintegration_started:
            elapsed = current_time - self.start_time

            if self.stage == 0 and elapsed > 1:
                self.stage = 1
                self.image = self.original_images[1]

            elif self.stage < 2 and elapsed > 3:
                self.stage = 2
                self.image = self.empty_image  # Invisible
                self.active = False  # Disable collision
                self.start_time = current_time  # Restart timer for respawn

            elif self.stage == 2 and elapsed > 3:
                self.stage = 0
                self.image = self.original_images[0]
                self.active = True  # Re-enable collision
                self.disintegration_started = False

    def start_disintegration(self):
        if not self.disintegration_started and self.stage == 0:
            self.disintegration_started = True
            self.start_time = time.time()

    def player_contact(self, is_above):
        self.player_on_block = is_above
        if is_above:
            self.start_disintegration()

    def reset_contact(self):
        self.player_on_block = False


class Player(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0):
        pygame.sprite.Sprite.__init__(self)
        # Load the image with alpha channel
        original_image = pygame.image.load("playerStop.png").convert_alpha()

        # Get original dimensions
        original_width = original_image.get_width()
        original_height = original_image.get_height()

        # Scale down the image
        scale_factor = 0.5
        scale_factor_x = 0.5
        new_width = int(original_width * scale_factor_x)
        new_height = int(original_height * scale_factor)

        # Create the scaled image
        self.image = pygame.transform.scale(original_image, (new_width, new_height))

        # Get the rectangle for the scaled image and position it
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Movement variables
        self.speed = 5
        self.dash_left = False
        self.dash_right = False
        self.jump_power = -12
        self.gravity = 0.5
        self.velocity_y = 0
        self.dash = False
        self.on_ground = False

        # Initialize time tracking variables
        self.start = time.time()
        self.end = time.time()

        # Track which disintegrating block the player is on
        self.current_dis_block = None

    def update(self, ground_group, wall_group, spike_group, disBlock_group):
        # Store the previous position for collision resolution
        prev_x = self.rect.x
        prev_y = self.rect.y

        # Get keyboard input
        keys = pygame.key.get_pressed()

        # Horizontal movement
        if keys[pygame.K_LEFT] and not self.dash_left and not self.dash_right:
            self.rect.x -= self.speed
            self.image = pygame.image.load("playerLeft.png").convert_alpha()
            original_width = self.image.get_width()
            original_height = self.image.get_height()
            scale_factor = 0.5
            scale_factor_x = 0.5
            new_width = int(original_width * scale_factor_x)
            new_height = int(original_height * scale_factor)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
        elif keys[pygame.K_RIGHT] and not self.dash_left and not self.dash_right:
            self.rect.x += self.speed
            self.image = pygame.image.load("playerRight.png").convert_alpha()
            original_width = self.image.get_width()
            original_height = self.image.get_height()
            scale_factor = 0.5
            scale_factor_x = 0.5
            new_width = int(original_width * scale_factor_x)
            new_height = int(original_height * scale_factor)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
        elif self.on_ground and not self.dash_left and not self.dash_right:
            self.image = pygame.image.load("playerStop.png").convert_alpha()
            original_width = self.image.get_width()
            original_height = self.image.get_height()
            scale_factor = 0.5
            scale_factor_x = 0.5
            new_width = int(original_width * scale_factor_x)
            new_height = int(original_height * scale_factor)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))

        # Apply gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Reset disintegrating block tracking before collision check
        self.current_dis_block = None

        # Mark all disintegrating blocks as not being stood on
        for disBlock in disBlock_group:
            disBlock.reset_contact()

        # Handle collisions with ground
        self.on_ground = False
        for ground in ground_group:
            if self.rect.colliderect(ground.rect):
                # Check if we're falling (coming from above)
                if self.velocity_y > 0 and prev_y + self.rect.height <= ground.rect.top + 10:
                    self.rect.bottom = ground.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                # Coming from below (hitting head)
                elif self.velocity_y < 0 and prev_y >= ground.rect.bottom - 10:
                    self.rect.top = ground.rect.bottom
                    self.velocity_y = 0
                # Coming from the sides
                else:
                    # From the left
                    if prev_x + self.rect.width <= ground.rect.left + 10:
                        self.rect.right = ground.rect.left
                    # From the right
                    elif prev_x >= ground.rect.right - 10:
                        self.rect.left = ground.rect.right

        # Handle collisions with disintegrating blocks
        for disBlock in disBlock_group:
            if self.rect.colliderect(disBlock.rect):
                # Check if we're falling (coming from above)
                if self.velocity_y > 0 and prev_y + self.rect.height <= disBlock.rect.top + 10:
                    self.rect.bottom = disBlock.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    # Mark this specific block as being stood on
                    disBlock.player_contact(True)
                    self.current_dis_block = disBlock
                # Coming from below (hitting head)
                elif self.velocity_y < 0 and prev_y >= disBlock.rect.bottom - 10:
                    self.rect.top = disBlock.rect.bottom
                    self.velocity_y = 0
                    disBlock.player_contact(False)
                # Coming from the sides
                else:
                    # From the left
                    if prev_x + self.rect.width <= disBlock.rect.left + 10:
                        self.rect.right = disBlock.rect.left
                        disBlock.player_contact(False)
                    # From the right
                    elif prev_x >= disBlock.rect.right - 10:
                        self.rect.left = disBlock.rect.right
                        disBlock.player_contact(False)

        # Handle collisions with walls
        for wall in wall_group:
            if self.rect.colliderect(wall.rect):
                # Coming from the left
                if prev_x + self.rect.width <= wall.rect.left + 10:
                    self.rect.right = wall.rect.left
                # Coming from the right
                elif prev_x >= wall.rect.right - 10:
                    self.rect.left = wall.rect.right
                # Coming from above
                elif prev_y + self.rect.height <= wall.rect.top + 10:
                    self.rect.bottom = wall.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                # Coming from below
                elif prev_y >= wall.rect.bottom - 10:
                    self.rect.top = wall.rect.bottom
                    self.velocity_y = 0

        # Check spike collisions
        spike_hit = pygame.sprite.spritecollide(self, spike_group, False)
        if spike_hit:
            # Reset player to starting position
            self.rect.x = 100
            self.rect.y = 300
            self.velocity_y = 0

        # Jump when space is pressed
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

        # Handle dash
        if keys[pygame.K_x] and self.dash == False:
            if keys[pygame.K_UP]:
                self.velocity_y = self.jump_power
                self.on_ground = False
                self.dash = True
                self.image = pygame.image.load("playerDash.png").convert_alpha()
                original_width = self.image.get_width()
                original_height = self.image.get_height()
                scale_factor = 0.37
                scale_factor_x = 0.37
                new_width = int(original_width * scale_factor_x)
                new_height = int(original_height * scale_factor)
                self.image = pygame.transform.scale(self.image, (new_width, new_height))
            if keys[pygame.K_LEFT]:
                self.start = time.time()
                self.dash_left = True
                self.image = pygame.image.load("playerDash2.png").convert_alpha()
                original_width = self.image.get_width()
                original_height = self.image.get_height()
                scale_factor = 0.37
                scale_factor_x = 0.37
                new_width = int(original_width * scale_factor_x)
                new_height = int(original_height * scale_factor)
                self.image = pygame.transform.scale(self.image, (new_width, new_height))
            if keys[pygame.K_RIGHT]:
                self.start = time.time()
                self.dash_right = True
                self.image = pygame.image.load("playerDash.png").convert_alpha()
                original_width = self.image.get_width()
                original_height = self.image.get_height()
                scale_factor = 0.37
                scale_factor_x = 0.37
                new_width = int(original_width * scale_factor_x)
                new_height = int(original_height * scale_factor)
                self.image = pygame.transform.scale(self.image, (new_width, new_height))

        # Reset dash if on ground
        if self.on_ground == True and self.dash_left != True and self.dash_right != True:
            self.dash = False

        # Handle dash movement
        self.end = time.time()
        if self.dash_left or self.dash_right:
            if self.start + 0.1 > self.end:
                if self.dash_left == True:
                    self.rect.x -= 10
                if self.dash_right == True:
                    self.rect.x += 10
            else:
                self.gravity = 0.5
                self.dash_right = False
                self.dash_left = False

        # Keep player within screen bounds
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > 460:  # Assuming player width is about 40
            self.rect.x = 460


def main():
    pygame.init()
    canvas = pygame.display.set_mode((500, 500))

    # Fill with cyan initially
    canvas.fill(cyan)

    # Load and scale the background image
    original_back = pygame.image.load('background.png').convert()

    # Get original dimensions
    original_width = original_back.get_width()
    original_height = original_back.get_height()

    # Define scale factors
    scale_factor_width = 1.2  # Increase width by 20%
    scale_factor_height = 1.2  # Increase height by 20%

    # Calculate new dimensions
    new_width = int(original_width * scale_factor_width)
    new_height = int(original_height * scale_factor_height)

    # Scale the background
    back = pygame.transform.scale(original_back, (new_width, new_height))

    pygame.display.set_caption("My Board")
    exit_game = False

    # Create sprite groups for collision detection
    all_sprites = pygame.sprite.Group()
    ground_group = pygame.sprite.Group()
    spike_group = pygame.sprite.Group()
    wall_group = pygame.sprite.Group()
    disBlock_group = pygame.sprite.Group()

    # Create the player and add to sprite group
    player_character = Player(100, 300)

    # Create ground at a specific position
    ground = Ground(0, 350)
    ground2 = Ground(80, 350)
    ground3 = Ground(160, 350)
    ground4 = Ground(242, 390)
    ground5 = Ground(322, 390)
    ground6 = Ground(402, 390)

    # Add ground to the ground group
    ground_group.add(ground, ground2, ground3, ground4, ground5, ground6)

    # Create spikes
    spike = Spike(242, 350)
    spike2 = Spike(285, 350)
    spike3 = Spike(328, 350)
    spike4 = Spike(371, 350)
    spike5 = Spike(414, 350)
    spike6 = Spike(453, 350)

    # Add spikes to the spike group
    spike_group.add(spike, spike2, spike3, spike4, spike5, spike6)

    # Create walls
    wall = Wall(0, 0)
    wall2 = Wall(470, 100)
    wall2.setHeight(335)

    # Add walls to the wall group
    wall_group.add(wall, wall2)

    # Create the disintegrating blocks
    disBlock = DisBlock(350, 200)
    disBlock2 = DisBlock(320, 200)
    disBlock_group.add(disBlock, disBlock2)

    # Add all objects to the main sprite group for rendering
    all_sprites.add(ground_group, spike_group, wall_group, player_character, disBlock_group)

    # Game loop
    clock = pygame.time.Clock()  # Add a clock to control frame rate

    while not exit_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True

        # Update disintegrating blocks
        for block in disBlock_group:
            block.update()

        # Update player with all collision groups
        player_character.update(ground_group, wall_group, spike_group, disBlock_group)

        # Clear the screen with the background (redraw it every frame)
        canvas.fill(cyan)  # First fill with cyan

        # Center the background if it's larger than the screen
        back_rect = back.get_rect(center=(canvas.get_width() // 2, canvas.get_height() // 2.9))
        canvas.blit(back, back_rect)

        # Draw everything
        all_sprites.draw(canvas)

        pygame.display.update()

        # Control the frame rate
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()