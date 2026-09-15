# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import lib.smf.core.sf.ldch as ldch


def default_options():
    options = {
        "IP": "",
        "PORT": "",
        "PASS": "",
        "URL": "",
        "EMAIL": "",
        "HASH": "",
        "MESSAGE": "",
        "USER": "",
        "USERNAME": "",
        "ID": "",
        "COUNT": "",
        "PATH": "",
        "INTERFACE": "",
        "PROTOCOL": "",
        "THREAD": "",
        "DOMAIN": "",
        "HOSTNAME": "",
        "MODULE": "",
        "HOST": "",
        "API": "",
        "KEY": "",
        "SUBDOM": "",
        "SERVER": "",
        "WORD": "",
        "COMMAND": "",
    }
    return ldch.session(options)
