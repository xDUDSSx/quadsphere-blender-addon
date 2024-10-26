import bpy
import bmesh
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty
# from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

bl_info = {
    "name": "QuadSphere",
    "description": "Create undistorted quadspheres from the Add Mesh menu.",
    "author": "DUDSS",
    "version": (1, 0, 0),
    "blender": (4, 2, 3),
    "location": "3D View > Add > Mesh > Quadsphere",
    "warning": "",
    "doc_url": "https://github.com/xDUDSSx/quadsphere-blender-addon",
    "tracker_url": "https://github.com/xDUDSSx/quadsphere-blender-addon",
    "category": "Add Mesh"
}


################################################################################
# UI
################################################################################

def addQuadsphereButton(self, context):
    self.layout.operator(
        AddQuadsphere.bl_idname,
        text="Quadsphere",
        icon='SPHERE')


################################################################################
# OPERATORS
################################################################################

qs_correction_factors = [None, None, [0.97325, 0.995401], [0.9946, 0.9983]]

class AddQuadsphere(bpy.types.Operator):
    bl_idname = "quadsphere.quadsphere_add"
    bl_label = "Quadsphere"
    bl_description = "Construct a spherical mesh consisting of similarly sized quads only."
    bl_options = {'REGISTER', 'UNDO'}

    subdivisions: IntProperty(
        name="Subdivisions",
        description="",
        min=1, max=3,
        default=3,
    )

    size: FloatProperty(
        name="Size",
        subtype='DISTANCE',
        default=2,
        min=0.001
    )

    shadeSmooth: BoolProperty(
        name="Shade Smooth",
        description="Applies smooth shading to created mesh.",
        default=True,
    )
    correct: BoolProperty(
        name="Correct Shading",
        description="""Scales certain points of the subdivided cube to avoid distortion around the original cube corners.
Works only for 2 and 3 subdivisions. For higher subdivisions simply apply a subdivide modifier on the 3 subdivisions quadsphere""",
        default=True,
    )

    def execute(self, context):
        cursor_pos = bpy.context.scene.cursor.location
        started_in_edit_mode = bpy.context.mode is "EDIT_MESH"

        if self.subdivisions < 1:
            print("Cannot create quadsphere with no subdivisions!")
            return {'CANCELLED'}

        # We need to create the cube as a separate object in object mode (as we use modifiers later)
        if (bpy.context.active_object is not None):
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=cursor_pos, size=self.size, scale=(1, 1, 1))
        bpy.context.object.name = "Quadsphere"

        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subdivision"].levels = self.subdivisions
        bpy.ops.object.modifier_apply(modifier="Subdivision")

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.tosphere(value=1, mirror=True, use_proportional_edit=False, snap=False)

        if (self.correct and self.subdivisions < len(qs_correction_factors)):
            factors = qs_correction_factors[self.subdivisions]
            if (factors is not None):
                cube = bpy.context.active_object
                bm = bmesh.from_edit_mesh(cube.data)
                bpy.ops.mesh.select_all(action='DESELECT')
                verts3 = [v for v in bm.verts if len(v.link_edges) == 3]
                for vert in verts3:
                    vert.select = True

                originalPivotPoint = bpy.context.scene.tool_settings.transform_pivot_point
                bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

                bpy.ops.transform.resize(value=(factors[0], factors[0], factors[0]), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                         mirror=True, use_proportional_edit=False,
                                         proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False,
                                         snap_elements={'INCREMENT'},
                                         use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

                bpy.ops.mesh.select_more()

                bpy.ops.transform.resize(value=(factors[1], factors[1], factors[1]), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                         mirror=True, use_proportional_edit=False,
                                         proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False,
                                         snap_elements={'INCREMENT'},
                                         use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                bpy.ops.mesh.select_all(action='SELECT')

        if (self.shadeSmooth):
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.shade_smooth()

        bpy.ops.object.mode_set(mode=('EDIT' if started_in_edit_mode else 'OBJECT'))  # Restore initial mode

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.scene.library is None


################################################################################
# ADDON
################################################################################

classes = [AddQuadsphere]

def register():
    print("QuadSphere: Registering addon")
    print("")
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.VIEW3D_MT_mesh_add.append(addQuadsphereButton)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
