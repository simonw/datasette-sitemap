from pluggy import HookspecMarker

hookspec = HookspecMarker("datasette")


@hookspec
def sitemap_extra_paths(datasette, request):
    "A list of extra paths to be added to /sitemap.xml"
