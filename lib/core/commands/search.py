# MIT License.
# Copyright (c) 2026 Storm Framework

# See LICENSE file in the project root for full license information.


from app.utility.search import search_modules
from app.utility.colors import C

def execute(args, context):
    query = args[0] if args else ""
    if not query:
        print("{C.INPUT}[-] Enter file name to search!")
    else:
        search_modules(query)
    return context
