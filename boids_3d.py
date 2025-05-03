from vpython import *
import random
import math

# Parameters
SCENE_SIZE = 100
BOID_SIZE = 0.3
MAX_SPEED = 2
NEIGHBOR_RADIUS = 15
AVOID_RADIUS = 5
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 1.0
SEPARATION_WEIGHT = 1.5
SMOOTHING = 0.05  # Lower = smoother
TRAIL_LENGTH = 30

speed_factor = 1.0
is_paused = False

scene = canvas(title="3D Boids Simulation - PRO",
               width=1200, height=700,
               center=vector(0,0,0),
               background=color.black)

scene.camera.pos = vector(0, 0, SCENE_SIZE)
scene.camera.axis = vector(0, 0, -SCENE_SIZE)
scene.userspin = True
scene.userzoom = True
scene.range = SCENE_SIZE / 2
scene.forward = vector(0, 0, -1)

def draw_box(size, color=color.red):
    s = size / 2
    edges = [
        [vector(-s, -s, -s), vector(s, -s, -s)],
        [vector(s, -s, -s), vector(s, s, -s)],
        [vector(s, s, -s), vector(-s, s, -s)],
        [vector(-s, s, -s), vector(-s, -s, -s)],
        [vector(-s, -s, s), vector(s, -s, s)],
        [vector(s, -s, s), vector(s, s, s)],
        [vector(s, s, s), vector(-s, s, s)],
        [vector(-s, s, s), vector(-s, -s, s)],
        [vector(-s, -s, -s), vector(-s, -s, s)],
        [vector(s, -s, -s), vector(s, -s, s)],
        [vector(s, s, -s), vector(s, s, s)],
        [vector(-s, s, -s), vector(-s, s, s)]
    ]
    for start, end in edges:
        curve(pos=[start, end], color=color, radius=0.08)

draw_box(SCENE_SIZE)

def draw_axes(length=SCENE_SIZE/2):
    shaft_w = 0.3
    transparency = 0.15
    arrow(pos=vector(0,0,0), axis=vector(length,0,0), color=vector(1,0,0), opacity=transparency, shaftwidth=shaft_w)
    arrow(pos=vector(0,0,0), axis=vector(0,length,0), color=vector(0,1,0), opacity=transparency, shaftwidth=shaft_w)
    arrow(pos=vector(0,0,0), axis=vector(0,0,length), color=vector(0,0,1), opacity=transparency, shaftwidth=shaft_w)
    label(pos=vector(length+2,0,0), text='X', height=20, color=color.red, box=False, opacity=0, billboard=True)
    label(pos=vector(0,length+2,0), text='Y', height=20, color=color.green, box=False, opacity=0, billboard=True)
    label(pos=vector(0,0,length+2), text='Z', height=20, color=color.blue, box=False, opacity=0, billboard=True)

draw_axes()

class Boid:
    def __init__(self, color_val):
        margin = 5
        half_size = SCENE_SIZE/2 - margin
        self.position = vector(random.uniform(-half_size, half_size),
                               random.uniform(-half_size, half_size),
                               random.uniform(-half_size, half_size))
        initial_speed = random.uniform(0.3, 1.0)
        self.velocity = norm(vector(random.uniform(-1,1),
                                    random.uniform(-1,1),
                                    random.uniform(-1,1))) * initial_speed
        self.body = sphere(pos=self.position, radius=BOID_SIZE, color=color_val)
        self.trail = curve(color=color_val, radius=0.05)

    def update(self, boids):
        alignment = vector(0,0,0)
        cohesion = vector(0,0,0)
        separation = vector(0,0,0)
        count = 0

        for other in boids:
            if other is self:
                continue
            distance = mag(other.position - self.position)
            if distance < NEIGHBOR_RADIUS:
                alignment += other.velocity
                cohesion += other.position
                count += 1
                if distance < AVOID_RADIUS:
                    separation -= (other.position - self.position)

        acceleration = vector(0,0,0)
        if count > 0:
            alignment = norm(alignment / count) * MAX_SPEED - self.velocity
            cohesion = norm((cohesion / count) - self.position) * MAX_SPEED - self.velocity
            separation = norm(separation) * MAX_SPEED - self.velocity

            acceleration += (alignment * ALIGNMENT_WEIGHT +
                             cohesion * COHESION_WEIGHT +
                             separation * SEPARATION_WEIGHT)

        # Smooth update using interpolation
        self.velocity += acceleration * SMOOTHING

        if mag(self.velocity) > MAX_SPEED:
            self.velocity = norm(self.velocity) * MAX_SPEED

        self.position += self.velocity * 0.5 * speed_factor

        half_size = SCENE_SIZE / 2
        for axis in ['x', 'y', 'z']:
            if getattr(self.position, axis) > half_size:
                setattr(self.position, axis, half_size)
                setattr(self.velocity, axis, -getattr(self.velocity, axis))
            elif getattr(self.position, axis) < -half_size:
                setattr(self.position, axis, -half_size)
                setattr(self.velocity, axis, -getattr(self.velocity, axis))

        self.body.pos = self.position
        self.trail.append(pos=self.position)
        if self.trail.npoints > TRAIL_LENGTH:
            self.trail.pop(0)

boids = []

def spawn_group(num, group_color):
    for _ in range(num):
        boids.append(Boid(group_color))

spawn_group(random.randint(30, 50), vector(1, 0, 0))  # Red group
spawn_group(random.randint(30, 50), vector(0, 1, 0))  # Green group
spawn_group(random.randint(30, 50), vector(0, 0, 1))  # Blue group

def pause(): global is_paused; is_paused = True
def play(): global is_paused; is_paused = False
def slow(): global speed_factor; speed_factor = 0.5
def fast(): global speed_factor; speed_factor = 2.0
def spawn_random_group():
    group_color = vector(random.random(), random.random(), random.random())
    spawn_group(random.randint(30, 50), group_color)

button(text='Pause', bind=lambda _: pause(), background=color.red)
button(text='Play', bind=lambda _: play(), background=color.green)
button(text='Slow', bind=lambda _: slow(), background=color.yellow)
button(text='Fast', bind=lambda _: fast(), background=color.cyan)
button(text='Spawn Group', bind=lambda _: spawn_random_group(), background=color.orange)

while True:
    rate(60)
    if not is_paused:
        for boid in boids:
            boid.update(boids)
