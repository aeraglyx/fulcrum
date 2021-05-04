import bpy
import time

class AX_OT_render_in_time(bpy.types.Operator):
    
    bl_idname = "ax.render_in_time"
    bl_label = "Render in Time"
    bl_description = "Estimate samples so that render takes a certain time"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.scene.render.engine == 'CYCLES'
    
    time_needed: bpy.props.FloatProperty(
        name = "Time",
        description = "How much time you want the render to take (in minutes)",
        subtype = 'TIME',
        min = 0, default = 1, soft_max = 60
    )
    frames: bpy.props.IntProperty(
        name = "Frames",
        description = "Take multiple tests and average results, improves precision",
        min = 1, default = 1, soft_max = 8
    )
    samples: bpy.props.IntProperty(
        name = "Samples",
        description = "Number of samples to use for test renders",
        min = 2, default = 32, soft_max = 1024
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
    unit: bpy.props.EnumProperty(
        name = "Units",
        description = "Unit of time",
        items = [
            ('S', "Seconds", ""),
            ('M', "Minutes", ""),
            ('H', "Hours", "")
        ],
        default = 'M'
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
            # x1 = 1, y1 = time at 1 sample
            return 1 + (t - y1) * (x2 - 1) / (y2 - y1)

        start = time.perf_counter()

        # store render values
        resolution_prev = bpy.context.scene.render.resolution_percentage
        samples_prev = bpy.context.scene.cycles.samples
        
        # pre_render()
        # bpy.context.scene.render.resolution_percentage = resolution_prev

        # TODO test if after changing res, the 1st render is still slower, even after previous test render

        # bpy.context.scene.render.resolution_percentage = 10
        
        # get render time for 1 sample
        bpy.context.scene.cycles.samples = 1
        bpy.ops.render.render(write_still = False)
        at_low_samples = test_render()

        # time unit conversion
        time_needed = self.time_needed * 60 # TODO unit enum

        # catch wrong results
        if at_low_samples > time_needed:
            bpy.context.scene.cycles.samples = 1  # samples_prev or set to 1 for fastest possible?
            self.report({'WARNING'}, f"Can't be done in less than {at_low_samples:.2f}s")
            return {'CANCELLED'}
        if at_low_samples == time_needed:
            bpy.context.scene.cycles.samples = 1  # warning - too low?
            self.report({'INFO'}, f"Done. Optimal samples - 1")
            return {'FINISHED'}

        # get render time for x samples
        bpy.context.scene.cycles.samples = self.samples
        at_high_samples = test_render()

        # catch wrong results
        if at_high_samples <= at_low_samples:
            bpy.context.scene.cycles.samples = samples_prev  # or set to 1 for fastest possible?
            self.report({'ERROR'}, f"Precision error, use higher samples and/or frames.")
            return {'CANCELLED'}
        if at_high_samples == time_needed:
            bpy.context.scene.cycles.samples = self.samples
            self.report({'INFO'}, f"Done. Optimal samples - {self.samples}")
            return {'FINISHED'}

        elapsed = time.perf_counter() - start
        samples_out = round(predict_samples(time_needed, at_low_samples, self.samples, at_high_samples))

        # at_low_res = test_render(1) # TODO deal with this
        # at_high_res = test_render(1)
        # min_samples = test_render(1)
        # res = 40

        # a, b = quadratic_fit_simplified(res / 2, at_low_res, res, at_high_res) # TODO maybe not simplified
        # res_final = 100
        # at_final_res = a * res_final**2 + b * res_final
        #res_mult = at_final_res / res  # kolikrát se čas prodlouží při 100%

        # needed = time_needed - elapsed

        bpy.context.scene.cycles.samples = samples_out
        # TODO so it renders and shows the image?

        self.report({'INFO'}, f"Done. Optimal samples - {samples_out}")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align = True) # TODO options for units
        col.prop(self, "time_needed")
        col.prop(self, "frames")
        col.prop(self, "samples")