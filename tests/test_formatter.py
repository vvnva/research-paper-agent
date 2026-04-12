from app.modules.formatter import ResponseFormatter
from app.schemas.domain import Paper, PipelineResult


def test_formatter_renders_papers():
    result = PipelineResult(
        session_id="tg_1",
        normalized_query="graph neural networks",
        message="test",
        papers=[
            Paper(
                paper_id="arxiv:1",
                title="Paper A",
                abstract="Abstract",
                authors=["A", "B"],
                published_at="2024-01-01",
                categories=["cs.LG"],
                url="https://arxiv.org/abs/1",
                summary="short",
            )
        ],
    )
    text = ResponseFormatter().format(result)
    assert "Paper A" in text
    assert "Summary: short" in text
