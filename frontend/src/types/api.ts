export type Availability = "sufficient" | "limited" | "unavailable";

export interface DemoMatchSummary {
  match_id: string;
  display_title: string;
  team_1: string;
  team_2: string;
  venue_id: string;
  venue_name: string;
  match_date: string;
  match_format: string;
}

export interface MatchDetail extends DemoMatchSummary {
  city: string | null;
  toss_winner: string | null;
  toss_decision: string | null;
  historical_cutoff_date: string;
  excluded_from_history: boolean;
}

export interface MetricWithSample {
  value: number | null;
  sample_size: number;
  availability: Availability;
  label?: string | null;
}

export interface VenueStatsResponse {
  venue_id: string;
  venue_name: string;
  location: string | null;
  context: { as_of_date: string; rules_version: string; data_source: string };
  total_matches_analysed: number;
  average_first_innings_score: MetricWithSample;
  average_second_innings_score: MetricWithSample;
  highest_innings_total: MetricWithSample;
  lowest_innings_total: MetricWithSample;
  batting_first_win_percentage: MetricWithSample;
  chasing_win_percentage: MetricWithSample;
  pace_wickets: MetricWithSample;
  spin_wickets: MetricWithSample;
  unknown_style_wickets: MetricWithSample;
  notes: string[];
}

export interface PlayerListItem {
  player_id: string;
  player_name: string;
  team: string;
  playing_role: string;
  batting_style: string;
  bowling_style: string;
}

export interface PlayerMetricBlock {
  average: number | null;
  strike_rate: number | null;
  economy: number | null;
  wickets: number | null;
  sample_size_innings: number;
  availability: Availability;
}

export interface PlayerStatsResponse {
  player_id: string;
  player_name: string;
  team: string;
  playing_role: string;
  recent_batting: {
    match_date: string;
    opponent: string;
    runs: number | null;
    strike_rate: number | null;
  }[];
  venue_batting: PlayerMetricBlock;
  venue_bowling: PlayerMetricBlock;
  opponent_batting: PlayerMetricBlock;
  opponent_bowling: PlayerMetricBlock;
  context: { as_of_date: string };
  notes: string[];
}

export interface CompareMetricRow {
  metric_key: string;
  label: string;
  player_a: {
    player_name: string;
    value: number | null;
    sample_size: number;
    availability: Availability;
  };
  player_b: {
    player_name: string;
    value: number | null;
    sample_size: number;
    availability: Availability;
  };
  difference: number | null;
}

export interface ComparePlayersResponse {
  match_id: string;
  player_a: { player_name: string; team: string };
  player_b: { player_name: string; team: string };
  metrics: CompareMetricRow[];
  context: { as_of_date: string };
  notes: string[];
}

export interface AIInsightsResponse {
  status: "ok" | "unavailable" | "validation_warning" | "error";
  answer: string;
  evidence: Record<string, unknown>;
  notes: string[];
}
