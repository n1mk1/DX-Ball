import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Paddle dimensions
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
PADDLE_SPEED = 10

# Ball dimensions
BALL_SIZE = 10
BALL_SPEED = 5

# Brick dimensions
BRICK_WIDTH = 75
BRICK_HEIGHT = 20

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DX Ball")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Paddle (move it a little higher)
paddle = pygame.Rect((SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 100), (PADDLE_WIDTH, PADDLE_HEIGHT))

# Ball
ball = pygame.Rect((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (BALL_SIZE, BALL_SIZE))
ball_dx = BALL_SPEED * random.choice([-1, 1])
ball_dy = -BALL_SPEED

# Bricks and hexcode values
bricks = [pygame.Rect((x * (BRICK_WIDTH + 5) + 35, y * (BRICK_HEIGHT + 5) + 35), (BRICK_WIDTH, BRICK_HEIGHT))
          for y in range(5) for x in range(10)]
brick_colors = ["#{:06x}".format(random.randint(0, 0xFFFFFF)) for _ in bricks]

# Target hexcode
target_hexcode = "#{:06x}".format(random.randint(0, 0xFFFFFF))
print(f"Target Hexcode: {target_hexcode}")

# Broken bricks list (tracking broken bricks' colors)
broken_bricks = []

def draw_objects():
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    for brick, color in zip(bricks, brick_colors):
        pygame.draw.rect(screen, pygame.Color(color), brick)
    
    # Display broken bricks count as a stack on the right side
    font = pygame.font.Font(None, 30)
    broken_text = font.render(f"Broken: {len(broken_bricks)}", True, WHITE)
    screen.blit(broken_text, (SCREEN_WIDTH - 150, 20))

    for i, hexcode in enumerate(reversed(broken_bricks)):
        hex_text = font.render(hexcode, True, WHITE)
        screen.blit(hex_text, (SCREEN_WIDTH - 150, 40 + i * 30))

    # Display target hexcode
    target_text = font.render(f"Target: {target_hexcode}", True, WHITE)
    screen.blit(target_text, (300, SCREEN_HEIGHT -20))

    # Display target hexcode color in the bottom middle
    target_color = pygame.Color(target_hexcode)
    target_color_rect = pygame.Rect(SCREEN_WIDTH // 2 -200, SCREEN_HEIGHT - 80, 100, 50)
    pygame.draw.rect(screen, target_color, target_color_rect)
    pygame.draw.rect(screen, WHITE, target_color_rect, 2)  # Add a border for visibility

    # Display summed hexcode and its color
    if broken_bricks:
        summed_hexcode = add_hexcodes(broken_bricks)
        similarity = calculate_similarity(summed_hexcode, target_hexcode)
        summed_text = font.render(f"Summed Hex: {summed_hexcode}", True, WHITE)
        similarity_text = font.render(f"Similarity: {similarity:.2f}%", True, WHITE)
        screen.blit(summed_text, (SCREEN_WIDTH - 500, SCREEN_HEIGHT - 20))
        screen.blit(similarity_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 50))

        # Display summed hexcode color next to the target hexcode
        summed_color = pygame.Color(summed_hexcode)
        summed_color_rect = pygame.Rect(SCREEN_WIDTH // 2 + 60, SCREEN_HEIGHT - 80, 100, 50)
        pygame.draw.rect(screen, summed_color, summed_color_rect)
        pygame.draw.rect(screen, WHITE, summed_color_rect, 2)  # Add a border for visibility

def move_paddle():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.move_ip(-PADDLE_SPEED, 0)
    if keys[pygame.K_RIGHT] and paddle.right < SCREEN_WIDTH:
        paddle.move_ip(PADDLE_SPEED, 0)

def move_ball():
    global ball_dx, ball_dy
    ball.move_ip(ball_dx, ball_dy)

    # Ball collision with walls
    if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
        ball_dx = -ball_dx
    if ball.top <= 0:
        ball_dy = -ball_dy

    # Ball collision with paddle
    if ball.colliderect(paddle):
        ball_dy = -BALL_SPEED

    # Ball collision with bricks
    for i, brick in enumerate(bricks[:] ):
        if ball.colliderect(brick):
            broken_bricks.append(brick_colors[i])
            bricks.remove(brick)
            brick_colors.pop(i)
            ball_dy = -ball_dy
            break

def hex_to_rgb(hexcode):
    return tuple(int(hexcode[i:i+2], 16) for i in (1, 3, 5))

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def add_hexcodes(hexcodes):
    if not hexcodes:
        return "#000000"  # Default to black if no bricks are broken

    total_rgb = [0, 0, 0]
    
    for hexcode in hexcodes:
        rgb = hex_to_rgb(hexcode)
        total_rgb = [total_rgb[i] + rgb[i] for i in range(3)]

    # Normalize by dividing by the number of bricks broken
    num_bricks = len(hexcodes)
    avg_rgb = [min(255, total_rgb[i] // num_bricks) for i in range(3)]

    return rgb_to_hex(tuple(avg_rgb))


def calculate_similarity(hex1, hex2):
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    difference = sum(abs(rgb1[i] - rgb2[i]) for i in range(3))
    max_difference = 255 * 3
    return 100 * (1 - difference / max_difference)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    move_paddle()
    move_ball()

    # Check if the ball falls below the screen
    if ball.bottom >= SCREEN_HEIGHT:
        summed_hexcode = add_hexcodes(broken_bricks)
        similarity = calculate_similarity(summed_hexcode, target_hexcode)
        print("Game Over!")
        print(f"Summed Hexcode: {summed_hexcode}")
        print(f"Similarity to Target: {similarity:.2f}%")
        running = False
        
    # Check if all bricks are broken
    if not bricks:
        print("You Win!")
        running = False

    # Check if broken bricks' summed hexcodes match the target
    summed_hexcode = add_hexcodes(broken_bricks)  # Update summed_hexcode here.
    if summed_hexcode == target_hexcode:
        print("You Matched the Target Hexcode! You Win!")
        running = False

    draw_objects()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
