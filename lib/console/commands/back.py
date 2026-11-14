# -- https://github.com/StormWorld0/storm-framework
# -- SMF License


# The back command is used to exit a module that has been locked by the use command.
# because moving between modules is very flexible, back will not be used
# unless you want to see global options.
def execute(args, ctx):

    # Checking object attributes, not key dictionary
    if ctx.current_module:
        ctx.current_module = None
        ctx.current_module_name = ""
