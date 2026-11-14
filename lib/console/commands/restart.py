# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
from apps.utility.restart import run_restart as restart


# This is to restart and save the variables that were set before restarting and then restore them.
# This is good if we experience a bug or error failure when we are ready to execute.
# by storing old variable data, it is very profitable and speeds up the time
def execute(args, ctx):
    try:
        restart(ctx.options)
    except Exception:
        pass
