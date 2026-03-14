"""
Make sure you use this template for all the modules you create.
This is the standard that must be set so that all modules can run.
"""

# This can be used to find the root project if needed.
from rootmap import ROOT # noqa

# This can also be used if you need color when printing the log.
# If you are confused about what the colors are, you can check the file according to the path.
from app.utility.colors import C # noqa


REQUIRED_OPTIONS = {
    "IP": "",
    "PORT": "",
    "PASS": "",
    "URL": "",
    "EMAIL": "",
    "HASH": "",
    "MESSAGE": "",
    "USER": "",
    "ID": "",
    "COUNT": "",
    "PATH": "",
    "INTERFACE": "",
    "THREAD": "",
    "DOMAIN": "",
    "HOSTNAME": "",
    "MODULE": "",
}

"""
For REQUIRED_OPTIONS select what you need.
Make sure the method name for the main function to be executed matches the template's. 
If it's different, the module won't execute.

"""

# --- Main function ---
def execute(options):

    example = options.get("IP")
    example = options.get("PORT")
    example = options.get("PASS")
    example = options.get("URL")


"""
Maybe you are asking what about modules with different languages
like Rust, Go, C/C++, and all sorts of languages?

Here you need a python based loader to keep following the rules
and run your binary module using python's subprocess.
that's a reasonable solution for now to keep things running smoothly

This is important if the module uses a compiled language
you need to map the binary output path to: 
external/source/binary

You can use the existing rootmap import with examples like: 
os.path.join(ROOT, "external", "source", "binary", "(binary name)")

Why is that? Because the default Storm compiler directs to that path as binary output
Also make sure you use a unique compiled language file name
so as not to collide with other binaries.

because basically the name of the output binary file follows the name of the original file, for example: sakura.rs becomes sakura.

If there is anything else you want to ask and it is not in Storm's explanation
just email me directly at: elzyproot@protonmail.com
I will definitely respond if I have time hehe😄


IMPORTANT!

The current compilers in Storm are only for C, Go, and Rust
you can check in the path scripts/cpl if you want to add for other languages
or you want to add more efficient code it will be very helpful for sure

If you add a module in Rust, make sure you create a Cargo.toml file next to it
in the same folder as the module you created, the compiler will detect it later
Example of the contents of Cargo.toml

[package]
name = "storm"
version = "0.1.0"
edition = "2024"

[[bin]]
name = "sakura" this is the name of the binary output.
path = "sakura.rs" this is your module name

[dependencies]
aes = "0.8"

After that you can check the path lib/smf/core/db/Cargo.toml
and make sure the dependencies you need are there too
because it's where all the Rust dependencies for offline builds are located.
"""
