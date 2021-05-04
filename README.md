# Fulcrum

Blender addon containing various tools.


## Render in Time

Based on current frame estimates samples so that render takes a certain time. This freezes Blender momentarily.


## Compare Node Speed

Retrieves relative speed of selected nodes by rendering a couple of images in background. Nodes then get colored based on the results:

- **Red** through **Cyan** based on their speed (cyan = fastest)
- **Purple** - no difference

Things to be aware of:
- This operation freezes Blender momentarily, to see progress open Blender's `System Console` beforehand.
- It's dependent on camera position, lighting etc. `Baseline Render` partially solves this (gives a more reasonable relative ratio) but if your camera can't see the object, it's basically random.
- Aim for 95 % `Confidence`, but do not rely on it too much when using low settings.

Recommended settings:
- `Frames` - I wouldn't go under 6, if you have the time, use 30+.
- `Resolution`, `Samples` - Both improve precision, resolution has a bigger impact on performance.
- `Baseline Render` - On.


## Miscellaneous
- Resetting custom color of selected nodes
- Swatches for basic colours in Vertex Paint mode
- Mass conversion of Vertex Groups to Vertex Colors

Live long and prosper 🖖