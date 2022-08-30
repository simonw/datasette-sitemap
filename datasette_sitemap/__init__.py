from datasette import hookimpl, NotFound, Response


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
def register_routes(datasette):
    if _sitemap_config(datasette):
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
    db = datasette.get_database(config.database)
    if config.sql:
        for row in await db.execute(config.sql + " limit 50000"):
            try:
                path = row["path"]
            except IndexError:
                raise SitemapError("SQL query must return a path column")
            if not path.startswith("/"):
                raise SitemapError("Path '{}' must start with /".format(path))
            content.append("<url><loc>{}</loc></url>".format(url(request, row["path"])))
    content.append("</urlset>")
    return Response("\n".join(content), 200, content_type="application/xml")


@hookimpl
def block_robots_extra_lines(datasette, request):
    url = _make_url_maker(datasette)
    return ["Sitemap: {}".format(url(request, "/sitemap.xml"))]
