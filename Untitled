# PitchWise
## Software Requirements Specification (SRS)

**Project:** PitchWise  
**Document Type:** Software Requirements Specification  
**Version:** 1.0  
**Application Type:** Web-based AI application

---

## 1. Introduction

### 1.1 Purpose

This document defines the functional and non-functional requirements, system architecture, data requirements and technical specifications for PitchWise.

PitchWise aims to simplify pre-match cricket research by combining historical cricket statistics with AI-powered contextual analysis.

### 1.2 Scope

The application will allow users to:
- Select a cricket match.
- Explore historical venue statistics.
- View individual player statistics.
- Compare two players.
- Ask natural-language questions about available statistics.
- Receive AI-generated explanations grounded in the supplied data.

The initial implementation will use a predefined historical dataset rather than real-time cricket data.

### 1.3 Intended Users

- Fantasy cricket players.
- Cricket enthusiasts.
- Beginners interested in understanding cricket statistics.

## 2. System Overview

PitchWise follows a client-server architecture.

**Frontend:** Displays match information, statistics, comparisons and AI insights.

**Backend:** Retrieves and processes cricket statistics, performs calculations and communicates with the AI service.

**Data Layer:** Stores predefined match, venue, player and performance records.

**AI Layer:** Interprets structured statistical information and generates contextual explanations.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js |
| Styling | Tailwind CSS |
| Backend | Python FastAPI |
| Data storage | JSON / SQLite |
| AI integration | Gemini API |
| Data processing | Python |
| Deployment | Vercel + Render |

The initial prototype may use JSON files to avoid unnecessary database complexity. SQLite can be introduced if structured querying becomes necessary.

## 4. Functional Requirements

### FR-01: Match Selection

The system shall:
- Display available demo matches.
- Display participating teams and match format.
- Display the associated venue.
- Allow users to select a match.
- Load the relevant venue and player information.

**Acceptance Criteria:** Selecting a match loads its corresponding venue and available player data.

### FR-02: Ground Intelligence

The system shall:
- Display the selected venue's historical statistics.
- Calculate average first-innings score.
- Calculate average second-innings score.
- Calculate batting-first and chasing win percentages.
- Display pace versus spin wicket distribution.
- Display the total number of matches analysed.

**Acceptance Criteria:** All venue statistics must be calculated from the selected venue's available historical match records.

### FR-03: Player Intelligence

The system shall:
- Display available players.
- Show player role and team.
- Display recent match performances.
- Calculate relevant batting or bowling averages.
- Display venue-specific performance.
- Display opposition-specific performance when sufficient data exists.

**Acceptance Criteria:** Player statistics must correspond to the selected player and selected match context.

### FR-04: Player Comparison

The system shall:
- Allow selection of two players.
- Retrieve their available historical statistics.
- Compare relevant performance metrics.
- Display differences between the players.
- Show the number of innings or matches supporting each statistic.
- Handle missing data without displaying fabricated values.

**Acceptance Criteria:** Users can compare two players and understand the statistical differences using a single interface.

### FR-05: AI-Powered Insights

The system shall:
- Accept natural-language questions.
- Retrieve relevant statistical information.
- Pass structured statistics to the AI service.
- Generate concise contextual explanations.
- Include supporting numerical evidence.
- Identify insufficient data when necessary.

**Acceptance Criteria:** AI-generated insights must be based on supplied statistics and must not introduce unsupported numerical claims.

### FR-06: Error Handling

The system shall:
- Display an error when data cannot be loaded.
- Handle unavailable player statistics.
- Handle invalid player comparisons.
- Handle AI API failures.
- Display a suitable fallback message when AI is unavailable.

## 5. Non-Functional Requirements

### NFR-01: Performance
- Main dashboard should load within approximately three seconds under normal demo conditions.
- Statistical calculations should be performed efficiently.
- AI responses should display a loading state.

### NFR-02: Usability
- Interface should be understandable to beginners.
- Statistics should use simple labels and explanations.
- Comparison information should be easy to scan.
- The main user journey should require minimal navigation.

### NFR-03: Reliability
- Statistics should be derived from structured data.
- Missing values must not be treated as zero.
- AI failure must not prevent access to historical statistics.
- Calculations should be reproducible.

### NFR-04: Security
- API keys must be stored in backend environment variables.
- API credentials must never be exposed in frontend code.
- User inputs should be validated.
- AI requests should have reasonable size limits.

### NFR-05: Maintainability
- Frontend, backend and AI integration should remain modular.
- Statistical calculations should be separated from AI interpretation.
- Data structures should support additional matches and venues.

## 6. System Architecture

The application will use the following flow:

User → React Frontend → FastAPI Backend → Statistical Processing → Structured Data → AI Service → Frontend Response.

### Component Responsibilities

**React Frontend**
- Match selection.
- Venue dashboard.
- Player dashboard.
- Comparison interface.
- AI question interface.

**FastAPI Backend**
- Match and player data retrieval.
- Statistical calculations.
- Player comparison.
- AI prompt construction.
- API response validation.

**Data Layer**
- Match records.
- Venue records.
- Player records.
- Individual player performance records.
- Ball-by-ball events if available.

**AI Service**
- Contextual interpretation.
- Natural-language explanations.
- Evidence-based comparisons.
- Missing-data communication.

## 7. Data Requirements

### 7.1 Match Data

Each match record should contain:

- match_id
- team_1
- team_2
- venue_id
- match_format
- match_date
- innings_results
- toss_winner
- toss_decision
- match_winner

### 7.2 Venue Data

Each venue record should contain:

- venue_id
- venue_name
- location
- total_matches
- average_first_innings_score
- average_second_innings_score
- batting_first_wins
- chasing_wins
- pace_wickets
- spin_wickets

Derived values should be calculated from match records wherever possible.

### 7.3 Player Data

Each player record should contain:

- player_id
- player_name
- team
- playing_role
- batting_style
- bowling_style

### 7.4 Player Performance Data

Each performance record should contain:

- match_id
- player_id
- runs
- balls_faced
- wickets
- runs_conceded
- overs_bowled
- catches
- venue_id
- opponent
- match_date

Missing statistics must be represented as unavailable rather than assumed to be zero.

## 8. API Requirements

The backend should expose the following endpoints.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/matches | Retrieve demo matches |
| GET | /api/matches/{id} | Retrieve match details |
| GET | /api/venues/{id}/stats | Retrieve venue statistics |
| GET | /api/players | Retrieve available players |
| GET | /api/players/{id}/stats | Retrieve player statistics |
| POST | /api/compare | Compare two players |
| POST | /api/ai/insights | Generate AI analysis |

### Example: Player Comparison Request

POST /api/compare

Request body:

{
  "player_a_id": "P001",
  "player_b_id": "P002",
  "match_id": "M001"
}

Expected response:

{
  "player_a": {
    "name": "Player A",
    "venue_average": 48.2,
    "sample_size": 8
  },
  "player_b": {
    "name": "Player B",
    "venue_average": 36.5,
    "sample_size": 12
  }
}

*The values above are illustrative only.*

## 9. AI Integration Requirements

The AI service should receive:
- User's question.
- Selected match details.
- Venue statistics.
- Player statistics.
- Comparison results.
- Data source and sample-size information.

### AI Instructions

The AI must:
1. Use only the supplied statistical information.
2. Never invent player statistics or match records.
3. Explain comparisons in simple language.
4. Mention sample sizes when relevant.
5. Distinguish historical performance from future predictions.
6. Explicitly state when data is insufficient.
7. Avoid guaranteeing fantasy points or match outcomes.
8. Return a concise, structured response.

### Example AI Interaction

**User:** Who has performed better at this venue, Player A or Player B?

**AI:** Player A has a higher venue batting average of 48.2 compared with Player B's 36.5. However, Player A's record comes from eight innings, while Player B has played 12 innings at this venue. Consider recent form and opposition matchups before drawing a conclusion.

## 10. User Interface Requirements

The application should contain the following primary screens:

### Screen 1: Home / Match Selection
- PitchWise branding.
- Short product description.
- Available demo matches.
- Match selection option.

### Screen 2: Match Overview
- Match details.
- Venue details.
- Ground intelligence summary.
- Navigation to player analysis.

### Screen 3: Player Analysis
- Player listing.
- Player statistics.
- Role-based performance information.
- Player selection for comparison.

### Screen 4: Player Comparison
- Side-by-side comparison.
- Statistical differences.
- Sample sizes.
- AI-generated interpretation.

### Screen 5: AI Insights
- Natural-language question input.
- Suggested questions.
- AI-generated response.
- Supporting statistical evidence.

## 11. Testing Requirements

### Functional Testing
- Verify match selection.
- Verify venue statistics calculations.
- Verify player statistics retrieval.
- Verify player comparison.
- Verify AI response generation.

### Data Validation Testing
- Check missing values.
- Check duplicate records.
- Check incorrect match associations.
- Verify sample sizes.
- Verify calculation accuracy against manually calculated results.

### AI Testing
- Ask questions with sufficient data.
- Ask questions with insufficient data.
- Ask questions about unavailable players.
- Check whether the AI invents unsupported statistics.
- Verify that AI explanations match backend calculations.

### Usability Testing
- Verify that a first-time user can select a match.
- Verify that users can compare two players without assistance.
- Check whether insights are understandable without advanced cricket knowledge.

## 12. Deployment Requirements

- Frontend deployed using Vercel.
- Backend deployed using Render or an equivalent service.
- AI API credentials stored securely.
- Sample dataset included with the backend.
- Application accessible through a public URL.
- Demo workflow tested before submission.

## 13. Constraints and Limitations

- Initial implementation uses a limited historical dataset.
- Statistics are not necessarily live.
- Player availability and playing XI confirmation are not guaranteed.
- Historical venue and player performance cannot guarantee future outcomes.
- AI output quality depends on the accuracy and completeness of the input data.
- The prototype does not directly integrate with Dream11.

## 14. Future Enhancements

These features are not required for the initial assignment but may be considered later:

- Live cricket data integration.
- Additional cricket formats.
- More venues and tournaments.
- Advanced batter-versus-bowler analysis.
- Historical pitch-condition trends.
- User-defined player watchlists.
- Additional statistical filters.

## 15. Final Acceptance Criteria

The MVP will be considered complete when:

1. A user can select a demo match.
2. The application displays relevant historical ground statistics.
3. A user can explore individual player performances.
4. A user can compare two players.
5. AI generates a contextual explanation based on actual supplied statistics.
6. The application handles missing data appropriately.
7. The complete workflow is accessible through a deployed public URL.

**Final Technical Objective:**

Build a lightweight, reliable AI-powered cricket analysis prototype that transforms structured historical statistics into understandable insights for fantasy cricket fans.