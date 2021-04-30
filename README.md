# Fulcrum

Blender addon containing various tools.


## Compare Node Speed

Renders a couple of images in background to retrieve relative speed of selected nodes and therefore their efficiency. Nodes then get colored based on the results:

- **Red** through **Cyan** based on their speed (cyan = fastest)
- **Purple** - all render times match exactly

Aim for 95 % confidence.

Works best with Cycles, in Eevee the renders are a lot more similar and harder to tell which is actually faster.

- Frames - larger values highly recommended
- Resolution, samples
- Baseline render Tries to minimize the effect of how prominent the object is in camera and what else is happening in the scene.

Things to be aware of:
- This operation freezes Blender momentarily, to see progress open Blender's `System Console` beforehand.
- It's dependent on camera position, lighting etc, if your camera can't see the object at all, it's just pure random.
- Do not rely on the `Confidence` read-out too much when using low settings (especially `frames`).


## Reset Node Color
Resets custom color of selected nodes.


## W.I.P.
- Estimate samples for pre-defined render time
- Vertex Groups to Colors

## Future Ideas
- Brush colour presets (RGB, Flowmap, BW, Grey)

---

Live long and prosper 🖖