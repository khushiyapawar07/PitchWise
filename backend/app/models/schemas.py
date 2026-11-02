from typing import Any, Literal

from pydantic import BaseModel, Field

Availability = Literal["sufficient", "limited", "unavailable"]


class DataContextMeta(BaseModel):
    data_source: str = "Cricsheet IPL JSON"
    as_of_date: str
    rules_version: str
    sample_size: int | None = None


class DemoMatchSummary(BaseModel):
    match_id: str
    display_title: str
    team_1: str
    team_2: str
    venue_id: str
    venue_name: str
    match_date: str
    match_format: str


class MatchDetail(DemoMatchSummary):
    city: str | None = None
    toss_winner: str | None = None
    toss_decision: str | None = None
    historical_cutoff_date: str
    excluded_from_history: bool = True


class MetricWithSample(BaseModel):
    value: float | int | None = None
    sample_size: int = 0
    availability: Availability = "unavailable"
    label: str | None = None


class VenueStatsResponse(BaseModel):
    venue_id: str
    venue_name: str
    location: str | None = None
    context: DataContextMeta
    total_matches_analysed: int
    average_first_innings_score: MetricWithSample
    average_second_innings_score: MetricWithSample
    highest_innings_total: MetricWithSample
    lowest_innings_total: MetricWithSample
    batting_first_wins: MetricWithSample
    chasing_wins: MetricWithSample
    batting_first_win_percentage: MetricWithSample
    chasing_win_percentage: MetricWithSample
    pace_wickets: MetricWithSample
    spin_wickets: MetricWithSample
    unknown_style_wickets: MetricWithSample
    notes: list[str] = Field(default_factory=list)


class PlayerListItem(BaseModel):
    player_id: str
    player_name: str
    team: str
    playing_role: str
    batting_style: str
    bowling_style: str


class PlayerInningsSummary(BaseModel):
    match_id: str
    match_date: str
    opponent: str
    runs: int | None
    balls_faced: int | None
    strike_rate: float | None
    wickets: int | None
    runs_conceded: int | None
    legal_balls_bowled: int | None
    economy: float | None


class PlayerMetricBlock(BaseModel):
    average: float | None = None
    strike_rate: float | None = None
    economy: float | None = None
    wickets: float | None = None
    sample_size_innings: int = 0
    availability: Availability = "unavailable"


class PlayerStatsResponse(BaseModel):
    player_id: str
    player_name: str
    team: str
    playing_role: str
    batting_style: str
    bowling_style: str
    context: DataContextMeta
    recent_batting: list[PlayerInningsSummary] = Field(default_factory=list)
    recent_bowling: list[PlayerInningsSummary] = Field(default_factory=list)
    venue_batting: PlayerMetricBlock
    venue_bowling: PlayerMetricBlock
    opponent_batting: PlayerMetricBlock
    opponent_bowling: PlayerMetricBlock
    notes: list[str] = Field(default_factory=list)


class ComparePlayersRequest(BaseModel):
    player_a_id: str
    player_b_id: str
    match_id: str


class CompareSideMetric(BaseModel):
    player_id: str
    player_name: str
    value: float | None = None
    sample_size: int = 0
    availability: Availability = "unavailable"


class CompareMetricRow(BaseModel):
    metric_key: str
    label: str
    player_a: CompareSideMetric
    player_b: CompareSideMetric
    difference: float | None = None


class ComparePlayerSummary(BaseModel):
    player_id: str
    player_name: str
    team: str
    playing_role: str
    venue_batting_average: float | None = None
    venue_batting_sample_size: int = 0


class ComparePlayersResponse(BaseModel):
    match_id: str
    context: DataContextMeta
    player_a: ComparePlayerSummary
    player_b: ComparePlayerSummary
    metrics: list[CompareMetricRow]
    notes: list[str] = Field(default_factory=list)


class AIInsightsRequest(BaseModel):
    question: str = Field(..., min_length=1)
    match_id: str
    player_a_id: str | None = None
    player_b_id: str | None = None


class AIInsightsResponse(BaseModel):
    status: Literal["ok", "unavailable", "validation_warning", "error"]
    answer: str
    evidence: dict[str, Any]
    notes: list[str] = Field(default_factory=list)
