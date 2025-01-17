import bpy
import math

bl_info = {
    "name": "Match Frame",
    "author": "tintwotin",
    "version": (0, 1, 1),
    "blender": (2, 90, 0),
    "description": "Jump to a matching frame in a different scene",
    "location": "Sequencer > Strip > Match Frame",
    "tracker_url": "https://github.com/tin2tin/match_frame",
    "category": "Sequencer",
}


class SEQUENCER_OT_match_frame(bpy.types.Operator):
    """Jump to a matching frame in a different scene."""

    bl_idname = "sequencer.match_frame"
    bl_label = "Match Frame"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        current_scene = bpy.context.scene
        current_frame = current_scene.frame_current
        try:
            active = current_scene.sequence_editor.active_strip
        except AttributeError:
            return {"CANCELLED"}
        frame_start = active.frame_start + active.frame_offset_start
        frame_end = (
            active.frame_start + active.frame_offset_start + active.frame_final_duration
        )

        if current_frame >= frame_start and current_frame <= frame_end:
            find_frame = current_frame - active.frame_start
        else:
            find_frame = 0
        for sce in bpy.data.scenes:
            seq = sce.sequence_editor

            if seq and (active.type == "MOVIE" or active.type == "SOUND"):
                for strip in seq.sequences_all:
                    if strip.type == active.type == "MOVIE":
                        strip_file_path = strip.filepath
                        active_file_path = active.filepath
                    elif strip.type == active.type == "SOUND":
                        strip_file_path = strip.sound.filepath
                        active_file_path = active.sound.filepath
                    if (
                        find_frame
                        and current_scene.name != sce.name
                        and active.type == strip.type
                        and active_file_path == strip_file_path
                    ):
                        frame_current = find_frame + strip.frame_start
                        frame_start = strip.frame_start + strip.frame_offset_start
                        frame_end = (
                            strip.frame_start
                            + strip.frame_offset_start
                            + strip.frame_final_duration
                        )
                        print("frame_current " + str(frame_current))
                        print("frame_start " + str(frame_start))
                        print("frame_end " + str(frame_end))
                        if frame_current >= frame_start and frame_current <= frame_end:
                            win = bpy.context.window_manager.windows[0]
                            win.scene = bpy.data.scenes[sce.name]
                            bpy.context.scene.frame_current = frame_current
                            bpy.ops.sequencer.select_all(action="DESELECT")
                            strip.select = True
                            bpy.context.scene.sequence_editor.active_strip = strip
                            bpy.ops.sequencer.view_all()
                            break
                            break
            elif active.type == "SCENE":
                scene_name = active.scene.name
                if scene_name == sce.name:
                    camera_name = ""
                    if active.scene_input == "CAMERA":
                        if active.scene_camera:
                            camera_name = active.scene_camera.name
                    if find_frame and current_scene.name != sce.name:
                        frame_current = find_frame
                        print("frame_current " + str(frame_current))
                        win = bpy.context.window_manager.windows[0]
                        win.scene = bpy.data.scenes[sce.name]
                        bpy.context.scene.frame_current = math.ceil(frame_current)

                        if camera_name:
                            for area in bpy.context.screen.areas:
                                if area.type == "VIEW_3D":
                                    bpy.context.scene.camera = bpy.data.objects[
                                        camera_name
                                    ]  # Select camera as view
                                    area.spaces.active.region_3d.view_perspective = (
                                        "CAMERA"  # Use camera view
                                    )
                                    break
                        break
                        break
        return {"FINISHED"}


def menu_match_frame(self, context):
    self.layout.separator()
    self.layout.operator("sequencer.match_frame")


def register():
    bpy.utils.register_class(SEQUENCER_OT_match_frame)
    bpy.types.SEQUENCER_MT_strip.append(menu_match_frame)


def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_match_frame)
    bpy.types.SEQUENCER_MT_strip.remove(menu_match_frame)


if __name__ == "__main__":
    register()
