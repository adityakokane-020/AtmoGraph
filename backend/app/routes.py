from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .database import driver, NEO4J_DATABASE


router = APIRouter()


# -----------------------------
# Company
# -----------------------------

class Company(BaseModel):
    name: str
    industry: str
    country: str


@router.post("/companies")
def create_company(company: Company):

    query = """
    MERGE (c:Company {name: $name})
    SET c.industry = $industry,
        c.country = $country
    RETURN c
    """

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            query,
            name=company.name,
            industry=company.industry,
            country=company.country
        )

        record = result.single()

    return {
        "message": "Company created successfully",
        "company": dict(record["c"])
    }


# -----------------------------
# Supply Relationship
# -----------------------------

class SupplyRelationship(BaseModel):
    supplier: str
    company: str


@router.post("/relationships/supply")
def create_supply_relationship(data: SupplyRelationship):

    query = """
    MATCH (s:Company {name: $supplier})
    MATCH (c:Company {name: $company})
    MERGE (s)-[r:SUPPLIES]->(c)
    RETURN s, r, c
    """

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            query,
            supplier=data.supplier,
            company=data.company
        )

        record = result.single()

    if not record:
        return {
            "message": "Supplier or company not found"
        }

    return {
        "message": "Supply relationship created successfully",
        "supplier": data.supplier,
        "company": data.company
    }


# -----------------------------
# Port
# -----------------------------

class Port(BaseModel):
    name: str
    country: str


@router.post("/ports")
def create_port(port: Port):

    query = """
    MERGE (p:Port {name: $name})
    SET p.country = $country
    RETURN p
    """

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            query,
            name=port.name,
            country=port.country
        )

        record = result.single()

    return {
        "message": "Port created successfully",
        "port": dict(record["p"])
    }


# -----------------------------
# Company Uses Port
# -----------------------------

class PortRelationship(BaseModel):
    company: str
    port: str


@router.post("/relationships/uses-port")
def create_port_relationship(data: PortRelationship):

    query = """
    MATCH (c:Company {name: $company})
    MATCH (p:Port {name: $port})
    MERGE (c)-[r:USES_PORT]->(p)
    RETURN c, r, p
    """

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            query,
            company=data.company,
            port=data.port
        )

        record = result.single()

    if not record:
        return {
            "message": "Company or port not found"
        }

    return {
        "message": "Company-Port relationship created successfully",
        "company": data.company,
        "port": data.port
    }


# -----------------------------
# Disruption
# -----------------------------

class Disruption(BaseModel):
    type: str
    description: str
    severity: str


@router.post("/disruptions")
def create_disruption(disruption: Disruption):

    query = """
    CREATE (d:Disruption {
        type: $type,
        description: $description,
        severity: $severity
    })
    RETURN d
    """

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            query,
            type=disruption.type,
            description=disruption.description,
            severity=disruption.severity
        )

        record = result.single()

    return {
        "message": "Disruption created successfully",
        "disruption": dict(record["d"])
    }


# -----------------------------
# Port Affected By Disruption
# -----------------------------

class DisruptionRelationship(BaseModel):
    port: str
    disruption_type: str


@router.post("/relationships/affected-by")
def create_disruption_relationship(
    data: DisruptionRelationship
):

    query = """
    MATCH (p:Port {name: $port})
    MATCH (d:Disruption {type: $disruption_type})
    MERGE (p)-[r:AFFECTED_BY]->(d)
    RETURN p, r, d
    """

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            query,
            port=data.port,
            disruption_type=data.disruption_type
        )

        record = result.single()

    if not record:
        return {
            "message": "Port or disruption not found"
        }

    return {
        "message": "Disruption relationship created successfully",
        "port": data.port,
        "disruption": data.disruption_type
    }


# -----------------------------
# Graph
# -----------------------------

@router.get("/graph")
def get_graph():
    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(query)

        nodes = {}
        relationships = []

        for record in result:
            source = record["n"]
            relationship = record["r"]
            target = record["m"]

            if source:
                node_id = source.element_id

                nodes[node_id] = {
                        "id": node_id,
                        "label": source.get("name") or source.get("type"),
                        "type": list(source.labels)[0],
                        "country": source.get("country"),
                        "risk": source.get("risk"),
                        "capacity": source.get("capacity"),
                        "delay": source.get("delay"),
                        "disruption": source.get("disruption"),
                        "disruption_type": source.get("disruption_type"),
                        "predicted_risk": source.get("predicted_risk"),
                        "predicted_delay": source.get("predicted_delay")
                    }
            if target:
                node_id = target.element_id

                nodes[node_id] = {
                        "id": node_id,
                        "label": target.get("name") or target.get("type"),
                        "type": list(target.labels)[0],
                        "country": target.get("country"),
                        "risk": target.get("risk"),
                        "capacity": target.get("capacity"),
                        "delay": target.get("delay"),
                        "disruption": target.get("disruption"),
                        "disruption_type": target.get("disruption_type"),
                        "predicted_risk": target.get("predicted_risk"),
                        "predicted_delay": target.get("predicted_delay")
                        }

            if relationship is not None:
                relationships.append({
                    "source": relationship.start_node.element_id,
                    "target": relationship.end_node.element_id,
                    "type": relationship.type
                })

    return {
        "nodes": list(nodes.values()),
        "relationships": relationships
    }
# -----------------------------
# Risk Calculation
# -----------------------------

def calculate_risk(severity, impact_level):

    severity_scores = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }

    severity_score = severity_scores.get(
        severity,
        1
    )

    risk_score = (
        severity_score * 2
        + impact_level
    )

    if risk_score >= 7:
        risk = "High"

    elif risk_score >= 5:
        risk = "Medium"

    else:
        risk = "Low"

    return {
        "risk": risk,
        "risk_score": risk_score
    }


# -----------------------------
# Ripple Effect Prediction
# -----------------------------

@router.get("/ripple-effect/{disruption_type}")
def get_ripple_effect(disruption_type: str):

    query = """
MATCH (start:SupplyChainNode)
WHERE start.disruption = 1
  AND start.disruption_type = $disruption_type

MATCH path =
    (start)-[*0..5]->(target:SupplyChainNode)

WITH start, path, target
WHERE target <> start

RETURN
    start.name AS disruption_node,
    start.risk AS disruption_risk,
    start.disruption_type AS disruption_type,
    collect(DISTINCT {
        node_id: target.id,
        node_name: target.name,
        node_type: target.type,
        risk: target.predicted_risk,
        predicted_delay: target.predicted_delay,
        path_length: length(path)
    }) AS affected_nodes
"""

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            query,
            disruption_type=disruption_type
        )

        record = result.single()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Disruption not found"
        )

    disruption = {
        "node": record["disruption_node"],
        "risk": record["disruption_risk"],
        "type": record["disruption_type"]
    }

    ripple_effect = []

    for node in record["affected_nodes"]:
        ripple_effect.append({
            "node_id": node["node_id"],
            "node_name": node["node_name"],
            "node_type": node["node_type"],
            "risk": node["risk"] or "Low",
            "predicted_delay": node["predicted_delay"] or 0,
            "impact_level": node["path_length"]
        })

    return {
        "disruption": disruption,
        "ripple_effect": ripple_effect
    }
# -----------------------------
# Ripple Effect by Any Node
# -----------------------------

@router.get("/ripple-effect/node/{node_id}")
def get_ripple_effect_by_node(node_id: str):

    query = """
    MATCH (start:SupplyChainNode)
WHERE elementId(start) = $node_id

    MATCH path =
        (start)-[*0..5]->(target:SupplyChainNode)

    WITH start, path, target
    WHERE target <> start

    RETURN
        start.name AS disruption_node,
        start.risk AS disruption_risk,
        collect(DISTINCT {
            node_id: target.id,
            node_name: target.name,
            node_type: target.type,
            risk: target.predicted_risk,
            predicted_delay: target.predicted_delay,
            path_length: length(path)
        }) AS affected_nodes
    """

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(
            query,
            node_id=node_id
        )

        record = result.single()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Node not found"
        )

    ripple_effect = []

    for node in record["affected_nodes"]:
        ripple_effect.append({
            "node_id": node["node_id"],
            "node_name": node["node_name"],
            "node_type": node["node_type"],
            "risk": node["risk"] or "Low",
            "predicted_delay": node["predicted_delay"] or 0,
            "impact_level": node["path_length"]
        })

    return {
        "disruption": {
            "node": record["disruption_node"],
            "risk": record["disruption_risk"] or "Low",
            "type": "Simulated Disruption"
        },
        "ripple_effect": ripple_effect
    }

# ==========================================
# GNN MODEL METRICS
# ==========================================

@router.get("/model-metrics")
def get_model_metrics():

    import pandas as pd
    from pathlib import Path
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    import math

    BASE_DIR = Path(__file__).resolve().parents[2]

    prediction_file = (
        BASE_DIR
        / "ml"
        / "data"
        / "gcn_v2_test_predictions.csv"
    )

    if not prediction_file.exists():
        raise HTTPException(
            status_code=404,
            detail="GNN prediction file not found."
        )

    df = pd.read_csv(prediction_file)

    actual = df["actual_delay"]
    predicted = df["predicted_delay"]

    mae = mean_absolute_error(actual, predicted)
    rmse = math.sqrt(mean_squared_error(actual, predicted))
    r2 = r2_score(actual, predicted)

    return {
        "model": "Ripple GCN V2",
        "test_predictions": len(df),
        "mae": round(float(mae), 3),
        "rmse": round(float(rmse), 3),
        "r2": round(float(r2), 3)
    }