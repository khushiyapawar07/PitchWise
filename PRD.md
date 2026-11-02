# PitchWise
## Product Requirements Document (PRD)

**Product:** PitchWise  
**Category:** AI-powered Cricket Decision Intelligence  
**Target Platform:** Web Application  
**Target Users:** Fantasy cricket players, particularly Dream11 users  
**Project Type:** Working MVP / Interactive Prototype  
**Version:** 1.0

---

## 1. Product Overview

PitchWise is an AI-powered cricket analysis assistant designed to help fantasy cricket players make more informed player-selection decisions before a match.

It brings together historical ground statistics, player performance, recent form and batter-versus-bowler matchups in one place.

Instead of simply displaying numbers, PitchWise uses AI to interpret relevant statistics and explain what they mean in the context of an upcoming match.

**Product Vision:**

Make cricket statistics understandable, accessible and actionable for every fantasy cricket fan.

## 2. Problem Statement

Fantasy cricket players often research multiple sources before creating their teams.

They need to understand:
- Historical performance of players at a particular venue.
- Ground conditions and historical scoring patterns.
- Player performance against specific opponents.
- Batter-versus-bowler matchups.
- Recent player form and consistency.

However, this information is scattered across different platforms and is often presented as raw statistics.

Users must manually collect, compare and interpret the data before making decisions.

**The actual problem is not the lack of cricket statistics. It is the difficulty of converting scattered historical data into meaningful insights.**

## 3. Target Audience

### Primary Persona: Regular Fantasy Cricket Player

**Profile:**
- Follows cricket regularly.
- Participates in fantasy cricket platforms.
- Researches players before creating teams.
- Uses multiple websites for match statistics.
- Wants to make informed decisions without spending excessive time researching.

**Pain Points:**
- Difficulty finding venue-specific statistics.
- Uncertainty about the relevance of historical records.
- Difficulty comparing two players.
- Lack of contextual explanations.
- Information overload before a match.

### Secondary Persona: Beginner Fantasy Player

- Understands basic cricket.
- Is unfamiliar with advanced statistics.
- Needs simple explanations of player and ground performance.
- Prefers insights over complicated statistical dashboards.

## 4. Product Goals

1. Centralise relevant historical cricket statistics.
2. Help users understand ground and pitch performance patterns.
3. Enable meaningful comparison between players.
4. Use AI to explain statistical trends in simple language.
5. Reduce the time required for pre-match research.

## 5. Proposed Solution

PitchWise provides a single match-analysis experience with four major components.

### A. Ground Intelligence

Provides historical information about the selected venue.

Key information:
- Average first-innings score.
- Average second-innings score.
- Matches won batting first versus chasing.
- Pace and spin wicket distribution.
- Historical high and low scores.
- Number of matches in the dataset.

### B. Player Intelligence

Displays player-specific performance.

Key information:
- Recent match performances.
- Average runs and strike rate for batters.
- Wickets and economy for bowlers.
- Historical venue performance.
- Performance against the selected opposition.

### C. Player Comparison

Allows users to compare two players using relevant historical data.

Comparison parameters:
- Recent form.
- Venue performance.
- Opponent-specific performance.
- Relevant role-based statistics.
- Sample size and consistency.

### D. AI Match Insights

Provides contextual explanations based on available statistics.

Example questions:
- Who has performed better at this venue?
- Does this ground historically favour batting or bowling?
- How does this batter perform against left-arm pace?
- Which player has been more consistent recently?
- What are the important statistical differences between these players?

AI should explain the evidence rather than generate unsupported predictions.

## 6. Core User Journey

1. User opens PitchWise.
2. Selects an upcoming match.
3. Views the selected venue's historical statistics.
4. Explores the available players.
5. Selects two players for comparison.
6. Reviews their statistical performance.
7. Asks AI a question about the comparison.
8. Receives a concise explanation with supporting statistics.

**Primary success moment:** A user understands an important statistical difference between two players without having to manually research multiple sources.

## 7. MVP Scope

The first version will focus on one complete, reliable workflow.

**Must Have:**
- One preconfigured demo match.
- Venue statistics dashboard.
- Player performance dashboard.
- Two-player comparison.
- AI-generated contextual insights.
- Simple, understandable interface.
- Transparent data sources and sample sizes.

**Nice to Have:**
- Batter-versus-bowler analysis.
- Filters for recent matches.
- Additional demo matches.
- Captain and vice-captain statistical comparison.

**Out of Scope:**
- Live ball-by-ball score updates.
- Real-time Dream11 integration.
- Automatic fantasy team generation.
- User accounts and authentication.
- Payment features.
- Guaranteed match or fantasy-point predictions.
- Complex machine-learning prediction models.

## 8. Key Differentiator

Traditional cricket statistics platforms primarily present historical numbers.

PitchWise focuses on explaining those numbers in the context of a user's question.

**Example:**

Traditional statistics:
Player A has a venue average of 48.2 across eight innings.

PitchWise:
Player A has a higher historical average at this venue than Player B. However, eight innings represent a limited sample, so recent form and opposition bowling combinations should also be considered.

The differentiation is contextual interpretation, not simply displaying statistics.

## 9. Success Metrics

For this prototype, success will be measured through usability and output quality rather than commercial growth.

- User can complete the main workflow without assistance.
- User can compare two players in under one minute.
- AI responses reference actual supplied statistics.
- Every statistical comparison displays its sample size.
- No unsupported statistics are presented as facts.
- The application communicates insights clearly and concisely.

## 10. Product Constraints and Assumptions

- Initial version uses a curated historical cricket dataset.
- Historical data will be clearly labelled with its format, date range and source.
- Demo data must not be represented as live or verified statistics.
- AI responses depend on the quality and availability of supplied data.
- Historical performance does not guarantee future performance.
- The product is an independent prototype and is not an official Dream11 product.

## 11. Final Product Definition

PitchWise is an AI-powered cricket decision-support tool that converts historical ground, player and matchup statistics into simple, contextual insights, helping fantasy cricket fans make more informed player-selection decisions.