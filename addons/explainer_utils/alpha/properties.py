from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy.types import Context, Object, UILayout
from explainer_utils import bootstrap_utils


def layout_properties(layout: UILayout, context: Context):
    row = layout.row()
    row.use_property_decorate = True
    row.use_property_split = True
    row.prop(context.object, "alpha_mode", slider=True)

    row = layout.row()
    row.use_property_decorate = True
    row.use_property_split = True
    row.prop(context.object, "alpha", slider=True)

    row = layout.row()
    row.use_property_decorate = True
    row.use_property_split = True
    row.prop(context.object, "composite_alpha", slider=True)

    parent = context.object.parent
    while parent is not None:
        if parent.is_occluder:
            row = layout.row()
            row.alignment = 'RIGHT'
            row.label(text="{:0.0f}% occluded by {}".format(
                (1.0 - parent.composite_alpha) * 100.0,
                parent.name
            ))
        parent = parent.parent

    row = layout.row()
    row.use_property_decorate = True
    row.use_property_split = True
    row.prop(context.object, "is_occluder")


bootstrap_utils.object_panel_layouts.append((500, layout_properties))


def register_properties():
    Object.alpha_mode = EnumProperty(
        name="Alpha Mode",
        description="How a material should react to changes in alpha. Does "
        + "nothing without an appropriate material. Use an attribute node "
        + "with the name set to `composite_alpha_mode` to access this "
        + "property in materials, 0=transparent, 1=black",
        items=[(
            "fade_to_transparent",
            "Fade To Transparent",
            "Become increasingly transparent as alpha approaches zero",
        ), (
            "fade_to_black",
            "Fade To Black",
            "Become increasingly dark as alpha approaches zero",
        ), (
            "same_as_parent",
            "Same As Parent",
            "Use whatever the parent's behavior is (defaults to "
            + "Fade To Transparent if there is no parent)"
        )],
        default='same_as_parent',
        options={'ANIMATABLE', 'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'}
    )
    Object.composite_alpha_mode = IntProperty(
        name="Composite Alpha Mode",
        description="See Alpha Mode",
        min=0,
        max=1,
        options={'HIDDEN', 'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'}
    )
    Object.alpha = FloatProperty(
        name="Alpha",
        description="Transparency of the object.\nUse composite alpha instead "
        + "of this when making materials.\nDoes nothing without an "
        + "appropriate material.",
        default=1.0,
        min=0.0,
        max=1.0,
        soft_min=0.0,
        soft_max=1.0,
        precision=2,
        options={'ANIMATABLE', 'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'}
    )
    Object.composite_alpha = FloatProperty(
        name="Composite Alpha",
        description="This object's alpha, multiplied with the alpha of all "
        + "its parents.\nUse this in shaders by adding an attribute node "
        + "with the name set to `composite_alpha`",
        default=1.0,
        min=0.0,
        max=1.0,
        soft_min=0.0,
        soft_max=1.0,
        precision=2,
        options=set(),
        override=set()
    )
    Object.is_occluder = BoolProperty(
        name="Is Occluder?",
        description="Check if this object works to hide other objects "
        + "as alpha goes to zero (e.g. a black square which becomes "
        + "opaque when composite_alpha=0.0). If this object has children, "
        + "this object is assumed to only occlude its children, and both "
        + "will be hidden when composite_alpha = 0.0",
        default=False,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'}
    )


bootstrap_utils.register_listeners.append(register_properties)


def unregister_properties():
    Object.alpha_mode = None
    Object.alpha = None
    Object.composite_alpha = None
    Object.is_occluder = None


bootstrap_utils.unregister_listeners.append(unregister_properties)
