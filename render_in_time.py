import bpy
import time

class AX_OT_render_in_time(bpy.types.Operator):
    
    bl_idname = "ax.render_in_time"
    bl_label = "Render in Time"
    bl_description = "Set time in which you want the render to complete"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.scene.render.engine == 'CYCLES'
    
    how_much_i_want: bpy.props.FloatProperty(
        name = "Time",
        description = "How much time you have to render",
        subtype = 'TIME',
        min = 0, default = 20, soft_max = 60
    )
    frames: bpy.props.IntProperty(
        name = "Frames",
        description = "Take multiple tests and average results, improves precision",
        min = 1, default = 2, soft_max = 8
    )
    samples: bpy.props.IntProperty(
        name = "Samples",
        description = "Number of samples to use",
        min = 1, default = 64, soft_max = 1024
    )
    quality: bpy.props.FloatProperty(
        name = "Quality",
        description = "Low - faster estimation; High - better precision",
        subtype = "PERCENTAGE",
        min = 1, default = 40, max = 100
    )
    hq: bpy.props.BoolProperty(
        name = "High Quality",
        description = "Use better algorithm",
        default = False
    )

    def execute(self, context):

        def mean(a):
            return sum(a) / len(a)

        def pre_render():
            bpy.context.scene.render.resolution_percentage = 1
            bpy.context.scene.cycles.samples = 1
            bpy.ops.render.render(write_still = False)
            print("Pre-render done")
        
        def test_render():
            data = []
            for _ in range(self.frames):
                tic = time.perf_counter()
                bpy.ops.render.render(write_still = False)
                render_time = time.perf_counter() - tic
                data.append(render_time)
            return mean(data)
        
        def render(samples):
            bpy.context.scene.render.resolution_percentage = 10
            bpy.context.scene.cycles.samples = samples
            bpy.ops.render.render(write_still = False)
            return 1.0
        
        def quadratic_fit(x1, y1, x2, y2, x3, y3):
            denom = (x1 - x2) * (x1 - x3) * (x2 - x3)
            a = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom
            b = (x3**2 * (y1 - y2) + x2**2 * (y3 - y1) + x1**2 * (y2 - y3)) / denom
            c = (x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3) / denom
            return a, b, c
        
        def quadratic_fit_simplified(x2, y2, x3, y3):
            denom = x2 * x3 * (x2 - x3)
            a = (x3*y2 - x2*y3) / denom
            b = (x2*x2*y3 - x3*x3*y2) / denom
            return a, b
        
        def linear_fit(x, y1, x2, y2):
            return (x - 1) * (y2 - y1) / (x2 - 1) + y1

        def predict_samples(t, y1, x2, y2):
            return 1 + (t - y1) * (x2 - 1) / (y2 - y1)

        start = time.perf_counter()

        # store render values
        resolution_prev = bpy.context.scene.render.resolution_percentage
        samples_prev = bpy.context.scene.cycles.samples
        
        pre_render()

        # bpy.context.scene.render.resolution_percentage = 10
        
        bpy.context.scene.cycles.samples = 1
        low_samples = test_render()

        bpy.context.scene.cycles.samples = self.samples
        high_samples = test_render()

        samples_out = predict_samples(how_much_i_want, low_samples, self.samples, high_samples)

        at_low_res = test_render(1) # todo deal with this
        at_high_res = test_render(1)
        min_samples = test_render(1)
        res = 40

        a, b = quadratic_fit_simplified(res / 2, at_low_res, res, at_high_res) # todo maybe not simplified
        res_final = 100
        at_final_res = a * res_final**2 + b * res_final
        #res_mult = at_final_res / res  # kolikrát se čas prodlouží při 100%

        # base = 2 * b - a  # todo not relevant anymore
        # on_top = 2 * (a - b)

        # elapsed = time.perf_counter() - start
        # needed = how_much_i_want - elapsed

        # samples_out = self.samples * (needed - base) / on_top

        bpy.context.scene.cycles.samples = samples_out
        # render() # todo so it shows the image?

        self.report({'INFO'}, f"Done. Optimal samples - {self.samples}")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "how_much_i_want")