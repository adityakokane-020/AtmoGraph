# AtmoGraph

**Supply Chain Ripple Effect Predictor using NLP, Neo4j and Graph Neural Networks**

AtmoGraph is an AI-based supply-chain disruption prediction system that combines **Natural Language Processing (NLP)**, **Neo4j Graph Database**, and **Graph Convolutional Networks (GCN)** to identify supply-chain disruptions and predict their downstream ripple effects.

---

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
* [x] Disruption type detection
* [x] Port Closure detection
* [x] Port Strike detection
* [x] Port Congestion detection
* [x] Neo4j risk state update
* [x] Disruption type stored in Neo4j
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
Disruption Type Detection
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

Disruption Type:
Port Closure

        ↓

Neo4j:
P001 Risk = HIGH
P001 Disruption = 1
P001 Disruption Type = Port Closure
```

---

### Week 3 – GNN Ripple Effect Prediction

During Week 3, the initial Graph Convolutional Network was developed for supply-chain ripple effect prediction.

#### Completed Tasks

* [x] Supply-chain graph converted to PyTorch Geometric format
* [x] Node feature preparation
* [x] Edge index preparation
* [x] Disruption scenarios created
* [x] Scenario-aware GCN implemented
* [x] Ripple delay prediction implemented
* [x] Model evaluation completed
* [x] Trained model saved

---

### Week 4 – GCN V2 & Full ML Integration

During Week 4, the GCN V2 model and complete NLP-to-GNN pipeline were integrated.

#### Completed Tasks

* [x] GCN V2 training pipeline implemented
* [x] Scenario-based training data generated
* [x] 30 disruption scenarios created
* [x] 900 node-level ripple labels generated
* [x] Severity-aware features implemented
* [x] Disruption-type features implemented
* [x] 9-dimensional GCN input features implemented
* [x] GCN V2 model trained
* [x] GCN V2 evaluation completed
* [x] GCN V2 inference pipeline implemented
* [x] Neo4j → GCN integration completed
* [x] NLP → GCN integration completed
* [x] Predicted delays written back to Neo4j
* [x] Predicted risk levels written back to Neo4j
* [x] End-to-end pipeline tested

---

## GCN V2 Dataset

| Parameter            |             Value |
| -------------------- | ----------------: |
| Supply-chain nodes   |                30 |
| Relationships        |                25 |
| Disruption scenarios |                30 |
| Node-level labels    |               900 |
| GCN input features   |                 9 |
| Graph framework      | PyTorch Geometric |

### GCN V2 Input Features

The GCN V2 model uses the following 9 features:

```text
Base Features
├── Capacity
├── Delay
├── Risk Value
└── Disruption Value

Scenario Features
├── Source Node Indicator
├── Severity
├── Port Strike
├── Port Closure
└── Port Congestion
```

---

## GCN V2 Architecture

```text
9 Input Features
       ↓
GCN Layer 1
       ↓
ReLU
       ↓
GCN Layer 2
       ↓
ReLU
       ↓
GCN Layer 3
       ↓
ReLU
       ↓
Linear Layer
       ↓
Predicted Delay
       ↓
Risk Classification
```

---

## GCN V2 Training Results

The GCN V2 model was evaluated on the generated test scenarios.

| Metric |         Result |
| ------ | -------------: |
| MAE    | **0.408 days** |
| RMSE   | **1.518 days** |
| R²     |      **0.930** |

The GCN V2 model improved the prediction performance compared with the earlier baseline model.

> Note: The current model uses scenario-based/synthetic training data. Therefore, these evaluation results demonstrate model performance on the prepared scenarios and should not be interpreted as real-world production accuracy.

### Model

```text
ml/models/ripple_gcn_v2.pth
```

---

## Disruption Types

The current GCN V2 pipeline supports three port disruption types:

```text
Port Closure
Port Strike
Port Congestion
```

### Severity Levels

```text
HIGH
MEDIUM
LOW
```

The disruption type and severity are passed from the NLP pipeline to the GCN V2 model.

---

## Overall Project Pipeline

```text
                 ┌─────────────────────┐
                 │      News / Event    │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │    NLP Pipeline     │
                 │                     │
                 │ Entity Extraction   │
                 │ Entity Mapping      │
                 │ Severity Detection  │
                 │ Disruption Type     │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │       Neo4j         │
                 │                     │
                 │ Supply Chain Graph  │
                 │ Risk Update         │
                 │ Disruption State    │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │      GCN V2         │
                 │                     │
                 │ Graph Processing    │
                 │ Ripple Prediction   │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Predicted Delay     │
                 │ Predicted Risk      │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │       Neo4j         │
                 │ Prediction Storage  │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Dashboard / Frontend│
                 │    React + D3/Flow  │
                 └─────────────────────┘
```

---

## End-to-End Pipeline Execution

The complete pipeline can be executed using:

```cmd
python ml\run_pipeline.py
```

Example input:

```text
Rotterdam Port has been closed due to a severe operational disruption.
```

The pipeline performs:

```text
1. Reset Previous Disruptions
2. News Input
3. Entity Mapping
4. Severity Detection
5. Disruption Type Detection
6. Neo4j Risk Update
7. GCN V2 Ripple Prediction
8. Predicted Delay Calculation
9. Predicted Risk Classification
10. Neo4j Prediction Update
```

Example output:

```text
Entity:
Rotterdam Port → P001

Severity:
HIGH

Disruption Type:
Port Closure

GCN V2:

P001 → 45.78 days → Critical
W001 → 37.16 days → Critical
D002 → 23.67 days → Critical
R002 → 17.27 days → Critical
```

This demonstrates the propagation of disruption effects through the supply-chain graph.

---

## Neo4j Prediction Properties

After GCN inference, prediction results are stored in Neo4j.

Relevant properties include:

```text
risk
disruption
disruption_type
predicted_delay
predicted_risk
```

Example:

```text
P001
├── Risk: HIGH
├── Disruption: 1
├── Disruption Type: Port Closure
├── Predicted Delay: 45.78 days
└── Predicted Risk: Critical
```

---

## Project Structure

```text
AtmoGraph/
│
├── ml/
│   ├── data/
│   │   ├── node_features.csv
│   │   ├── edge_index.csv
│   │   ├── disruption_scenarios_v2.csv
│   │   ├── mapped_scenarios_v2.csv
│   │   └── ripple_labels_v2.csv
│   │
│   ├── gnn/
│   │   ├── train_gcn_v2.py
│   │   ├── neo4j_gcn_integration.py
│   │   └── neo4j_gcn_v2_integration.py
│   │
│   ├── nlp/
│   │   ├── integration.py
│   │   ├── severity_detection.py
│   │   ├── disruption_type_detection.py
│   │   └── neo4j_risk_update.py
│   │
│   ├── preprocessing/
│   │   ├── generate_scenarios_v2.py
│   │   ├── map_scenarios_v2.py
│   │   └── generate_ripple_labels_v2.py
│   │
│   ├── models/
│   │   └── ripple_gcn_v2.pth
│   │
│   └── run_pipeline.py
│
├── graph/
│   └── neo4j_ingestion.py
│
├── entity_mapper.py
│
└── README.md
```

---

## Technologies Used

| Technology         | Purpose                     |
| ------------------ | --------------------------- |
| Python             | Core development            |
| spaCy              | NLP and entity extraction   |
| Neo4j              | Supply-chain graph database |
| PyTorch            | Deep learning               |
| PyTorch Geometric  | Graph Neural Networks       |
| Pandas             | Data processing             |
| NumPy              | Numerical processing        |
| scikit-learn       | Model evaluation            |
| React              | Frontend dashboard          |
| D3.js / React Flow | Graph visualization         |

---

## Current Project Status

### Core ML + Neo4j

* [x] Neo4j Supply Chain Graph
* [x] Entity Mapping
* [x] Severity Detection
* [x] Disruption Type Detection
* [x] Neo4j Risk Update
* [x] GCN V2 Training
* [x] GCN V2 Evaluation
* [x] GCN Inference Pipeline
* [x] Neo4j → GCN Integration
* [x] NLP → GCN Integration
* [x] Predicted Delay → Neo4j
* [x] Predicted Risk → Neo4j
* [x] End-to-End ML Pipeline

### Remaining Work

* [ ] Port Strike end-to-end testing
* [ ] Port Congestion end-to-end testing
* [ ] Full frontend + backend + ML integration
* [ ] Complete system testing
* [ ] Performance optimization
* [ ] Final documentation
* [ ] Final dashboard validation
* [ ] Final presentation and review preparation

---

## Current Completion

```text
Core Neo4j + ML Pipeline       ████████████████████ 100%
NLP Pipeline                   ████████████████████ 100%
GCN V2                         ████████████████████ 100%
Neo4j + GCN Integration        ████████████████████ 100%
End-to-End ML Pipeline         ████████████████████ 100%

Remaining Project Work        ████░░░░░░░░░░░░░░░░ ~15%
```

---

## Future Improvements

* Real-world disruption datasets
* Real-time news ingestion
* More disruption categories
* Supplier and warehouse-specific disruption models
* Improved GNN architectures
* Real-time risk propagation
* Automated alert generation
* Advanced dashboard analytics
* Larger and more diverse training datasets

---

## Project Goal

AtmoGraph aims to provide an intelligent graph-based system that can:

1. Detect supply-chain disruptions from news.
2. Identify affected supply-chain entities.
3. Update their risk state in Neo4j.
4. Understand graph relationships between supply-chain entities.
5. Predict downstream ripple effects using GCN.
6. Estimate delay propagation across the network.
7. Classify predicted risk levels.
8. Store predictions back into the supply-chain graph.
9. Visualize the impact through a dashboard.

---

## Conclusion

AtmoGraph combines **NLP, Graph Databases and Graph Neural Networks** into an end-to-end supply-chain intelligence pipeline.

The current ML pipeline successfully performs:

```text
News
 ↓
NLP
 ↓
Entity Mapping
 ↓
Severity + Disruption Type
 ↓
Neo4j Risk Update
 ↓
GCN V2
 ↓
Ripple Effect Prediction
 ↓
Predicted Delay + Risk
 ↓
Neo4j
```

The core **ML + Neo4j intelligence pipeline is now operational**, with the remaining work focused primarily on broader testing, full team integration, dashboard validation, documentation and final project preparation.
