import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 650
GROUND_HEIGHT = 100

# Colors
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (245, 247, 250)  # Very light gray-blue (light background)
GRAY_TEXT = (107, 114, 128)  # #6b7280 neutral gray text
PIPE_COLOR = (30, 144, 255)  # Dodger blue for pipes (clean and bold)
BIRD_COLOR = (0, 0, 0)       # Black bird with subtle shadow
SHADOW_COLOR = (0, 0, 0, 50) # Semi-transparent for shadows

# Fonts
FONT_LARGE = pygame.font.SysFont("Segoe UI", 48, bold=True)
FONT_MEDIUM = pygame.font.SysFont("Segoe UI", 24, bold=True)
FONT_SMALL = pygame.font.SysFont("Segoe UI", 18)

FPS = 60
GRAVITY = 0.5
FLAP_POWER = -10
PIPE_SPEED = 3
PIPE_GAP = 160
PIPE_FREQUENCY = 1500  # milliseconds


# Utility to draw rounded rect with anti-aliasing effect
def draw_rounded_rect(surface, rect, color, radius=12):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), border_radius=radius)
    surface.blit(shape_surf, rect)


class Bird:
    RADIUS = 18

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.alive = True
        self.rect = pygame.Rect(self.x - self.RADIUS, self.y - self.RADIUS, self.RADIUS*2, self.RADIUS*2)

    def flap(self):
        if self.alive:
            self.velocity = FLAP_POWER

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.center = (self.x, self.y)
        # Restrict going above screen
        if self.y < self.RADIUS:
            self.y = self.RADIUS
            self.velocity = 0
        # Death by falling on ground handled externally

    def draw(self, surface):
        # Shadow (soft)
        shadow_pos = (self.x + 3, self.y + 5)
        shadow_surf = pygame.Surface((self.RADIUS*2+6, self.RADIUS*2+6), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0,0,0,50), (self.RADIUS+3, self.RADIUS+3), self.RADIUS)
        surface.blit(shadow_surf, (shadow_pos[0]-self.RADIUS-3, shadow_pos[1]-self.RADIUS-3))
        # Bird circle
        pygame.draw.circle(surface, BIRD_COLOR, (int(self.x), int(self.y)), self.RADIUS)


class Pipe:
    WIDTH = 70

    def __init__(self, x):
        self.x = x
        self.height = random.randint(150, SCREEN_HEIGHT - GROUND_HEIGHT - PIPE_GAP - 150)
        self.top_rect = pygame.Rect(self.x, 0, self.WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, self.WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - self.height - PIPE_GAP)
        self.passed = False  # Has the bird passed this pipe?

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = int(self.x)
        self.bottom_rect.x = int(self.x)

    def draw(self, surface):
        # Draw top pipe with rounded corners bottom corners radius
        draw_rounded_rect(surface, self.top_rect, PIPE_COLOR, radius=12)
        # Draw bottom pipe with rounded corners top corners radius
        draw_rounded_rect(surface, self.bottom_rect, PIPE_COLOR, radius=12)


def draw_ground(surface):
    ground_rect = pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
    pygame.draw.rect(surface, (230, 230, 230), ground_rect)  # light surface for ground
    # subtle shadow line at top of ground for separation
    pygame.draw.line(surface, (200, 200, 200), (0, SCREEN_HEIGHT - GROUND_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT), 2)


def show_text(surface, text, font, color, center):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, rect)


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird - Minimal Elegant UI")
    clock = pygame.time.Clock()
    running = True

    bird = Bird(100, SCREEN_HEIGHT//2)
    pipes = []
    spawn_pipe_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_pipe_event, PIPE_FREQUENCY)
    score = 0

    game_active = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if game_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.flap()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        bird.flap()
                if event.type == spawn_pipe_event:
                    pipes.append(Pipe(SCREEN_WIDTH + 10))
            else:
                # Game over screen input
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    # Reset game
                    bird = Bird(100, SCREEN_HEIGHT//2)
                    pipes.clear()
                    score = 0
                    game_active = True

        if game_active:
            bird.update()

            # Update pipes
            for pipe in pipes:
                pipe.update()

            # Remove pipes off screen
            pipes = [pipe for pipe in pipes if pipe.x + Pipe.WIDTH > 0]

            # Check collision with pipes
            for pipe in pipes:
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_active = False
                # Score increment
                if not pipe.passed and pipe.x + Pipe.WIDTH < bird.x:
                    pipe.passed = True
                    score += 1

            # Check collision with ground
            if bird.y + bird.RADIUS > SCREEN_HEIGHT - GROUND_HEIGHT:
                game_active = False

        # Drawing
        screen.fill(BACKGROUND_COLOR)

        # Pipes
        for pipe in pipes:
            pipe.draw(screen)

        # Ground
        draw_ground(screen)

        # Bird
        bird.draw(screen)

        # Score display top center
        show_text(screen, str(score), FONT_LARGE, GRAY_TEXT, (SCREEN_WIDTH // 2, 80))

        # If game over
        if not game_active:
            # translucent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            screen.blit(overlay, (0, 0))

            # Game over text
            show_text(screen, "Game Over", FONT_LARGE, (80, 80, 80), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            show_text(screen, f"Score: {score}", FONT_MEDIUM, (80, 80, 80), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            show_text(screen, "Press Space or Click to Restart", FONT_SMALL, (107, 114, 128), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

