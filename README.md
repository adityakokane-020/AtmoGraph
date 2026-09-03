# AtmoGraph
Supply Chain Ripple Effect Predictor using NLP, Neo4j and Graph Neural Networks
## Project Development Progress

### Week 1 – Supply Chain Graph & Neo4j

During Week 1, the basic supply-chain graph infrastructure was developed using Neo4j.

#### Completed Tasks

* [x] Neo4j database setup
* [x] Supply-chain node dataset created
* [x] Supply-chain relationship dataset created
* [x] 30 supply-chain nodes created
* [x] 25 supply-chain relationships created
* [x] Supplier, Manufacturer, Port, Warehouse, Distributor and Retailer nodes added
* [x] `SUPPLIES_TO`, `SHIPS_TO` and `DELIVERS_TO` relationships implemented
* [x] Risk, capacity, delay and disruption properties added
* [x] Graph verification completed

#### Week 1 Architecture

```text
Supply Chain Dataset
        ↓
CSV Data
        ↓
Neo4j Graph Database
        ↓
Nodes + Relationships
        ↓
Supply Chain Network
```

---

### Week 2 – NLP-Based Disruption Detection

During Week 2, an NLP pipeline was developed to process disruption-related news and identify affected supply-chain entities.

#### Completed Tasks

* [x] News text input
* [x] Named Entity Recognition using spaCy
* [x] Supply-chain entity extraction
* [x] Entity-to-node mapping
* [x] Direct node matching from news text
* [x] Disruption detection
* [x] Severity detection
* [x] HIGH / MEDIUM / LOW severity classification
* [x] Neo4j risk state update
* [x] NLP pipeline integration

#### Week 2 NLP Pipeline

```text
News Input
    ↓
Entity Extraction
    ↓
Entity Mapping
    ↓
Disruption Detection
    ↓
Severity Detection
    ↓
Neo4j Risk Update
```

#### Example

```text
News:
"Rotterdam Port has been closed due to a severe operational disruption."

        ↓

Entity:
Rotterdam Port

        ↓

Node ID:
P001

        ↓

Severity:
HIGH

        ↓

Neo4j:
P001 Risk = HIGH
```

---

### Week 3 – GNN Ripple Effect Prediction

During Week 3, a Graph Convolutional Network (GCN) was implemented to predict downstream ripple effects caused by supply-chain disruptions.

#### Completed Tasks

* [x] Supply-chain graph converted to PyTorch Geometric format
* [x] Node feature preparation
* [x] Edge index preparation
* [x] Disruption scenarios created
* [x] Scenario-aware GCN implemented
* [x] GCN model trained for 300 epochs
* [x] Ripple delay prediction implemented
* [x] Model evaluation completed
* [x] Trained model saved

#### Dataset

| Parameter       | Value |
| --------------- | ----: |
| Nodes           |    30 |
| Relationships   |    25 |
| Scenarios       |    10 |
| Training Labels |   300 |

#### GCN Architecture

```text
Node Features
     ↓
GCN Layer 1
     ↓
ReLU
     ↓
GCN Layer 2
     ↓
ReLU
     ↓
Linear Layer
     ↓
Predicted Delay
```

#### Training Results

| Metric |   Result |
| ------ | -------: |
| MAE    | **1.20** |
| RMSE   | **3.17** |

Model:

```text
ml/models/ripple_gcn.pth
```

---

## Overall Project Pipeline

```text
              ┌──────────────────┐
              │   News / Event   │
              └────────┬─────────┘
                       ↓
              ┌──────────────────┐
              │   NLP Pipeline   │
              │ Entity Extraction│
              │ Entity Mapping   │
              │ Severity Detection│
              └────────┬─────────┘
                       ↓
              ┌──────────────────┐
              │      Neo4j       │
              │ Supply Chain     │
              │ Graph + Risk     │
              └────────┬─────────┘
                       ↓
              ┌──────────────────┐
              │       GCN        │
              │ Ripple Prediction│
              └────────┬─────────┘
                       ↓
              ┌──────────────────┐
              │ Predicted Delay  │
              │ & Ripple Effect  │
              └────────┬─────────┘
                       ↓
              ┌──────────────────┐
              │    Dashboard     │
              │ React + D3/Flow  │
              └──────────────────┘
```

## Current Project Status

* [x] Week 1 – Neo4j Supply Chain Graph
* [x] Week 2 – NLP Disruption Detection & Risk Update
* [x] Week 3 – GCN Ripple Effect Model
* [ ] GNN Inference Pipeline
* [ ] Neo4j → GNN Integration
* [ ] Frontend Predictive Visualization
* [ ] Real-Time Pipeline
* [ ] Final Testing & Optimization
