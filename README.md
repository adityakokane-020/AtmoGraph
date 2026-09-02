# AtmoGraph

## Project Title

# AtmoGraph: Supply Chain Ripple Effect Predictor

---

## Problem Statement

Traditional supply chain predictive models rely on linear and isolated time-series data.

They fail to understand complex global networks and cannot predict how a localized crisis in one industry or location will affect connected industries across the globe.

AtmoGraph aims to solve this problem by representing the supply chain as an interconnected graph and predicting how disruptions can propagate through the network.

---

## Use Case

A logistics director monitors the AtmoGraph dashboard.

A sudden port strike occurs in Europe.

The system will eventually process the news using NLP, identify the affected entities, map the disruption to the supply-chain graph, and use a Graph Neural Network to predict the downstream ripple effect.

For example, the system could predict a 3-month delay in North American consumer electronics, allowing the logistics director to proactively reroute shipments.

---

## Team Members

- Team Member 1 – Frontend Development
- Team Member 2 – Backend & Neo4j
- Team Member 3 – NLP / Data Processing
- Team Member 4 – Machine Learning / GNN

---

## Team Responsibilities

| Team Member | Module | Main Responsibilities |
|---|---|---|
| Sudipta Chakraborty | Frontend | React dashboard, interactive graph, node details and risk visualization |
| Team Member 2 | Backend & Neo4j | FastAPI, Neo4j database, graph structure and APIs |
| Team Member 3 | NLP | News processing, NER, entity extraction and disruption detection |
| Team Member 4 | Machine Learning / GNN | GNN model, delay prediction and ripple-effect analysis |

---

## Tech Stack

### Frontend

- React
- Vite
- React Flow
- D3.js

### Backend

- Python
- FastAPI

### Database

- Neo4j

### Natural Language Processing

- spaCy
- HuggingFace
- Named Entity Recognition (NER)

### Machine Learning

- PyTorch
- PyTorch Geometric

### Development Tools

- Git
- GitHub
- VS Code

---

## Folder Structure

```text
AtmoGraph/
│
├── frontend/
├── backend/
├── ml/
├── docs/
├── assets/
│
├── .gitignore
└── README.md