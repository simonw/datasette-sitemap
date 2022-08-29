from datasette.app import Datasette
from xml.etree import ElementTree as ET
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sql,database,expected_paths,expected_error",
    (
        (
            "select 'nopath' as nopath",
            None,
            None,
            "SQL query must return a path column",
        ),
        ("select 'path' as path", None, None, "Path &#39;path&#39; must start with /"),
        ("select '/' as path", None, ["http://localhost/"], None),
        ("select path from urls", "two", ["http://localhost/3"], None),
        (
            "select '/' as path union select '/2' as path",
            None,
            ["http://localhost/", "http://localhost/2"],
            None,
        ),
        # This returns 50001 rows, but we should only get 50000
        (
            """
        with recursive counter(x) as (
        select 0
            union
        select x + 1 from counter
        ),
        paths as (
            select '/' || x as path from counter limit 50001
        ) select path from paths
            """,
            None,
            ["http://localhost/{}".format(i) for i in range(50000)],
            None,
        ),
    ),
)
async def test_datasette_sitemap(sql, database, expected_paths, expected_error):
    datasette = Datasette(
        memory=True,
        metadata={
            "plugins": {
                "datasette-sitemap": {
                    "sql": sql,
                    "database": database,
                }
            }
        },
    )
    if database == "two":
        two = datasette.add_memory_database("two")
        await two.execute_write_script(
            """
            create table if not exists urls (path text);
            insert into urls values ('/3');
        """
        )
    response = await datasette.client.get("/sitemap.xml")
    if expected_error:
        assert response.status_code == 500
        assert expected_error in response.text
    else:
        assert response.status_code == 200
        # It should be XML
        assert response.headers["content-type"] == "application/xml"
        # Parse the XML
        tree = ET.fromstring(response.text)
        # Pull out the <urlset> <url> <loc> elements
        paths = [
            url.text
            for url in tree.findall(
                "{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
            )
        ]
        assert paths == expected_paths
