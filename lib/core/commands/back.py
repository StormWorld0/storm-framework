def execute(args, context):
    if context["current_module"]:
        context["current_module"] = None
        context["current_module_name"] = ""
    return context
