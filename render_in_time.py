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
        name = "Tests",
        description = "Take multiple tests and average results, improves precision",
        min = 1, default = 1, soft_max = 8
    )
    samples: bpy.props.IntProperty(
        name = "Samples",
        description = "Number of samples to use for test renders",
        min = 2, default = 16, soft_max = 1024
    )
    fast_mode: bpy.props.BoolProperty(
        name = "Fast Mode",
        description = "Use quicker prediction algorithm at the cost of lower precision",
        default = True
    )
    quality: bpy.props.FloatProperty(
        name = "Quality",
        description = "Low - faster estimation; High - better precision",
        subtype = "PERCENTAGE",
        min = 3, soft_min = 10, default = 40, soft_max = 70, max = 100
    )
    unit: bpy.props.EnumProperty(
        name = "Unit",
        description = "Unit of time",
        items = [
            ('S', "Seconds", ""),
            ('M', "Minutes", ""),
            ('H', "Hours", "")
        ],
        default = 'M'
    )
    # what: bpy.props.EnumProperty(
    #     name = "What",
    #     description = "Whether you specify time per frame or for full animation",
    #     items = [
    #         ('FRAME', "Per Frame", ""),
    #         ('ANIMATION', "Animation", "")
    #     ],
    #     default = 'FRAME'
    # )

    # 70 - 99% range is inefficient

    def execute(self, context):

        def mean(a):
            return sum(a) / len(a)

        def pre_render():
            bpy.context.scene.render.resolution_percentage = 1
            bpy.context.scene.cycles.samples = 1
            bpy.ops.render.render(write_still = False)
            print("Pre-render done")
        
        def get_render_time():
            data = []
            for _ in range(self.frames):
                time_start = time.perf_counter()
                bpy.ops.render.render(write_still = False)
                render_time = time.perf_counter() - time_start
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

        res = self.quality
        bpy.context.scene.render.resolution_percentage = res
        
        # get render time for 1 sample
        bpy.context.scene.cycles.samples = 1
        bpy.ops.render.render(write_still = False)  # pre-render
        at_low_samples = get_render_time()

        # time unit conversion - REFACTOR to match-case for Python 3.10
        if self.unit == 'S':
            time_needed = self.time_needed
        elif self.unit == 'M':
            time_needed = self.time_needed * 60
        elif self.unit == 'H':
            time_needed = self.time_needed * 3600

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
        at_high_samples = get_render_time()

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
        
        bpy.context.scene.render.resolution_percentage = resolution_prev
        bpy.context.scene.cycles.samples = samples_out
        # TODO so it renders and shows the image?

        
        
        
        
        # at_low_res = get_render_time(1) # TODO deal with this
        # at_high_res = get_render_time(1)
        # min_samples = get_render_time(1)
        # res = 40

        # a, b = quadratic_fit_simplified(res / 2, at_low_res, res, at_high_res) # TODO maybe not simplified
        # res_final = 100
        # at_final_res = a * res_final**2 + b * res_final
        #res_mult = at_final_res / res  # kolikrát se čas prodlouží při 100%

        # needed = time_needed - elapsed


        self.report({'INFO'}, f"Done. Optimal samples - {samples_out}")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        
        layout = self.layout

        #layout.prop(self, "what", expand = True)
        
        row = layout.row(align = True)
        row.prop(self, "time_needed")
        row_x = row.row(align = True)
        row_x.scale_x = 0.75
        row_x.prop(self, "unit", text = "")
        
        col = layout.column(align = True)
        col.prop(self, "samples")
        col.prop(self, "frames")

        layout.prop(self, "fast_mode")
        if self.fast_mode:
            layout.prop(self, "quality")

        layout.label(text = "WARNING: This could take a couple of minutes.")