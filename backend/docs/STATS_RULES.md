# PitchWise statistical calculation rules (v1)

All metrics are derived from Cricsheet ball-by-ball JSON by the Python backend.  
**Source:** `data/raw/` (read-only). **Rules version:** `1.0.0`.

## Demo temporal boundary

- **Featured match:** `1426267` (MI vs CSK, 2024-04-14, Wankhede).
- **Pre-match historical cutoff:** `2024-04-13` (inclusive).
- Matches with `match_date > cutoff` or `match_id == 1426267` are **excluded** from pre-match historical statistics.

## Deliveries

| Concept | Rule |
|--------|------|
| **Wide** | Delivery has `extras.wides`. |
| **No-ball** | Delivery has `extras.noballs`. |
| **Legal ball** | Not a wide and not a no-ball. |
| **Balls faced (batter)** | Count **legal** deliveries where the player is `batter`. |
| **Batter runs** | Sum of `runs.batter` on deliveries where the player is `batter`. |
| **Bowler runs conceded** | Sum of `runs.total` on deliveries where the player is `bowler` (includes extras). |
| **Bowler legal balls** | Count **legal** deliveries where the player is `bowler`. |
| **Overs bowled** | `bowler_legal_balls / info.balls_per_over` (typically 6). |
| **Wicket (bowler)** | Count `wickets[]` on a delivery where the player is `bowler` and `kind` is **not** `run out` or `retired out`. |
| **Missing participation** | If a player did not bat or bowl, batting/bowling fields are **`null`**, not `0`. |

## Innings totals

- **Innings runs:** Sum of `runs.total` over all deliveries in the innings (includes extras).
- **Innings wickets:** Count wicket events on deliveries in that innings (all dismissal kinds).

## Super overs

- Innings with `"super_over": true` are **excluded** from:
  - Average first-innings / second-innings scores at a venue.
  - High/low venue totals for regulation innings.
- Super-over runs and wickets are still stored on the match record for completeness.
- **Win percentages** use the match `outcome.winner` from the file (includes eliminator/super-over results for tied games).

## DLS / shortened games

- Cricsheet records balls actually bowled; **innings runs** are always computed from delivered balls (no external run targets).
- If an innings is incomplete (e.g. no result), the partial innings total is still summed from data; **venue regulation averages** exclude matches classified as **no result** entirely (see below).
- Revised targets (`target` on chase innings) are informational only; scoring uses ball-by-ball totals.

## Match result classification

| Class | Detection | Venue win-% denominator | Venue regulation innings averages |
|-------|-----------|-------------------------|-----------------------------------|
| **normal** | `outcome.winner` present, no `result: tie`, no `result: no result` | Included | Included (regulation innings only) |
| **tie** | `outcome.result == "tie"` | **Excluded** | Included for non–super-over innings |
| **no_result** | `outcome.result == "no result"` | **Excluded** | **Excluded** (entire match) |

Bat-first vs chase wins (normal matches only): compare toss decision with `outcome.winner`.

## Venue identity

- Raw `info.venue` strings are mapped via `data/metadata/venues.json` aliases to a canonical `venue_id`.

## Player metadata

- Roles and styles come only from `data/metadata/players_ipl.json`.
- Use `"unknown"` when not verified; never infer from names or AI.
