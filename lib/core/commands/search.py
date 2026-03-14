from app.utility.search import search_modules


def execute(args, context):
    query = args[0] if args else ""
    if not query:
        print("{C.INPUT}[-] Enter file name to search!")
    else:
        search_modules(query)
    return context
