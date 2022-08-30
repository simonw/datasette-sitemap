from datasette import hookimpl, NotFound, Response
from datasette.utils import await_me_maybe
from datasette.plugins import pm
from . import hookspecs

pm.add_hookspecs(hookspecs)


class SitemapConfig:
    def __init__(self, sql, database, base_url):
        self.sql = sql
        self.database = database
        self.base_url = base_url


def _sitemap_config(datasette):
    plugin_config = datasette.plugin_config("datasette-sitemap") or {}
    if plugin_config.get("sql") or plugin_config.get("base_url"):
        return SitemapConfig(
            plugin_config.get("sql"),
            plugin_config.get("database"),
            plugin_config.get("base_url"),
        )
    return None


@hookimpl
def register_routes():
    return [("^/sitemap.xml$", sitemap_xml)]


@hookimpl
def handle_exception(datasette, request, exception):
    if request and request.path == "/robots.txt" and isinstance(exception, NotFound):
        return robots_txt(datasette, request)


def _make_url_maker(datasette):
    config = _sitemap_config(datasette)
    if config and config.base_url:
        return lambda _, path: config.base_url + path
    else:
        return lambda request, path: datasette.absolute_url(request, path)


class SitemapError(Exception):
    pass


def robots_txt(datasette, request):
    url = _make_url_maker(datasette)
    return Response.text("Sitemap: {}".format(url(request, "/sitemap.xml")))


async def sitemap_xml(datasette, request):
    config = _sitemap_config(datasette)
    url = _make_url_maker(datasette)
    content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # First get paths provided by plugins
    paths = []
    for more_paths in pm.hook.sitemap_extra_paths(datasette=datasette, request=request):
        more_paths = await await_me_maybe(more_paths)
        if more_paths:
            paths.extend(more_paths)

    # Add any configured using the SQL query
    if config and config.sql:
        db = datasette.get_database(config.database)
        # Sitemap limit is 50,000
        limit = 50000 - len(paths)
        for row in await db.execute("{} limit {}".format(config.sql, limit)):
            try:
                path = row["path"]
            except IndexError:
                raise SitemapError("SQL query must return a path column")
            paths.append(row["path"])

    # Verify those paths
    for path in paths:
        if not path.startswith("/"):
            raise SitemapError("Path '{}' must start with /".format(path))
        content.append("<url><loc>{}</loc></url>".format(url(request, path)))
    content.append("</urlset>")
    return Response("\n".join(content), 200, content_type="application/xml")


@hookimpl
def block_robots_extra_lines(datasette, request):
    url = _make_url_maker(datasette)
    return ["Sitemap: {}".format(url(request, "/sitemap.xml"))]
