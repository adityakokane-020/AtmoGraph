import { useEffect, useState } from "react";

import {
  ReactFlow,
  Controls,
  Background,
  Handle,
  Position,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

// -----------------------------
// Custom Node
// -----------------------------

function SupplyChainNode({ data }) {
  return (
    <div
      className={`supply-chain-node ${data.riskClass}`}
      style={{
        minWidth: "160px",
        padding: "14px 18px",
        borderRadius: "12px",
        background: "#ffffff",
        color: "#111827",
        border: "2px solid #64748b",
        boxShadow: "0 4px 12px rgba(0,0,0,0.25)",
        textAlign: "center",
        fontWeight: "600",
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        style={{
          background: "#64748b",
          width: "8px",
          height: "8px",
        }}
      />

      <div
        style={{
          fontSize: "14px",
          fontWeight: "700",
          marginBottom: "5px",
        }}
      >
        {data.label}
      </div>

      <div
        style={{
          fontSize: "11px",
          color: "#64748b",
        }}
      >
        {data.type}
      </div>

      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: "#64748b",
          width: "8px",
          height: "8px",
        }}
      />
    </div>
  );
}

// -----------------------------
// Node Types
// -----------------------------

const nodeTypes = {
  supplyChain: SupplyChainNode,
};

// -----------------------------
// Risk Helper
// -----------------------------

const getRiskClass = (risk) => {
  if (risk === "High") {
    return "high-risk";
  }

  if (risk === "Medium") {
    return "medium-risk";
  }

  return "low-risk";
};

const getRiskFromImpactLevel = (impactLevel) => {
  if (impactLevel >= 2) {
    return "High";
  }

  if (impactLevel === 1) {
    return "Medium";
  }

  return "Low";
};

// -----------------------------
// Main App
// -----------------------------

function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const [selectedNode, setSelectedNode] = useState(null);
  const [search, setSearch] = useState("");

  const [rippleNodes, setRippleNodes] = useState([]);
  const [ripplePrediction, setRipplePrediction] = useState(null);

  const [showGraph, setShowGraph] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // -----------------------------
  // Load Graph From Backend
  // -----------------------------

  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      setError("");

      try {
        const response = await fetch(`${API_URL}/graph`);

        if (!response.ok) {
          throw new Error(
            `Backend returned ${response.status}`
          );
        }

        const data = await response.json();

        console.log("Graph data received:", data);

        // -----------------------------
        // Create Node Positions
        // -----------------------------

        const graphNodes = data.nodes.map((node) => {
          let position = {
            x: 100,
            y: 300,
          };

          // Supplier
          if (node.label === "Steel Supplier Ltd") {
            position = {
              x: 80,
              y: 300,
            };
          }

          // Tata Motors
          else if (node.label === "Tata Motors") {
            position = {
              x: 360,
              y: 300,
            };
          }

          // Mumbai Port
          else if (node.label === "Mumbai Port") {
            position = {
              x: 640,
              y: 300,
            };
          }

          // Port Closure
          else if (node.label === "Port Closure") {
            position = {
              x: 920,
              y: 300,
            };
          }

          return {
            id: node.id,
            type: "supplyChain",
            position,

            data: {
              label: node.label || "Unnamed Node",
              type: node.type || "Unknown",
              location: "Not available",
              status: "Normal",
              risk: "Low",
              riskClass: "low-risk",
            },
          };
        });

        // -----------------------------
        // Create Relationships
        // -----------------------------

        const graphEdges = data.relationships.map(
          (relationship, index) => ({
            id: `edge-${index}`,

            source: relationship.source,
            target: relationship.target,

            label: relationship.type,

            type: "smoothstep",

            animated: false,

            style: {
              stroke: "#64748b",
              strokeWidth: 2,
            },

            labelStyle: {
              fill: "#ffffff",
              fontSize: 11,
              fontWeight: 700,
            },

            labelBgStyle: {
              fill: "#111827",
              fillOpacity: 0.85,
            },

            labelBgPadding: [6, 4],
            labelBgBorderRadius: 4,
          })
        );

        setNodes(graphNodes);
        setEdges(graphEdges);
      } catch (err) {
        console.error(
          "Failed to load graph:",
          err
        );

        setError(
          "Unable to connect to the AtmoGraph backend. Make sure FastAPI is running."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, []);

  // -----------------------------
  // Node Click / Ripple Effect
  // -----------------------------

  const handleNodeClick = async (event, node) => {
    setSelectedNode(node);
    setError("");

    // -----------------------------
    // Disruption Node
    // -----------------------------

    if (node.data.type === "Disruption") {
      try {
        const response = await fetch(
          `${API_URL}/ripple-effect/${encodeURIComponent(
            node.data.label
          )}`
        );

        if (!response.ok) {
          throw new Error(
            `Backend returned ${response.status}`
          );
        }

        const data = await response.json();

        console.log(
          "Ripple prediction received:",
          data
        );

        setRipplePrediction(data);

        // -----------------------------
        // Create impact lookup
        // -----------------------------

        const impactLookup = {};

        data.ripple_effect.forEach((impact) => {
          impactLookup[impact.company] =
            impact.impact_level;
        });

        // -----------------------------
        // Update Node Risk
        // -----------------------------

        const updatedNodes = nodes.map(
          (graphNode) => {
            let risk = "Low";

            // Disruption gets its backend severity
            if (
              graphNode.id === node.id &&
              data.disruption.severity
            ) {
              risk = data.disruption.severity;
            }

            // Companies get risk from impact level
            else if (
              impactLookup[graphNode.data.label] !==
              undefined
            ) {
              risk = getRiskFromImpactLevel(
                impactLookup[graphNode.data.label]
              );
            }

            return {
              ...graphNode,

              data: {
                ...graphNode.data,
                risk,
                riskClass: getRiskClass(risk),
              },
            };
          }
        );

        setNodes(updatedNodes);

        // -----------------------------
        // Find Affected Frontend Nodes
        // -----------------------------

        const affectedCompanyNames =
          data.ripple_effect.map(
            (item) => item.company
          );

        const affectedNodeIds = updatedNodes
          .filter((graphNode) =>
            affectedCompanyNames.includes(
              graphNode.data.label
            )
          )
          .map((graphNode) => graphNode.id);

        // Also highlight the disruption itself
        affectedNodeIds.push(node.id);

        setRippleNodes([
          ...new Set(affectedNodeIds),
        ]);

        // Update selected node with new risk
        const updatedSelectedNode =
          updatedNodes.find(
            (graphNode) =>
              graphNode.id === node.id
          );

        if (updatedSelectedNode) {
          setSelectedNode(
            updatedSelectedNode
          );
        }
      } catch (err) {
        console.error(
          "Failed to load ripple prediction:",
          err
        );

        setRipplePrediction(null);
        setRippleNodes([node.id]);

        setError(
          "Unable to load ripple prediction from the backend."
        );
      }

      return;
    }

    // -----------------------------
    // Normal Graph Traversal
    // -----------------------------

    setRipplePrediction(null);

    const affectedNodes = [node.id];
    let currentNodes = [node.id];

    while (currentNodes.length > 0) {
      const nextNodes = edges
        .filter((edge) =>
          currentNodes.includes(edge.source)
        )
        .map((edge) => edge.target)
        .filter(
          (id) =>
            !affectedNodes.includes(id)
        );

      affectedNodes.push(...nextNodes);
      currentNodes = nextNodes;
    }

    setRippleNodes(affectedNodes);
  };

  // -----------------------------
  // Styled Nodes
  // -----------------------------

  const nodesWithRisk = nodes.map((node) => {
    const matchesSearch =
      search.trim() !== "" &&
      node.data.label
        .toLowerCase()
        .includes(search.toLowerCase());

    const isRippleNode =
      rippleNodes.includes(node.id);

    return {
      ...node,

      data: {
        ...node.data,

        riskClass: getRiskClass(
          node.data.risk
        ),
      },

      style: {
        ...(matchesSearch
          ? {
              boxShadow:
                "0 0 20px 6px #3b82f6",

              border:
                "3px solid #3b82f6",
            }
          : {}),

        ...(isRippleNode
          ? {
              boxShadow:
                "0 0 20px 6px #f97316",

              border:
                "3px solid #f97316",
            }
          : {}),
      },
    };
  });

  // -----------------------------
  // Styled Edges
  // -----------------------------

  const edgesWithRipple =
    edges.map((edge) => {
      const isRippleEdge =
        rippleNodes.includes(
          edge.source
        ) &&
        rippleNodes.includes(
          edge.target
        );

      return {
        ...edge,

        animated: isRippleEdge,

        style: isRippleEdge
          ? {
              stroke: "#f97316",
              strokeWidth: 4,
            }
          : {
              stroke: "#64748b",
              strokeWidth: 2,
            },
      };
    });

  // -----------------------------
  // Risk Counts
  // -----------------------------

  const lowRiskCount =
    nodes.filter(
      (node) =>
        node.data.risk === "Low"
    ).length;

  const mediumRiskCount =
    nodes.filter(
      (node) =>
        node.data.risk === "Medium"
    ).length;

  const highRiskCount =
    nodes.filter(
      (node) =>
        node.data.risk === "High"
    ).length;

  // -----------------------------
  // Clear Ripple
  // -----------------------------

  const clearRipple = () => {
    setRippleNodes([]);
    setRipplePrediction(null);
    setSelectedNode(null);

    // Reset all risks to Low
    setNodes((currentNodes) =>
      currentNodes.map((node) => ({
        ...node,

        data: {
          ...node.data,
          risk: "Low",
          riskClass: "low-risk",
        },
      }))
    );
  };

  // -----------------------------
  // Landing Page
  // -----------------------------

  if (!showGraph) {
    return (
      <div className="landing-page">
        <div className="landing-content">

          <div className="landing-badge">
            AI-POWERED SUPPLY CHAIN
            INTELLIGENCE
          </div>

          <h1>
            AtmoGraph
          </h1>

          <h2>
            Supply Chain Ripple Effect
            Predictor
          </h2>

          <p>
            Visualize supply chain networks,
            identify risk, and understand how
            disruptions propagate across
            connected entities.
          </p>

          <div className="landing-features">

            <div className="feature-card">
              <span>🌐</span>

              <h3>
                Network Graph
              </h3>

              <p>
                Explore interconnected
                supply chain entities.
              </p>
            </div>

            <div className="feature-card">
              <span>⚠️</span>

              <h3>
                Risk Analysis
              </h3>

              <p>
                Monitor and visualize
                supply chain risks.
              </p>
            </div>

            <div className="feature-card">
              <span>📈</span>

              <h3>
                Prediction
              </h3>

              <p>
                Understand potential
                downstream impacts.
              </p>
            </div>

          </div>

          <button
            className="show-graph-btn"
            onClick={() =>
              setShowGraph(true)
            }
          >
            Show Supply Chain Graph

            <span>
              →
            </span>
          </button>

        </div>
      </div>
    );
  }

  // -----------------------------
  // Graph Page
  // -----------------------------

  return (
    <div className="app">

      <header className="header">

        <h1>
          AtmoGraph
        </h1>

        <p>
          Supply Chain Ripple Effect
          Predictor
        </p>

      </header>

      <main className="graph-container">

        {/* Search */}

        <div className="search-box">

          <input
            type="text"
            placeholder="Search node..."
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
          />

        </div>

        {/* Risk Legend */}

        <div className="risk-legend">

          <h3>
            Risk Level
          </h3>

          <div>
            <span className="legend-dot low"></span>
            Low
          </div>

          <div>
            <span className="legend-dot medium"></span>
            Medium
          </div>

          <div>
            <span className="legend-dot high"></span>
            High
          </div>

          <div>
            <span className="legend-dot ripple"></span>
            Ripple Effect
          </div>

        </div>

        {/* Prediction Panel */}

        <div className="prediction-panel">

          <h3>
            Current Prediction
          </h3>

          {ripplePrediction ? (
            <>
              <div className="prediction-item">

                <strong>
                  {ripplePrediction.disruption.type}
                </strong>

                <span
                  className={
                    ripplePrediction.disruption
                      .severity === "High"
                      ? "prediction-high"
                      : "prediction-medium"
                  }
                >
                  {ripplePrediction.disruption.severity} Risk
                </span>

                <p>
                  {ripplePrediction.disruption.description}
                </p>

              </div>

              <div className="prediction-item">

                <strong>
                  Affected Entities
                </strong>

                <p>
                  {ripplePrediction.ripple_effect.length}
                  {" "}
                  companies impacted
                </p>

              </div>
            </>
          ) : (
            <div className="prediction-item">

              <strong>
                No disruption selected
              </strong>

              <p>
                Click a disruption node to
                run a ripple-effect prediction.
              </p>

            </div>
          )}

        </div>

        {/* Risk Summary */}

        <div className="risk-summary">

          <h3>
            Risk Overview
          </h3>

          <div className="risk-counts">

            <span className="risk-low">
              Low: {lowRiskCount}
            </span>

            <span className="risk-medium">
              Medium: {mediumRiskCount}
            </span>

            <span className="risk-high">
              High: {highRiskCount}
            </span>

          </div>

        </div>

        {/* Loading */}

        {loading && (

          <div className="ripple-info">

            <h3>
              Loading Graph...
            </h3>

            <p>
              Connecting to AtmoGraph
              backend.
            </p>

          </div>

        )}

        {/* Error */}

        {error && (

          <div className="ripple-info">

            <h3>
              Backend Connection Error
            </h3>

            <p>
              {error}
            </p>

          </div>

        )}

        {/* React Flow */}

        <ReactFlow
          nodes={nodesWithRisk}
          edges={edgesWithRipple}
          nodeTypes={nodeTypes}
          onNodeClick={handleNodeClick}
          fitView
          fitViewOptions={{
            padding: 0.15,
          }}
          minZoom={0.5}
          maxZoom={1.5}
          zoomOnScroll={false}
          zoomOnPinch={false}
          zoomOnDoubleClick={false}
          panOnDrag={true}
          nodesDraggable={false}
          nodesConnectable={false}
        >
          <Controls />
          <Background />
        </ReactFlow>

        {/* Ripple Information */}

        {rippleNodes.length > 0 && (

          <div className="ripple-info">

            <h3>
              Ripple Effect
            </h3>

            {ripplePrediction ? (

              <>

                <p>
                  <strong>
                    Disruption:
                  </strong>{" "}
                  {ripplePrediction.disruption.type}
                </p>

                <p>
                  <strong>
                    Severity:
                  </strong>{" "}
                  {ripplePrediction.disruption.severity}
                </p>

                <p>
                  <strong>
                    Description:
                  </strong>{" "}
                  {ripplePrediction.disruption.description}
                </p>

                <h4>
                  Impacted Companies
                </h4>

                {ripplePrediction.ripple_effect.map(
                  (impact) => (
                    <div
                      key={`${impact.company}-${impact.impact_level}`}
                      className="ripple-impact"
                      style={{
                        marginBottom: "8px",
                        padding: "8px",
                        borderRadius: "8px",
                        background:
                          "rgba(255,255,255,0.08)",
                      }}
                    >
                      <strong>
                        {impact.company}
                      </strong>

                      <div
                        style={{
                          fontSize: "12px",
                          marginTop: "3px",
                        }}
                      >
                        Impact Level{" "}
                        {impact.impact_level}
                      </div>

                    </div>
                  )
                )}

              </>

            ) : (

              <p>
                {rippleNodes.length}
                {" "}
                connected nodes affected
              </p>

            )}

            <button
              onClick={clearRipple}
            >
              Clear Ripple
            </button>

          </div>

        )}

        {/* Selected Node */}

        {selectedNode && (

          <div className="node-details">

            <h2>
              {selectedNode.data.label}
            </h2>

            <p>
              <strong>
                ID:
              </strong>{" "}
              {selectedNode.id}
            </p>

            <p>
              <strong>
                Type:
              </strong>{" "}
              {selectedNode.data.type}
            </p>

            <p>
              <strong>
                Location:
              </strong>{" "}
              {selectedNode.data.location}
            </p>

            <p>
              <strong>
                Status:
              </strong>{" "}
              {selectedNode.data.status}
            </p>

            <p>
              <strong>
                Risk:
              </strong>{" "}
              {selectedNode.data.risk}
            </p>

            <button
              onClick={() => {
                setSelectedNode(null);
                setRippleNodes([]);
              }}
            >
              Close
            </button>

          </div>

        )}

      </main>

    </div>
  );
}

export default App;