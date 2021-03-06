from bpy.types import Depsgraph, Object, Scene
from collections.abc import Callable
from explainer_utils import bootstrap_utils


def compute_composite_alpha(obj: Object, alpha_getter: Callable[[Object], float]) -> float:
    composite_alpha = alpha_getter(obj)
    obj = obj.parent
    while obj is not None:
        if not obj.is_occluder:
            composite_alpha *= alpha_getter(obj)
        elif alpha_getter(obj) < 1e-5:
            composite_alpha = 0.0
        obj = obj.parent
    return composite_alpha


def compute_composite_alpha_mode(obj: Object, depsgraph: Depsgraph) -> int:
    if obj is None:
        return 1
    else:
        if depsgraph is not None:
            obj = obj.evaluated_get(depsgraph)
        if obj.alpha_mode == 'fade_to_transparent':
            return 0
        elif obj.alpha_mode == 'fade_to_black':
            return 1
        elif obj.alpha_mode == 'same_as_parent':
            return compute_composite_alpha_mode(obj.parent, depsgraph)


def get_alpha_on_frame(obj: Object, frame: int) -> float:
    if not obj.animation_data or not obj.animation_data.action or not obj.animation_data.action.fcurves:
        return obj.alpha
    for fcurve in obj.animation_data.action.fcurves:
        if fcurve.data_path == 'alpha':
            return fcurve.evaluate(frame)
    return obj.alpha


def compute_composite_alpha_on_frame(obj: Object, frame: int) -> float:
    def alpha_getter(o): return get_alpha_on_frame(o, frame)
    return compute_composite_alpha(obj, alpha_getter)


def get_alpha_via_depsgraph(obj: Object, depsgraph: Depsgraph) -> float:
    if depsgraph is None:
        return obj.alpha
    else:
        return obj.evaluated_get(depsgraph).alpha


def update_composites(scene: Scene, depsgraph: Depsgraph):
    def alpha_getter(o): return get_alpha_via_depsgraph(o, depsgraph)
    for obj in scene.objects:
        try:
            ca = compute_composite_alpha(obj, alpha_getter)
            obj.composite_alpha = ca
            cam = compute_composite_alpha_mode(obj, depsgraph)
            obj.composite_alpha_mode = cam
            if depsgraph is not None:
                evaluated = obj.evaluated_get(depsgraph)
                # for (sks, esks) in zip(obj.data.shape_keys, evaluated.data.shape_keys):
                #     for (sk, esk) in zip(sks.key_blocks, evaluated.key_blocks):
                #         sk.value = esk.value
                for propname in ["location", "rotation_axis_angle", "rotation_euler", "rotation_mode", "rotation_quaternion", "scale"]:
                    setattr(obj, propname, getattr(evaluated, propname))
                for custom_propname in obj.keys():
                    if custom_propname in ["cycles", "alpha", "composite_alpha", "_RNA_UI", "xu_breached", "composite_alpha_mode", "group_with_children", "cycles_visibility", "xu_hidden", "xu_hidden_render"]:
                        continue
                    obj[custom_propname] = evaluated[custom_propname]
            obj.update_tag()
        except:
            # Why does it randomly error for 0.1% of frames? I don't know and I
            # don't want to put effort into actually figuring that out.
            pass


bootstrap_utils.update_listeners.append(update_composites)
