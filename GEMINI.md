# Project: Bot-Aware Influence Scoring

## Directory Overview
This workspace contains the planning and documentation for a Social Network Analysis (SNA) project that aims to identify social bots using Graph Attention Networks (GNNs) and calculate "clean" influence scores. By removing detected bots from the network, the project provides a more accurate measure of human-driven influence.

## Key Files
- **`Bot_Aware/Bot_Aware_Influence_Scoring_Roadmap.md`**: The primary project document. It contains a 24-week implementation plan, technical architecture, code snippets, and success metrics.
- **`Bot_Aware/InitialReport.pdf`**: An academic-style report detailing the theoretical framework, literature review, and preliminary findings of the bot-aware influence scoring methodology.

## Project Scope & Context
- **Core Goal**: Develop a pipeline that constructs heterogeneous graphs, detects bots via GAT, and recomputes influence using a composite metric (PageRank, HITS, and Independent Cascade).
- **Primary Dataset**: Cresci-2017.
- **Note on Twibot-22**: As per user directive, Twibot-22 has been removed from the roadmap and is no longer part of the project's scope.

## Usage
Refer to the `Bot_Aware_Influence_Scoring_Roadmap.md` for step-by-step instructions on setting up the environment, training the model, and building the backend/frontend components. This directory currently serves as the "Research and Strategy" phase of the development lifecycle.
