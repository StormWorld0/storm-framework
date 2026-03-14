# Exit command to avoid errors or crashes in storm.
# Because if you only use CTRL + C it is possible that the storm will come out messy.
# This will minimize the possibility of a crash to prevent damage.
def execute(args, context):
    context["exit"] = True
    return context
