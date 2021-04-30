import bpy
import math
import mathutils
import time
import statistics


class my_properties(bpy.types.PropertyGroup):

    engine: bpy.props.EnumProperty(
        name = "Engine",
        description = "Engine to use for rendering",
        items = [
            ('BLENDER_EEVEE', "Eevee", ""),
            ('CYCLES', "Cycles", "")
        ],
        default = 'CYCLES'
    )
    frames: bpy.props.IntProperty(
        name = "Frames",
        description = "Number of frames to render per dataset",
        min = 2, default = 12, soft_max = 256
    )
    resolution: bpy.props.IntProperty(
        name = "Resolution",
        description = "Resolution percentage",
        subtype = "PERCENTAGE",
        min = 1, default = 20, max = 100
    )
    samples: bpy.props.IntProperty(
        name = "Samples",
        description = "Number of samples for each render",
        min = 1, default = 16, soft_max = 1024
    )
    use_base: bpy.props.BoolProperty(
        name = "Baseline Render",
        description = "Whether to render a shaderless image and use it as baseline for ratio",
        default = True
    )
    result: bpy.props.FloatProperty(
        default = 1.0
    )
    confidence: bpy.props.FloatProperty(
        default = 0.5
    )


def lerp(x, in_min, in_max, out_min, out_max):
    return (x - in_min)*(out_max - out_min)/(in_max - in_min) + out_min

def oklab_hsl_2_srgb(h, s, l):

    """ HSL but based on Oklab, so better :) """
    # https://bottosson.github.io/posts/oklab/

    a = s * math.cos(h * math.tau)
    b = s * math.sin(h * math.tau)

    x = l + 0.3963377774 * a + 0.2158037573 * b
    y = l - 0.1055613458 * a - 0.0638541728 * b
    z = l - 0.0894841775 * a - 1.2914855480 * b

    x = x * x * x
    y = y * y * y
    z = z * z * z

    return [
        +4.0767416621 * x - 3.3077115913 * y + 0.2309699292 * z,
        -1.2684380046 * x + 2.6097574011 * y - 0.3413193965 * z,
        -0.0041960863 * x - 0.7034186147 * y + 1.7076147010 * z,
    ]

def falloff(x, g):
    # max(0, x-1) but with smooth transition
    return max(0, x-1) + 0.5*g*math.pow(max(1-abs(x-1), 0), 1/g)


class AX_OT_compare(bpy.types.Operator):
    
    bl_idname = "ax.compare"
    bl_label = "Compare Node Speed"
    bl_description = "Compare speed of multiple nodes, useful for making optimized node groups"
    
    @classmethod
    def poll(cls, context):
        selected = bpy.context.selected_nodes
        in_shader_editor = bpy.context.space_data.tree_type == 'ShaderNodeTree'
        # ^ or context.area.spaces.active.tree_type
        return len(selected) > 1 and in_shader_editor # todo what if i select output

    def execute(self, context):
        
        props = context.scene.ax_compare

        def prepare_nodes():
            if node.outputs[0].type == 'SHADER': # todo fix when i select output (or any other nodes without out?)
                links.new(node.outputs[0], output_node.inputs[0])
                if "ax_viewer" in nodes:
                    nodes.remove(nodes.get("ax_viewer"))  # or? remove on last - todo
            else:
                if "ax_viewer" not in nodes:
                    viewer = nodes.new(type = "ShaderNodeEmission")
                    viewer.location = output_node.location + mathutils.Vector((0, 50))
                    viewer.hide = True
                    viewer.name = "ax_viewer"
                    viewer.label = "ax_viewer"
                
                viewer = nodes.get("ax_viewer")
                
                links.new(node.outputs[0], viewer.inputs[0])
                links.new(viewer.outputs[0], output_node.inputs[0])
        
        def pre_render():
            bpy.context.scene.render.resolution_percentage = 1
            bpy.context.scene.cycles.samples = 1

            bpy.ops.render.render(write_still = False)
            print("Pre-render done")

            bpy.context.scene.render.resolution_percentage = props.resolution
            bpy.context.scene.cycles.samples = props.samples
        
        def get_render():
            start_time = time.perf_counter()
            bpy.ops.render.render(write_still = False)
            return time.perf_counter() - start_time

        def student(mean_a, mean_b, var_a, var_b, n):

            # mean_a = statistics.mean(a)
            # mean_b = statistics.mean(b)
            # var_a = statistics.variance(a, mean_a)
            # var_b = statistics.variance(b, mean_b)

            # dof = 2 * n - 2  # assumes same variance
            dof = (n - 1) * (var_a + var_b)**2 / (var_a**2 + var_b**2)

            threshold = 0.00005

            if mean_a == mean_b:
                return 0.5
            elif var_a != 0 or var_b != 0:
                t = (mean_a - mean_b) / math.sqrt((var_a + var_b)/n)  # todo - stdev or variance, wtf?

            if var_a == 0 and var_b == 0:
                return 1.0
            else:
                # approximation of student's t distribution
                z = t * (1 - 1/(4*dof)) / math.sqrt(1 + (t**2)/(2*dof))
                zzz = 1 - 1 / (1 + math.e**(0.000345*z**5 - 0.069547*z**3 - 1.604326*z))

            return max(0.5, zzz) # todo rename zzz
        
        
        print("Starting - 0%\n")

        # store render values
        engine_prev = bpy.context.scene.render.engine
        resolution_prev = bpy.context.scene.render.resolution_percentage
        samples_prev = bpy.context.scene.cycles.samples  # todo samples prob only work in cycles now

        # set render values
        bpy.context.scene.render.engine = props.engine
        bpy.context.scene.render.resolution_percentage = props.resolution
        bpy.context.scene.cycles.samples = props.samples

        nodes = bpy.context.material.node_tree.nodes
        links = bpy.context.material.node_tree.links
        selected = bpy.context.selected_nodes
        active = bpy.context.active_node
        output_node = nodes.get("Material Output")

        was_linked = output_node.inputs[0].is_linked

        if was_linked:
            link_from_node = output_node.inputs[0].links[0].from_node
            link_from_socket = output_node.inputs[0].links[0].from_socket
        
        # links.remove(link_from_node)  # todo everywhere?
        
        render_times = []
        render_deviations = []

        # main loop, nodes to compare
        for i, node in enumerate(selected):

            prepare_nodes()
            pre_render()
 
            data = []
            # inside loop, renders per node
            for j in range(props.frames):
                
                count = i * props.frames + j + 1
                if props.use_base == True: 
                    progress = count / ((len(selected) + 1) * props.frames)
                else:
                    progress = count / (len(selected) * props.frames)

                render = get_render()
                print(f"{render:.3f}s - {100*progress:.1f}%")
                data.append(render)

            render_time = statistics.mean(data)
            render_times.append(render_time)
            
            if props.frames > 1:
                deviation = statistics.stdev(data)
                render_deviations.append(deviation)
            
            print(f"\nNODE #{i + 1}       Mean: {render_time:.3f}s")
            print(f"Standard Deviation: {deviation:.3f}s\n")
        
        links.remove(output_node.inputs[0].links[0])
        

        # base render
        if props.use_base == True:
            pre_render()
            data_base = []
            for j in range(props.frames):
                render = get_render()
                
                count = len(selected) * props.frames + j + 1
                progress = count / ((len(selected) + 1) * props.frames)
                
                print(f"{render:.3f}s - {100*progress:.1f}%")
                data_base.append(render)
                
            base_time = statistics.mean(data_base)
            print(f"\nBase mean: {base_time:.3f}s\n")


        
        # restore initial link
        if was_linked:
            links.new(link_from_socket, output_node.inputs[0])
        
        min_time = min(render_times)
        max_time = max(render_times)
        
        if props.use_base == True:
            smooth = 0.125
            props.result = falloff(max_time/base_time, smooth) / falloff(min_time/base_time, smooth)
        else:
            props.result = max_time / min_time
            
        

        # stdev needs at least 2
        if props.frames > 1 and min_time != max_time:
            mean = max_time - min_time
            max_dev = render_deviations[render_times.index(max_time)]
            min_dev = render_deviations[render_times.index(min_time)]
            dev = math.sqrt(max_dev**2 + min_dev**2)
            # plus or minus mean, it's (0 - mean) v
            # props.confidence = 0.5 + 0.5 * math.erf(mean / (dev * math.sqrt(2)))
            props.confidence = student(min_time, max_time, min_dev, max_dev, props.frames)
        else:
            props.confidence = 0
        
        if render_times.count(min_time) == 1:
            nodes.active = selected[render_times.index(min_time)]
        else:
            nodes.active = None


        # node color based on results
        for node in selected:
            node.use_custom_color = True
            if min_time == max_time :
                h = 0.8  # purple
            else:
                x = render_times[selected.index(node)]
                h = lerp(x, min_time, max_time, 0.6, 0)
            node.color = [x**0.45 for x in oklab_hsl_2_srgb(h, 0.06, 0.45)]
        if "ax_viewer" in nodes:
            nodes.remove(nodes.get("ax_viewer"))


        # restore render values
        bpy.context.scene.render.engine = engine_prev
        bpy.context.scene.render.resolution_percentage = resolution_prev
        bpy.context.scene.cycles.samples = samples_prev

        self.report({'INFO'}, "Done!")  # todo done how quickly
        
        return {'FINISHED'}