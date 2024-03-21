import pygame
import random
import math
import psutil
import copy
import tkinter as tk
from gui import CheckboxWindow

WIDTH = 800
HEIGHT = 600
MIN_RADIUS = 10
MAX_RADIUS = 30
MAX_SPEED = 5
NEW_BALL_RADIUS = 20
NEW_BALL_COLOR = [0, 0, 255] # New ball color -> blue
LINE_COLOR = [255, 0, 0]  # New ball trajectory line color -> red
VELOCITY_SCALAR = 1
COLOR_SCALAR = 1
RADIUS_SCALAR = 1
GRAVITY_SCALAR = psutil.virtual_memory().percent / 100

root = tk.Tk()
gui = CheckboxWindow(root, True, True, True, NEW_BALL_RADIUS, True)
gui.get_bool_vars_on_close()
root.mainloop()

CPU_VELOCITY = gui.cpu_velocity
CPU_COLOR = gui.cpu_color
MEMORY_GRAVITY = gui.memory_gravity
NUM_BALLS = gui.ball_num


class Ball:
    def __init__(self, x, y, radius, color, dx=0, dy=0):
        self.x = x
        self.y = y
        self.start_radius = copy.deepcopy(radius)
        self.radius = copy.deepcopy(radius)
        self.start_color = color[:]
        self.color = color[:]
        self.dx = dx
        self.dy = dy
        self.mass = math.pi * radius ** 2  # Mass based on area

    def update(self):
        self.x += self.dx * VELOCITY_SCALAR
        self.y += self.dy * VELOCITY_SCALAR

        self.radius = self.start_radius * RADIUS_SCALAR
        # BBounce off walls by negating either dx (left and right walls) or dy (top and bottom walls)
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.dx *= -1
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.dx *= -1

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.dy *= -1
        elif self.y + self.radius >= HEIGHT:
            self.y = HEIGHT - self.radius
            self.dy *= -1

        self.color[0] = int(self.start_color[0] * COLOR_SCALAR)
        self.color[1] = int(self.start_color[1] * COLOR_SCALAR)
        self.color[2] = int(self.start_color[2] * COLOR_SCALAR)


    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set program window dimensions
pygame.display.set_caption("Bounce")

# Create initial balls
balls = []
for _ in range(NUM_BALLS):
    x = random.randint(MAX_RADIUS, WIDTH - MAX_RADIUS)
    y = random.randint(MAX_RADIUS, HEIGHT - MAX_RADIUS)
    radius = random.randint(MIN_RADIUS, MAX_RADIUS)
    color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    dx = random.randint(-MAX_SPEED, MAX_SPEED)
    dy = random.randint(-MAX_SPEED, MAX_SPEED)
    ball = Ball(x, y, radius, color, dx, dy)
    balls.append(ball)

# Check collision and update velocities
def handle_collision(ball1, ball2):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    distance = max(math.sqrt(dx ** 2 + dy ** 2), .1)  # Prevent distance = 0 since we divide by it later

    if distance <= ball1.radius + ball2.radius:  # If collision detected
        # Reposition balls to prevent overlap-related bugs:
        angle = math.atan2(dy, dx)
        overlap = (ball1.radius + ball2.radius) - distance
        ball1.x -= overlap * math.cos(angle)
        ball1.y -= overlap * math.sin(angle)
        ball2.x += overlap * math.cos(angle)
        ball2.y += overlap * math.sin(angle)

        #  Update velocities of colliding balls based on initial velocities and their mass (size):
        total_mass = ball1.mass + ball2.mass
        nx = dx / distance
        ny = dy / distance
        # Calculate the tangential vector components
        tangential_x = -ny
        tangential_y = nx
        # Calculate the dot products of velocities with the tangential and normal vectors
        dp_tangent_1 = ball1.dx * tangential_x + ball1.dy * tangential_y
        dp_tangent_2 = ball2.dx * tangential_x + ball2.dy * tangential_y
        dp_normal_1 = ball1.dx * nx + ball1.dy * ny
        dp_normal_2 = ball2.dx * nx + ball2.dy * ny
        # Calculate the scalar values for velocity changes along the normal direction
        m1 = (dp_normal_1 * (ball1.mass - ball2.mass) + 2 * ball2.mass * dp_normal_2) / total_mass
        m2 = (dp_normal_2 * (ball2.mass - ball1.mass) + 2 * ball1.mass * dp_normal_1) / total_mass
        # Update velocities with the combined effects of normal and tangential components
        ball1.dx = tangential_x * dp_tangent_1 + nx * m1
        ball1.dy = tangential_y * dp_tangent_1 + ny * m1
        ball2.dx = tangential_x * dp_tangent_2 + nx * m2
        ball2.dy = tangential_y * dp_tangent_2 + ny * m2

def apply_gravity(ball1, ball2):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    distance = max(math.sqrt(dx ** 2 + dy ** 2), 0.1)  # Prevent distance = 0 since we divide by it later

    # Calculate gravitational force
    force_magnitude = GRAVITY_SCALAR * (ball1.mass * ball2.mass) / (distance ** 2)

    # Apply force components to velocity components
    ball1.dx += force_magnitude * (dx / distance) / ball1.mass
    ball1.dy += force_magnitude * (dy / distance) / ball1.mass
    ball2.dx -= force_magnitude * (dx / distance) / ball2.mass
    ball2.dy -= force_magnitude * (dy / distance) / ball2.mass

running = True
clock = pygame.time.Clock()

dragging = False
start_pos = (0, 0)
end_pos = (0, 0)
preview_ball = None

def rotate_point_180(start_pos, end_pos):
    # Calculate the vector from start_pos to end_pos
    delta_x = end_pos[0] - start_pos[0]
    delta_y = end_pos[1] - start_pos[1]

    # Negate both components to rotate 180 degrees
    flipped_delta_x = -delta_x
    flipped_delta_y = -delta_y

    # Calculate the flipped end_pos by adding the negated vector to the start_pos
    flipped_end_pos = (start_pos[0] + flipped_delta_x, start_pos[1] + flipped_delta_y)

    return flipped_end_pos

# Define variables for timing or frame counting
frame_counter = 0  # Counter for frames
frame_interval = 15  # Interval in frames (e.g., call every 60 frames)

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                dragging = True
                start_pos = event.pos
                end_pos = event.pos
                preview_ball = Ball(start_pos[0], start_pos[1], NEW_BALL_RADIUS, [random.randint(0,255),random.randint(0,255),random.randint(0,255)])
                preview_ball.draw(screen)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and preview_ball is not None:  # Left mouse button
                dragging = False
                end_pos = event.pos
                dx = start_pos[0] - end_pos[0]
                dy = start_pos[1] - end_pos[1]
                # Launch a new ball in the opposite direction of the drag
                preview_ball.dx = dx / 10
                preview_ball.dy = dy / 10
                balls.append(preview_ball)
                preview_ball = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging:  # Update end position while dragging
                end_pos = event.pos
                if preview_ball is not None:
                    dx = start_pos[0] - end_pos[0]
                    dy = start_pos[1] - end_pos[1]
                    preview_ball.dx = dx / 10
                    preview_ball.dy = dy / 10
        elif event.type == pygame.KEYUP:
            root = tk.Tk()
            gui = CheckboxWindow(root, CPU_VELOCITY, CPU_COLOR, MEMORY_GRAVITY, NEW_BALL_RADIUS, False)
            gui.get_bool_vars_on_close()
            root.mainloop()
            CPU_VELOCITY = gui.cpu_velocity
            CPU_COLOR = gui.cpu_color
            MEMORY_GRAVITY = gui.memory_gravity
            if gui.reset_balls:
                balls = []
            NEW_BALL_RADIUS = gui.new_ball_radius

    # Increment frame counter
    frame_counter += 1

    if frame_counter >= frame_interval:
        cpu_percent = psutil.cpu_percent()
        if CPU_VELOCITY:
            VELOCITY_SCALAR = max(1 - cpu_percent / 100, .5)
        else:
            VELOCITY_SCALAR = 1

        if CPU_COLOR:
            COLOR_SCALAR = max(1 - cpu_percent / 100, .5)
        else:
            COLOR_SCALAR = 1

        GRAVITY_SCALAR = psutil.virtual_memory().percent / 100



        # Reset frame counter
        frame_counter = 0

    screen.fill((255, 255, 255))  # White background color

    # Update and draw balls
    for i, ball in enumerate(balls):
        ball.update()
        ball.draw(screen)

        # Check for collision and apply gravity
        for other_ball in balls[i + 1:]:
            handle_collision(ball, other_ball)
            if MEMORY_GRAVITY:
                apply_gravity(ball, other_ball)

    # Draw trajectory line
    if dragging:
        rot_end_pos = rotate_point_180(start_pos, end_pos)
        pygame.draw.line(screen, LINE_COLOR, start_pos, rot_end_pos, 2)

    # Draw preview ball
    if preview_ball:
        preview_ball.draw(screen)

    pygame.display.flip()
    clock.tick(80)  # Set FPS upperbound to 80

pygame.quit()
