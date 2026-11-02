from app.utils.cutoff import CutoffContext


def test_cutoff_excludes_demo_match_and_future_dates() -> None:
    ctx = CutoffContext.from_demo_config("2024-04-13", ["1426267"])
    assert not ctx.includes_match("1426267", "2024-04-14")
    assert ctx.includes_match("501221", "2011-04-22")
    assert not ctx.includes_match("1426268", "2024-04-15")
    assert ctx.includes_match("1426266", "2024-04-13")
