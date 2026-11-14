# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import apps.base.config_ui as ui


# The about command is used to display developer information, etc.
# to find out who the creator, contributor, version, etc.
# This is useful for very specific information.
def execute(args, ctx):
    ui.show_about()
