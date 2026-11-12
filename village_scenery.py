"""
Computer Graphics Lab Project
Animated Village-Scenery with Day & Night Mode
OpenGL (PyOpenGL + GLUT)

CONTROLS:
  d       -> switch to DAY
  n       -> switch to NIGHT
  SPACE   -> pause / resume animation (windmill, cloud, cart)
  LEFT/RIGHT arrow -> orbit camera
  UP/DOWN arrow    -> raise/lower camera
  ESC     -> quit

Run: python village_scenery.py
Requires: pip install PyOpenGL PyOpenGL_accelerate
"""

import os
os.environ["PYOPENGL_PLATFORM"] = "glx"

import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# ---------------------------------------------------------------
# GLOBAL STATE
# ---------------------------------------------------------------
is_day = True
paused = False

windmill_angle = 0.0
cloud_x = -900.0
cart_x = -700.0
wheel_angle = 0.0

cam_angle = 35.0      # camera orbit angle (degrees)
cam_height = 450.0    # camera height

WIN_W, WIN_H = 1200, 800


# ---------------------------------------------------------------
# DRAW HELPERS
# ---------------------------------------------------------------

def draw_ground():
    glColor3f(0.25, 0.55, 0.2) if is_day else glColor3f(0.08, 0.15, 0.08)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-1500, 0, -1500)
    glVertex3f(-1500, 0, 1500)
    glVertex3f(1500, 0, 1500)
    glVertex3f(1500, 0, -1500)
    glEnd()

    # simple road strip
    glColor3f(0.4, 0.35, 0.3) if is_day else glColor3f(0.12, 0.1, 0.09)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-1500, 0.5, -120)
    glVertex3f(-1500, 0.5, 120)
    glVertex3f(1500, 0.5, 120)
    glVertex3f(1500, 0.5, -120)
    glEnd()


def draw_house(x, z):
    glPushMatrix()
    glTranslatef(x, 0, z)

    # body
    glColor3f(0.85, 0.65, 0.4)
    glPushMatrix()
    glTranslatef(0, 100, 0)
    glScalef(220, 200, 200)
    glutSolidCube(1.0)
    glPopMatrix()

    # roof (cone with 4 slices = pyramid shape)
    glColor3f(0.6, 0.15, 0.1)
    glPushMatrix()
    glTranslatef(0, 200, 0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(170, 130, 4, 4)
    glPopMatrix()

    # window (lights up at night)
    if is_day:
        glColor3f(0.6, 0.8, 0.9)
    else:
        glColor3f(1.0, 0.9, 0.3)
    glPushMatrix()
    glTranslatef(60, 110, 101)
    glScalef(50, 50, 2)
    glutSolidCube(1.0)
    glPopMatrix()

    # door
    glColor3f(0.35, 0.2, 0.1)
    glPushMatrix()
    glTranslatef(-60, 55, 101)
    glScalef(50, 110, 2)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()


def draw_tree(x, z, scale=1.0):
    glPushMatrix()
    glTranslatef(x, 0, z)
    glScalef(scale, scale, scale)

    # trunk
    glColor3f(0.4, 0.25, 0.1)
    glPushMatrix()
    glTranslatef(0, 60, 0)
    glScalef(30, 120, 30)
    glutSolidCube(1.0)
    glPopMatrix()

    # foliage (3 overlapping spheres for a fuller look)
    glColor3f(0.1, 0.5, 0.15)
    for dx, dy, dz, r in [(0, 150, 0, 70), (45, 130, 0, 55), (-45, 130, 0, 55)]:
        glPushMatrix()
        glTranslatef(dx, dy, dz)
        glutSolidSphere(r, 16, 16)
        glPopMatrix()

    glPopMatrix()


def draw_windmill(x, z):
    glPushMatrix()
    glTranslatef(x, 0, z)

    # pole
    glColor3f(0.6, 0.6, 0.6)
    glPushMatrix()
    glTranslatef(0, 140, 0)
    glScalef(16, 280, 16)
    glutSolidCube(1.0)
    glPopMatrix()

    # blades (rotate around the pole top)
    glColor3f(0.9, 0.9, 0.85)
    glPushMatrix()
    glTranslatef(0, 280, 0)
    glRotatef(windmill_angle, 0, 0, 1)   # spin
    for i in range(4):
        glPushMatrix()
        glRotatef(i * 90, 0, 0, 1)
        glTranslatef(0, 70, 0)
        glScalef(14, 130, 6)
        glutSolidCube(1.0)
        glPopMatrix()
    glPopMatrix()

    glPopMatrix()


def draw_wheel():
    glColor3f(0.15, 0.1, 0.08)
    glRotatef(90, 0, 1, 0)
    glutSolidTorus(6, 35, 12, 20)


def draw_cart(x, z):
    glPushMatrix()
    glTranslatef(x, 45, z)

    # cart body
    glColor3f(0.5, 0.3, 0.15)
    glPushMatrix()
    glScalef(140, 60, 80)
    glutSolidCube(1.0)
    glPopMatrix()

    # wheels (spin as the cart moves)
    for wx in (-55, 55):
        glPushMatrix()
        glTranslatef(wx, -35, 45)
        glRotatef(wheel_angle, 1, 0, 0)
        draw_wheel()
        glPopMatrix()
        glPushMatrix()
        glTranslatef(wx, -35, -45)
        glRotatef(wheel_angle, 1, 0, 0)
        draw_wheel()
        glPopMatrix()

    glPopMatrix()


def draw_cloud(x, y, z):
    glColor3f(1.0, 1.0, 1.0) if is_day else glColor3f(0.5, 0.5, 0.55)
    glPushMatrix()
    glTranslatef(x, y, z)
    for dx, dy, dz, r in [(0, 0, 0, 55), (60, 10, 0, 45), (-60, 10, 0, 45), (20, 25, 0, 40)]:
        glPushMatrix()
        glTranslatef(dx, dy, dz)
        glutSolidSphere(r, 14, 14)
        glPopMatrix()
    glPopMatrix()


def draw_pond(x, z):
    # water surface
    glColor4f(0.2, 0.5, 0.8, 0.85) if is_day else glColor4f(0.05, 0.1, 0.25, 0.85)
    glPushMatrix()
    glTranslatef(x, 1.0, z)
    glScalef(1.0, 0.05, 0.7)
    glutSolidSphere(140, 24, 24)
    glPopMatrix()


def draw_sun_moon():
    """Returns the light position used this frame and draws the sun/moon sphere."""
    if is_day:
        pos = (300.0, 500.0, -400.0, 1.0)
        glColor3f(1.0, 0.95, 0.3)
    else:
        pos = (-300.0, 450.0, -400.0, 1.0)
        glColor3f(0.85, 0.85, 0.95)

    glDisable(GL_LIGHTING)  # the sun/moon itself should look "glowing", not shaded
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glutSolidSphere(60, 20, 20)
    glPopMatrix()
    glEnable(GL_LIGHTING)

    return pos


def draw_stars():
    if is_day:
        return
    glDisable(GL_LIGHTING)
    glColor3f(1, 1, 1)
    glPointSize(2.5)
    glBegin(GL_POINTS)
    for i in range(80):
        sx = -1400 + (i * 37) % 2800
        sy = 400 + (i * 53) % 500
        sz = -1400 + (i * 71) % 1000
        glVertex3f(sx, sy, sz)
    glEnd()
    glEnable(GL_LIGHTING)


# ---------------------------------------------------------------
# SCENE / LIGHTING
# ---------------------------------------------------------------

def setup_lighting(light_pos):
    if is_day:
        ambient = (0.35, 0.35, 0.35, 1.0)
        diffuse = (1.0, 1.0, 0.95, 1.0)
        bg = (0.55, 0.75, 0.95, 1.0)
    else:
        ambient = (0.08, 0.08, 0.15, 1.0)
        diffuse = (0.35, 0.35, 0.55, 1.0)
        bg = (0.02, 0.02, 0.08, 1.0)

    glClearColor(*bg)
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.3, 0.3, 0.3, 1.0))


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    rad = math.radians(cam_angle)
    cam_x = 1100 * math.sin(rad)
    cam_z = 1100 * math.cos(rad)
    gluLookAt(cam_x, cam_height, cam_z,   # eye
              0, 150, 0,                  # look-at target
              0, 1, 0)                    # up vector

    light_pos = draw_sun_moon()
    setup_lighting(light_pos)

    draw_ground()
    draw_house(-300, -250)
    draw_tree(250, -300)
    draw_tree(400, -150, 0.8)
    draw_windmill(500, -400)
    draw_pond(-400, 250)
    draw_cloud(cloud_x, 550, -600)
    draw_cart(cart_x, 0)
    draw_stars()

    glutSwapBuffers()


# ---------------------------------------------------------------
# ANIMATION / INPUT
# ---------------------------------------------------------------

def update(value):
    global windmill_angle, cloud_x, cart_x, wheel_angle

    if not paused:
        windmill_angle = (windmill_angle + 4) % 360
        wheel_angle = (wheel_angle + 6) % 360

        cloud_x += 1.2
        if cloud_x > 1400:
            cloud_x = -1400

        cart_x += 1.5
        if cart_x > 1300:
            cart_x = -1300

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # ~60 FPS


def keyboard(key, x, y):
    global is_day, paused
    if key == b'd':
        is_day = True
    elif key == b'n':
        is_day = False
    elif key == b' ':
        paused = not paused
    elif key == b'\x1b':  # ESC
        glutLeaveMainLoop()
    glutPostRedisplay()


def special_keys(key, x, y):
    global cam_angle, cam_height
    if key == GLUT_KEY_LEFT:
        cam_angle -= 4
    elif key == GLUT_KEY_RIGHT:
        cam_angle += 4
    elif key == GLUT_KEY_UP:
        cam_height += 20
    elif key == GLUT_KEY_DOWN:
        cam_height -= 20
    glutPostRedisplay()


# ---------------------------------------------------------------
# INIT
# ---------------------------------------------------------------

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_NORMALIZE)   # keeps lighting correct even after glScalef

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50, WIN_W / WIN_H, 1, 4000)
    glMatrixMode(GL_MODELVIEW)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b"Animated Village Scenery - Day & Night Mode")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutTimerFunc(16, update, 0)
    glutMainLoop()


if __name__ == "__main__":
    main()
