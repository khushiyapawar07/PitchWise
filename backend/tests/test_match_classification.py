from app.services.match_classification import classify_result, counts_for_win_percentage


def test_no_result_excluded_from_win_percentage() -> None:
    info = {"outcome": {"result": "no result"}}
    rt = classify_result(info)
    assert rt == "no_result"
    assert counts_for_win_percentage(rt) is False


def test_tie_excluded_from_win_percentage() -> None:
    info = {"outcome": {"result": "tie", "eliminator": "Team A"}}
    rt = classify_result(info)
    assert rt == "tie"
    assert counts_for_win_percentage(rt) is False
