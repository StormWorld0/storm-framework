# -- https://github.com/StormWorld0/storm-framework
# -- SMF License

from lib.pid_manager import PIDManager as pid

# Exit command to avoid errors or crashes in storm.
# Because if you only use CTRL + C it is possible that the storm will come out messy.
# This will minimize the possibility of a crash to prevent damage.
def execute(args, ctx):
    # Kill all running process PIDs
    pid.cleanup()
    # Mutate state exit in-place
    ctx.exit = True
