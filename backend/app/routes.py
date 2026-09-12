from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .database import driver


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

    with driver.session() as session:
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

    with driver.session() as session:
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

    with driver.session() as session:
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

    with driver.session() as session:
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

    with driver.session() as session:
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

    with driver.session() as session:
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

    with driver.session() as session:
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
                    "label": source.get("name")
                    or source.get("type"),
                    "type": list(source.labels)[0]
                }

            if target:
                node_id = target.element_id

                nodes[node_id] = {
                    "id": node_id,
                    "label": target.get("name")
                    or target.get("type"),
                    "type": list(target.labels)[0]
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
    MATCH (d:Disruption {type: $disruption_type})
    MATCH (p:Port)-[:AFFECTED_BY]->(d)
    MATCH (c:Company)-[:USES_PORT]->(p)

    OPTIONAL MATCH path =
        (s:Company)-[:SUPPLIES*1..5]->(c)

    RETURN d,
           p.name AS port,
           c.name AS affected_company,
           collect(DISTINCT {
               supplier: s.name,
               supplier_level: length(path) + 1
           }) AS suppliers
    """

    with driver.session() as session:
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

    disruption = dict(record["d"])

    ripple_effect = []

    # -----------------------------
    # Directly affected company
    # -----------------------------

    direct_risk = calculate_risk(
        disruption.get("severity", "Low"),
        1
    )

    ripple_effect.append({
        "company": record["affected_company"],
        "port": record["port"],
        "impact_level": 1,
        "risk": direct_risk["risk"],
        "risk_score": direct_risk["risk_score"]
    })

    # -----------------------------
    # Supplier ripple effects
    # -----------------------------

    for supplier in record["suppliers"]:

        supplier_name = supplier.get("supplier")
        supplier_level = supplier.get(
            "supplier_level"
        )

        if (
            supplier_name is None
            or supplier_level is None
        ):
            continue

        impact_level = int(supplier_level)

        supplier_risk = calculate_risk(
            disruption.get("severity", "Low"),
            impact_level
        )

        ripple_effect.append({
            "company": supplier_name,
            "port": record["port"],
            "impact_level": impact_level,
            "risk": supplier_risk["risk"],
            "risk_score": supplier_risk["risk_score"]
        })

    return {
        "disruption": disruption,
        "ripple_effect": ripple_effect
    }