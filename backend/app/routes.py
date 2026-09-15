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

    with driver.session(database="atmograph") as session:
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

    with driver.session(database="atmograph") as session:
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

    with driver.session(database="atmograph") as session:
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

    with driver.session(database="atmograph") as session:
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

    with driver.session(database="atmograph") as session:
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

    with driver.session(database="atmograph") as session:
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

    with driver.session(database="atmograph") as session:
        result = session.run(query)

        nodes = {}
        relationships = []

        for record in result:

            source = record["n"]
            relationship = record["r"]
            target = record["m"]

            # SOURCE NODE
            if source:
                node_id = source.element_id

                nodes[node_id] = {
                    "id": node_id,
                    "label": source.get("name")
                    or source.get("type")
                    or source.get("id"),
                    "type": source.get("type", "Unknown"),
                    "country": source.get("country", "Unknown"),
                    "risk": source.get("risk", "Low"),
                    "predicted_risk": source.get(
                        "predicted_risk",
                        source.get("risk", "Low")
                    ),
                    "predicted_delay": source.get(
                        "predicted_delay",
                        0
                    ),
                    "delay": source.get("delay", 0),
                    "capacity": source.get("capacity", 0)
                }

            # TARGET NODE
            if target:
                node_id = target.element_id

                nodes[node_id] = {
                    "id": node_id,
                    "label": target.get("name")
                    or target.get("type")
                    or target.get("id"),
                    "type": target.get("type", "Unknown"),
                    "country": target.get("country", "Unknown"),
                    "risk": target.get("risk", "Low"),
                    "predicted_risk": target.get(
                        "predicted_risk",
                        target.get("risk", "Low")
                    ),
                    "predicted_delay": target.get(
                        "predicted_delay",
                        0
                    ),
                    "delay": target.get("delay", 0),
                    "capacity": target.get("capacity", 0)
                }

            # RELATIONSHIP
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