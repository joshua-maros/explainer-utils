from . import bootstrap_utils

bl_info = {
    "name": "Explainer Utils",
    "category": "All",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
}


def module_and_children(module_name, child_names):
    return [
        module_name,
        *[module_name + "." + child_name for child_name in child_names]
    ]


# A list of all modules excluding the root module and bootstrap_utils.
modules = module_and_children(__name__, [
    "test_module",
    *module_and_children("alpha", [
        "properties"
    ]),
    *module_and_children("ui", [
        "object_properties_panel"
    ]),
])[1:]
print(modules)


def register():
    bootstrap_utils.clear_all_registries()
    for module in modules:
        bootstrap_utils.import_or_reload(module)
    for listener in bootstrap_utils.register_listeners:
        listener()


def unregister():
    for listener in bootstrap_utils.unregister_listeners:
        listener()
