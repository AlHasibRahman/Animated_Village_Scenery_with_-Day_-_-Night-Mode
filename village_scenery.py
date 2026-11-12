

import os
os.environ["PYOPENGL_PLATFORM"] = "glx"

"""
Animated Bangladeshi Village - Python + PyOpenGL + GLUT
Inspired by the user's C++ village reference.

Controls:
  D = Day, N = Night, R = Rain
  B = start/stop boat movement (boat is hidden at night)
  M = mute placeholder (no audio included)
  Arrow keys = move the bird group
  ESC = quit

This is a self-contained 2D OpenGL project. No image assets are required.
"""

import math
import random
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

WIDTH, HEIGHT = 1100, 800
WORLD_W, WORLD_H = 100.0, 80.0

is_night = False
is_raining = False
boat_moving = True
music_on = False  # Audio intentionally omitted; add audio later if desired.

cloud_offsets = [0.0, 0.0, 0.0, 0.0]
rain = [(random.uniform(0, WORLD_W), random.uniform(0, WORLD_H))
        for _ in range(220)]
stars = [(random.uniform(2, 98), random.uniform(52, 78))
         for _ in range(75)]

cloud_speed = [0.035, 0.025, 0.045, 0.03]
bird_x = 0.0
bird_y = 0.0
wing_phase = 0.0
wave_phase = 0.0
leaf_phase = 0.0
cloth_phase = 0.0
boat_x = 0.0
boat_direction = 1


def color(r, g, b):
    glColor3f(r, g, b)


def polygon(points, rgb):
    color(*rgb)
    glBegin(GL_POLYGON)
    for x, y in points:
        glVertex2f(x, y)
    glEnd()


def quad(x1, y1, x2, y2, rgb):
    polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], rgb)


def circle(cx, cy, rx, ry=None, rgb=(1, 1, 1), segments=36):
    if ry is None:
        ry = rx
    color(*rgb)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments + 1):
        a = 2 * math.pi * i / segments
        glVertex2f(cx + math.cos(a) * rx, cy + math.sin(a) * ry)
    glEnd()


def line(x1, y1, x2, y2, rgb=(0, 0, 0), width=1.0):
    color(*rgb)
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()


def text(x, y, message, rgb=(0.05, 0.05, 0.05)):
    color(*rgb)
    glRasterPos2f(x, y)
    for ch in message:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))


def draw_sky():
    if is_night:
        top, bottom = (0.025, 0.035, 0.12), (0.12, 0.16, 0.28)
    elif is_raining:
        top, bottom = (0.28, 0.34, 0.42), (0.52, 0.59, 0.65)
    else:
        top, bottom = (0.22, 0.57, 0.88), (0.70, 0.88, 0.98)

    glBegin(GL_QUADS)
    color(*bottom); glVertex2f(0, 0); glVertex2f(100, 0)
    color(*top); glVertex2f(100, 80); glVertex2f(0, 80)
    glEnd()

    if is_night and not is_raining:
        for x, y in stars:
            circle(x, y, 0.13, 0.13, (1.0, 1.0, 0.85), 8)
        circle(85, 69, 4.0, 4.0, (0.96, 0.96, 0.78))
        circle(86.5, 70.5, 3.5, 3.5, (0.025, 0.035, 0.12))
    elif not is_night and not is_raining:
        circle(48, 70, 4.0, 4.0, (1.0, 0.72, 0.12))


def draw_cloud(x, y, scale=1.0):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(scale, scale, 1)
    c = (0.55, 0.58, 0.62) if is_raining else (0.97, 0.98, 1.0)
    circle(0, 0, 2.6, 2.0, c)
    circle(3, 1.0, 3.2, 2.8, c)
    circle(6.5, 0.5, 3.0, 2.3, c)
    circle(9, -0.1, 2.5, 1.8, c)
    glPopMatrix()


def draw_clouds():
    for i, start in enumerate([-12, 15, 48, 78]):
        x = (start + cloud_offsets[i]) % 125 - 12
        draw_cloud(x, 65 - (i % 2) * 7, 0.65 + (i % 2) * 0.15)


def draw_ground():
    quad(0, 0, 100, 39, (0.24, 0.48, 0.20) if not is_night else (0.10, 0.22, 0.13))
    # Distant green fields
    polygon([(0, 37), (18, 43), (37, 37), (55, 44), (75, 37), (100, 45), (100, 28), (0, 28)],
            (0.32, 0.57, 0.27) if not is_night else (0.12, 0.25, 0.15))
    # Field lines
    for x in range(4, 100, 8):
        line(x, 27, x + 7, 31, (0.30, 0.54, 0.25), 1)


def draw_house(x, y, scale=1.0, wall=(0.78, 0.48, 0.26), roof=(0.42, 0.18, 0.10)):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(scale, scale, 1)

    # Raised platform
    quad(0, 0, 19, 1.2, (0.48, 0.35, 0.22))
    # Walls
    polygon([(1, 1), (17, 1), (17, 12), (9, 16), (1, 12)], wall)
    # Roof
    polygon([(-1, 11.5), (9, 18), (20, 11.5), (18.5, 10), (9, 15.3), (0.5, 10)],
            roof)
    # Door and windows
    quad(8, 1, 11, 8, (0.25, 0.12, 0.06))
    quad(2.5, 7, 6, 10, (0.42, 0.78, 0.88))
    quad(13, 7, 16, 10, (0.42, 0.78, 0.88))
    line(4.25, 7, 4.25, 10, (0.18, 0.18, 0.18), 1)
    line(2.5, 8.5, 6, 8.5, (0.18, 0.18, 0.18), 1)
    line(14.5, 7, 14.5, 10, (0.18, 0.18, 0.18), 1)
    line(13, 8.5, 16, 8.5, (0.18, 0.18, 0.18), 1)
    glPopMatrix()


def draw_coconut_tree(x, y, scale=1.0):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(scale, scale, 1)
    # Slightly curved trunk
    color(0.40, 0.23, 0.10)
    glLineWidth(5)
    glBegin(GL_LINE_STRIP)
    glVertex2f(0, 0); glVertex2f(1.2, 5); glVertex2f(-0.4, 10); glVertex2f(1, 16)
    glEnd()
    # Fronds sway around the crown
    for i in range(7):
        angle = i * (2 * math.pi / 7) + math.sin(leaf_phase + i) * 0.08
        ex = 1 + math.cos(angle) * 9
        ey = 16 + math.sin(angle) * 6
        line(1, 16, ex, ey, (0.02, 0.28, 0.06), 3)
        for t in [0.35, 0.55, 0.75, 0.9]:
            px = 1 + (ex - 1) * t
            py = 16 + (ey - 16) * t
            side = 1.3 * (1 - t)
            line(px, py, px + side, py - 1.2, (0.05, 0.42, 0.08), 1.4)
            line(px, py, px - side, py - 1.2, (0.05, 0.42, 0.08), 1.4)
    for i in range(3):
        circle(1 + math.cos(i * 2.1) * 1.2, 14.8 + math.sin(i * 2.1) * 0.8,
               0.65, 0.7, (0.30, 0.16, 0.05), 16)
    glPopMatrix()



def draw_banyan_tree(x, y, scale=1.0):
    """Draw a large banyan tree on the right side of the village."""
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(scale, scale, 1)

    # Thick, slightly irregular main trunk.
    polygon([(-2.0, 0), (-1.5, 7), (-2.2, 14), (-1.5, 23),
             (1.2, 25), (2.0, 18), (1.5, 10), (2.2, 0)],
            (0.34, 0.18, 0.08) if not is_night else (0.18, 0.12, 0.08))

    # Broad roots spreading along the ground.
    polygon([(-1.8, 2), (-6.5, 0), (-2.2, 0.8)], (0.38, 0.21, 0.09))
    polygon([(1.5, 2), (6.0, 0), (2.0, 0.8)], (0.38, 0.21, 0.09))
    polygon([(-0.8, 1), (-3.8, -0.2), (-1.1, 0.4)], (0.32, 0.17, 0.07))

    # Thick branches spreading underneath the canopy.
    branch_color = (0.29, 0.16, 0.07) if not is_night else (0.16, 0.11, 0.08)
    line(0, 19, -7, 27, branch_color, 5)
    line(0, 21, 7, 29, branch_color, 5)
    line(0, 22, -1, 31, branch_color, 4)
    line(0, 18, 10, 22, branch_color, 4)

    # Hanging aerial roots, characteristic of a banyan tree.
    for rx, top_y, bottom_y in [(-7, 27, 14), (-4, 29, 18),
                                (4, 29, 16), (7, 27, 12), (9, 22, 13)]:
        line(rx, top_y, rx + 0.5, bottom_y, branch_color, 1.8)

    # Dense rounded canopy. Slightly darker at night.
    leaf = (0.035, 0.30, 0.075) if not is_night else (0.025, 0.13, 0.055)
    leaf_light = (0.06, 0.39, 0.10) if not is_night else (0.035, 0.19, 0.075)
    canopy = [(-10, 29, 5.5), (-7, 34, 5.8), (-2, 36, 6.5),
              (4, 35, 6.0), (9, 31, 5.2), (0, 30, 6.0),
              (-5, 27, 5.0), (6, 27, 5.0)]
    for i, (cx, cy, radius) in enumerate(canopy):
        circle(cx, cy, radius, radius * 0.78,
               leaf_light if i % 3 == 0 else leaf, 32)

    # A few visible branch lines in front of the foliage.
    line(-1, 21, -8, 28, branch_color, 2.5)
    line(0, 22, 7, 29, branch_color, 2.5)
    glPopMatrix()


def draw_owl(x, y, scale=1.0):
    """Draw a small owl perched on a branch; shown only in night mode."""
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(scale, scale, 1)

    # Perching branch and feet.
    line(-2.6, -1.5, 2.8, -1.5, (0.24, 0.14, 0.07), 3)
    line(-0.7, -1.1, -0.7, -1.7, (0.72, 0.43, 0.16), 2)
    line(0.8, -1.1, 0.8, -1.7, (0.72, 0.43, 0.16), 2)

    # Body, head and ear tufts.
    circle(0, 0, 1.55, 2.0, (0.38, 0.22, 0.11), 32)
    polygon([(-1.15, 1.0), (-1.35, 2.4), (-0.35, 1.75)], (0.38, 0.22, 0.11))
    polygon([(1.15, 1.0), (1.35, 2.4), (0.35, 1.75)], (0.38, 0.22, 0.11))
    circle(0, 1.15, 1.55, 1.45, (0.48, 0.29, 0.15), 32)

    # Facial discs and bright eyes make the owl visible at night.
    circle(-0.65, 1.25, 0.62, 0.72, (0.88, 0.78, 0.58), 28)
    circle(0.65, 1.25, 0.62, 0.72, (0.88, 0.78, 0.58), 28)
    circle(-0.62, 1.28, 0.25, 0.31, (1.0, 0.82, 0.18), 24)
    circle(0.62, 1.28, 0.25, 0.31, (1.0, 0.82, 0.18), 24)
    circle(-0.62, 1.28, 0.10, 0.18, (0.025, 0.02, 0.015), 20)
    circle(0.62, 1.28, 0.10, 0.18, (0.025, 0.02, 0.015), 20)
    polygon([(-0.23, 0.72), (0.23, 0.72), (0, 0.28)], (0.95, 0.58, 0.08))

    # Small feather marks on the chest.
    for feather_y in [-0.25, -0.65]:
        line(-0.5, feather_y, 0.5, feather_y, (0.72, 0.52, 0.31), 1)
    glPopMatrix()


def draw_fence(x1, x2, y):
    color(0.42, 0.24, 0.10)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex2f(x1, y); glVertex2f(x2, y)
    glVertex2f(x1, y - 2); glVertex2f(x2, y - 2)
    glEnd()
    for x in range(int(x1), int(x2) + 1, 2):
        line(x, y - 3, x, y + 1, (0.48, 0.29, 0.13), 2)


def draw_well(x, y):
    quad(x, y, x + 5, y + 3, (0.68, 0.36, 0.13))
    quad(x - 0.5, y + 3, x + 5.5, y + 4, (0.85, 0.68, 0.25))
    quad(x + 0.3, y + 4, x + 0.8, y + 8, (0.25, 0.18, 0.10))
    quad(x + 4.2, y + 4, x + 4.7, y + 8, (0.25, 0.18, 0.10))
    quad(x - 0.2, y + 8, x + 5.2, y + 8.6, (0.65, 0.18, 0.12))
    line(x + 2.5, y + 8, x + 2.5, y + 3, (0.25, 0.20, 0.16), 1.5)


def draw_river():
    # River occupies the front of the scene
    quad(0, 0, 100, 13, (0.02, 0.30, 0.58) if not is_night else (0.015, 0.10, 0.25))
    color(0.22, 0.68, 0.88)
    glLineWidth(1.5)
    glBegin(GL_LINES)
    for x in range(0, 100, 5):
        y = 7 + math.sin(x * 0.22 + wave_phase) * 1.0
        glVertex2f(x, y)
        glVertex2f(x + 2.5, y + 0.2)
    glEnd()
    # River bank
    polygon([(0, 13), (18, 14), (35, 12.5), (55, 14), (78, 12.8), (100, 14), (100, 11), (0, 11)],
            (0.38, 0.55, 0.23))


def draw_water_lilies():
    for x in [12, 23, 43, 88]:
        y = 3 + (x % 3)
        circle(x, y, 1.7, 0.55, (0.08, 0.40, 0.15))
        circle(x + 0.3, y + 0.8, 0.45, 0.5, (0.75, 0.55, 0.86), 12)


def draw_boat():
    glPushMatrix()
    glTranslatef(boat_x, 0, 0)
    # Hull
    polygon([(62, 6), (87, 6), (83, 2.7), (67, 2.7)], (0.32, 0.16, 0.07))
    line(64, 6, 86, 6, (0.12, 0.08, 0.04), 2)
    # Boatman
    circle(75, 10, 1.0, 1.0, (0.88, 0.65, 0.45))
    circle(75, 10.8, 1.0, 0.55, (0.08, 0.06, 0.04))
    polygon([(73.5, 6.2), (76.5, 6.2), (76.3, 9.3), (73.7, 9.3)], (0.90, 0.70, 0.12))
    # Oar
    line(77, 9, 68, 1.8, (0.32, 0.20, 0.10), 3)
    glPopMatrix()


def draw_bird(x, y, scale=1.0):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(scale, scale, 1)
    a = math.sin(wing_phase) * 0.7
    color(0.04, 0.04, 0.04)
    glLineWidth(2)
    glBegin(GL_LINE_STRIP)
    glVertex2f(-1.3, 0)
    glVertex2f(-0.5, 0.7 + a)
    glVertex2f(0, 0)
    glVertex2f(0.5, 0.7 + a)
    glVertex2f(1.3, 0)
    glEnd()
    glPopMatrix()


def draw_rain():
    color(0.72, 0.84, 1.0)
    glLineWidth(1)
    glBegin(GL_LINES)
    for x, y in rain:
        glVertex2f(x, y)
        glVertex2f(x - 0.5, y - 1.7)
    glEnd()


def draw_clothesline():
    line(76, 24, 91, 24, (0.20, 0.15, 0.10), 1.5)
    line(76, 17, 76, 25, (0.35, 0.20, 0.10), 3)
    line(91, 17, 91, 25, (0.35, 0.20, 0.10), 3)
    if not is_night and not is_raining:
        # Three pieces of cloth gently swing
        for i, (x, c) in enumerate([(78, (0.85, 0.12, 0.12)),
                                    (82, (0.08, 0.30, 0.80)),
                                    (86, (0.05, 0.55, 0.48))]):
            glPushMatrix()
            glTranslatef(x + 1, 23.5, 0)
            glRotatef(math.sin(cloth_phase + i) * 7, 0, 0, 1)
            quad(-1, -5, 1, 0, c)
            glPopMatrix()


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_sky()
    draw_clouds()
    draw_ground()

    # Far objects first, then foreground objects
    draw_coconut_tree(7, 24, 0.85)
    draw_coconut_tree(58, 24, 0.72)
    # Large banyan tree on the right side, behind the village buildings.
    draw_banyan_tree(92, 19, 1.0)
    draw_house(12, 25, 0.85, (0.80, 0.48, 0.25), (0.45, 0.18, 0.10))
    draw_house(36, 29, 1.05, (0.82, 0.40, 0.22), (0.25, 0.42, 0.48))
    draw_house(78, 26, 0.82, (0.74, 0.58, 0.30), (0.48, 0.20, 0.12))
    draw_well(29, 17)
    draw_clothesline()
    draw_fence(0, 27, 22)
    draw_fence(70, 100, 22)

    # River and boat are in the foreground
    draw_river()
    draw_water_lilies()

    # The boat is visible in daytime only. It is completely hidden at night.
    if not is_night:
        draw_boat()

    # An owl sits in the banyan tree only when night mode is active.
    if is_night:
        draw_owl(90, 47, 0.9)

    if not is_night and not is_raining:
        for bx, by in [(30, 53), (34, 55), (38, 52), (42, 56)]:
            draw_bird(bx + bird_x, by + bird_y, 0.65)

    if is_raining:
        draw_rain()

    # Small HUD instructions
    quad(1, 75, 43, 79, (0.93, 0.95, 0.96))
    text(2, 77, "D: Day   N: Night   R: Rain   B: Boat   Arrows: Move birds")
    text(2, 74.8, "Animated Village | Python + OpenGL")
    glutSwapBuffers()


def update(value):
    global wave_phase, leaf_phase, cloth_phase, wing_phase, boat_x

    for i in range(len(cloud_offsets)):
        cloud_offsets[i] += cloud_speed[i]
        if cloud_offsets[i] > 125:
            cloud_offsets[i] = -25

    wave_phase += 0.08
    leaf_phase += 0.035
    cloth_phase += 0.07
    wing_phase += 0.18

    if boat_moving:
        boat_x += 0.08
        if boat_x > 25:
            boat_x = -35

    if is_raining:
        for i, (x, y) in enumerate(rain):
            y -= 0.9
            x -= 0.18
            if y < 0:
                x, y = random.uniform(0, 100), random.uniform(65, 85)
            rain[i] = (x, y)

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


def keyboard(key, x, y):
    global is_night, is_raining, boat_moving, music_on
    key = key.decode("utf-8", errors="ignore").lower()

    if key == '\x1b':
        sys.exit(0)
    elif key == 'd':
        is_night = False
        is_raining = False
    elif key == 'n':
        is_night = True
        is_raining = False
    elif key == 'r':
        is_raining = not is_raining
    elif key == 'b':
        boat_moving = not boat_moving
    elif key == 'm':
        music_on = False
        print("Audio is not included in this starter project.")
    glutPostRedisplay()


def special_keys(key, x, y):
    global bird_x, bird_y
    if key == GLUT_KEY_LEFT:
        bird_x -= 1
    elif key == GLUT_KEY_RIGHT:
        bird_x += 1
    elif key == GLUT_KEY_UP:
        bird_y += 1
    elif key == GLUT_KEY_DOWN:
        bird_y -= 1
    glutPostRedisplay()


def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WORLD_W, 0, WORLD_H)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(80, 50)
    glutCreateWindow(b"Animated Bangladeshi Village - Python OpenGL")

    glClearColor(0.5, 0.7, 0.9, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WORLD_W, 0, WORLD_H)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutTimerFunc(16, update, 0)
    glutMainLoop()


if __name__ == "__main__":
    main()