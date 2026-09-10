# AtmoGraph

## Project Title

# AtmoGraph: Supply Chain Ripple Effect Predictor

---

## Problem Statement

Traditional supply chain prediction systems often rely on linear and isolated data, making it difficult to understand the complex relationships between suppliers, factories, ports, warehouses, and markets.

As a result, these systems may struggle to predict how a disruption in one part of the supply chain can affect connected entities across different regions and industries.

AtmoGraph aims to address this problem by representing the supply chain as an interconnected graph and predicting how disruptions can propagate through the network.

---

## Use Case

A logistics director uses the AtmoGraph dashboard to monitor supply chain risks.

Suppose a sudden port strike occurs in Europe. The system will eventually process related news using Natural Language Processing (NLP), identify affected entities, map the disruption to the supply-chain graph, and use a Graph Neural Network (GNN) to predict potential downstream effects.

For example, the system could predict a potential delay in the delivery of consumer electronics to North American markets, allowing the logistics director to take preventive actions such as rerouting shipments or identifying alternative suppliers.

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
| Sudipta Chakraborty | Frontend | React dashboard, interactive graph, node details, risk visualization and user interface |
| Team Member 2 | Backend & Neo4j | FastAPI, Neo4j database, graph structure and backend APIs |
| Team Member 3 | NLP | News processing, NER, entity extraction and disruption detection |
| Team Member 4 | Machine Learning / GNN | GNN model, delay prediction and ripple-effect analysis |

---

## Tech Stack

### Frontend

- React
- Vite
- React Flow

### Backend

- Python
- FastAPI

### Database

- Neo4j

### Natural Language Processing

- spaCy
- Hugging Face
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

---

## Development Progress

### Frontend Development

The AtmoGraph frontend dashboard has been developed using React, Vite and React Flow.

Current frontend features include:

- Interactive supply chain graph visualization
- Supplier → Factory → Warehouse → Market flow
- Risk-based node visualization
- Search and risk filtering
- Node selection and detailed information panel
- Ripple effect visualization
- Risk Overview dashboard
- Risk Legend
- Prediction Timeline
- AI Supply Chain Insight panel
- Ripple impact and recommendation display
- Enterprise-style dark dashboard interface
- Report export functionality

### Current Status

The frontend dashboard and core user interface are currently functional.

The FastAPI backend and Neo4j database integration are currently under development. The frontend will be connected to the backend API to retrieve supply chain graph data and disruption predictions.

### Upcoming Development

- Connect React frontend with FastAPI backend
- Integrate Neo4j supply chain database
- Retrieve supply chain graph data from Neo4j
- Integrate NLP/NER for disruption information extraction
- Implement disruption detection
- Develop Graph Neural Network (GNN) model
- Predict downstream ripple effects
- Integrate ML predictions with the frontend dashboard
- Complete end-to-end pipeline

---

## Project Architecture

The planned AtmoGraph architecture is:

```text
                    News / Disruption Data
                              │
                              ▼
                         NLP / NER
                              │
                              ▼
                         Neo4j Graph
                              │
                              ▼
                    GNN Ripple Prediction
                              │
                              ▼
                       FastAPI Backend
                              │
                              ▼
                     React Dashboard