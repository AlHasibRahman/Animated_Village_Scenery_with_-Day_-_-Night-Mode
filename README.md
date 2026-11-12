# Animated Bangladeshi Village (Python + OpenGL)

A starter 2D village animation inspired by the supplied C++/GLUT source. It draws the scene from OpenGL shapes, so **no PNG/JPG/model files are needed**.

## 1. Project files

- `main.py` — complete starter application.
- `requirements.txt` — Python packages.
- `README.md` — setup and component guide.

## 2. Install on Ubuntu

First install the system OpenGL/GLUT libraries:

```bash
sudo apt update
sudo apt install freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev
```

Activate your Python virtual environment, then install:

```bash
python -m pip install -r requirements.txt
```

If PyOpenGL is already installed in your environment, you can skip the pip command.

Run:

```bash
python main.py
```

If you use a virtual environment that cannot see system OpenGL libraries, install the Ubuntu packages above outside the virtual environment; the GLUT shared library is a system dependency.

## 3. Controls

| Key | Action |
|---|---|
| `D` | Day scene |
| `N` | Night scene with moon and stars |
| `R` | Toggle rain |
| `B` | Start/stop boat |
| Arrow keys | Move the bird group |
| `Esc` | Exit |

Audio is intentionally not included. The original C++ uses Windows `PlaySound()` and external WAV files; add Linux-compatible audio only after the graphics are working.

## 4. Where to add or edit components

All drawing functions are in `main.py`. Keep each object in its own function.

| Village component | Function to edit | Where it appears |
|---|---|---|
| Sky, sun, moon, stars | `draw_sky()` | Background, top |
| Clouds | `draw_cloud()` / `draw_clouds()` | Sky |
| Grass and fields | `draw_ground()` | Middle |
| Houses | `draw_house()` | Middle ground |
| Coconut trees | `draw_coconut_tree()` | Behind houses |
| Bamboo fence | `draw_fence()` | Around houses |
| Well | `draw_well()` | Beside houses |
| Clothesline | `draw_clothesline()` | Right side |
| River | `draw_river()` | Front/bottom |
| Water plants | `draw_water_lilies()` | River |
| Boat and boatman | `draw_boat()` | River |
| Birds | `draw_bird()` | Sky |
| Rain | `draw_rain()` | Whole scene |

### Add a new object

1. Create a new function, for example `draw_lamp(x, y)`.
2. Use `quad()`, `circle()`, `line()` or `polygon()` to draw its parts.
3. Call `draw_lamp(20, 20)` inside `display()` at the correct layer.
4. If it must move, create a global position/angle variable and update it inside `update()`.

### Important drawing order

OpenGL draws later objects over earlier objects. In `display()`:

1. Sky and clouds
2. Ground and distant trees
3. Houses and village objects
4. River
5. Boat and water plants
6. Birds/rain and interface text

Move a function call up or down in `display()` to change which object appears in front.

## 5. How the animation works

- `display()` redraws the full village.
- `update()` changes positions and animation angles.
- `glutTimerFunc(16, update, 0)` schedules the next update (about 60 updates per second).
- `glutPostRedisplay()` asks GLUT to draw the next frame.
- `keyboard()` handles D/N/R/B controls.
- `special_keys()` handles arrow keys.
- `reshape()` keeps the 2D coordinate system when the window is resized.

## 6. Coordinate system

The scene uses a virtual coordinate range:

- X: `0` to `100` (left to right)
- Y: `0` to `80` (bottom to top)

For example, `draw_house(36, 29, 1.05)` places a house at X=36, Y=29 and scales it to 1.05 times its base size.

## 7. Suggested development order

1. Run the starter project and understand the coordinate system.
2. Customize house colors, roof styles and positions.
3. Add a village road, bridge, pond, crop field and additional trees.
4. Add people walking using position variables updated in `update()`.
5. Add more detailed boat/oar animation.
6. Add audio after the graphics and controls are stable.
