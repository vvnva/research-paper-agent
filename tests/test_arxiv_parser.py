from app.clients.arxiv import ArxivClient

SAMPLE = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom'>
  <entry>
    <id>http://arxiv.org/abs/1234.5678v1</id>
    <updated>2024-01-02T00:00:00Z</updated>
    <published>2024-01-01T00:00:00Z</published>
    <title> Sample Paper </title>
    <summary> Sample abstract text. </summary>
    <author><name>Author One</name></author>
    <category term='cs.LG' />
  </entry>
</feed>
"""


def test_arxiv_parser_extracts_paper():
    client = ArxivClient(api_base="http://example.com", http_client=None)  # type: ignore[arg-type]
    papers = client._parse_feed(SAMPLE)
    assert len(papers) == 1
    assert papers[0].title == "Sample Paper"
    assert papers[0].authors == ["Author One"]
