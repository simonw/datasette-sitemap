from datasette import hookimpl, Response

ROBOTS_TXT = """
Sitemap: https://www.niche-museums.com/sitemap.xml
""".strip()


class SitemapConfig:
    def __init__(self, sql, database, base_url):
        self.sql = sql
        self.database = database
        self.base_url = base_url


def _sitemap_config(datasette):
    plugin_config = datasette.plugin_config("datasette-sitemap") or {}
    if plugin_config.get("sql"):
        return SitemapConfig(
            plugin_config.get("sql"),
            plugin_config.get("database"),
            plugin_config.get("base_url"),
        )
    return None


@hookimpl
def register_routes(datasette):
    if _sitemap_config(datasette):
        return [
            ("^/robots.txt$", robots_txt),
            ("^/sitemap.xml$", sitemap_xml),
        ]


def _make_url_maker(datasette):
    config = _sitemap_config(datasette)
    if config.base_url:
        return lambda _, path: config.base_url + path
    else:
        return lambda request, path: datasette.absolute_url(request, path)


def robots_txt(datasette, request):
    url = _make_url_maker(datasette)
    return Response.text("Sitemap: {}".format(url(request, "/sitemap.xml")))


class SitemapError(Exception):
    pass


async def sitemap_xml(datasette, request):
    config = _sitemap_config(datasette)
    url = _make_url_maker(datasette)
    content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    db = datasette.get_database(config.database)
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
