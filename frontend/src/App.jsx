import { useState } from "react";
import {
  ReactFlow,
  Controls,
  MiniMap,
  Background,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./App.css";

const nodes = [
  {
    id: "supplier",
    position: { x: 50, y: 250 },
    data: {
      label: "Main Supplier",
      type: "Supplier",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "factory-a",
    position: { x: 300, y: 100 },
    data: {
      label: "Factory A",
      type: "Factory",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "factory-b",
    position: { x: 300, y: 250 },
    data: {
      label: "Factory B",
      type: "Factory",
      location: "India",
      status: "Normal",
      risk: "Medium",
    },
  },

  {
    id: "factory-c",
    position: { x: 300, y: 400 },
    data: {
      label: "Factory C",
      type: "Factory",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "warehouse-a",
    position: { x: 550, y: 100 },
    data: {
      label: "Warehouse A",
      type: "Warehouse",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "warehouse-b",
    position: { x: 550, y: 250 },
    data: {
      label: "Warehouse B",
      type: "Warehouse",
      location: "India",
      status: "Normal",
      risk: "Medium",
    },
  },

  {
    id: "warehouse-c",
    position: { x: 550, y: 400 },
    data: {
      label: "Warehouse C",
      type: "Warehouse",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "market-a",
    position: { x: 800, y: 100 },
    data: {
      label: "Market A",
      type: "Market",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "market-b",
    position: { x: 800, y: 250 },
    data: {
      label: "Market B",
      type: "Market",
      location: "India",
      status: "Normal",
      risk: "Medium",
    },
  },

  {
    id: "market-c",
    position: { x: 800, y: 400 },
    data: {
      label: "Market C",
      type: "Market",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },
];

const edges = [
  {
    id: "supplier-factory-a",
    source: "supplier",
    target: "factory-a",
  },
  {
    id: "supplier-factory-b",
    source: "supplier",
    target: "factory-b",
  },
  {
    id: "supplier-factory-c",
    source: "supplier",
    target: "factory-c",
  },

  {
    id: "factory-a-warehouse-a",
    source: "factory-a",
    target: "warehouse-a",
  },
  {
    id: "factory-b-warehouse-b",
    source: "factory-b",
    target: "warehouse-b",
  },
  {
    id: "factory-c-warehouse-c",
    source: "factory-c",
    target: "warehouse-c",
  },

  {
    id: "warehouse-a-market-a",
    source: "warehouse-a",
    target: "market-a",
  },
  {
    id: "warehouse-b-market-b",
    source: "warehouse-b",
    target: "market-b",
  },
  {
    id: "warehouse-c-market-c",
    source: "warehouse-c",
    target: "market-c",
  },
];

const getRiskClass = (risk) => {
  if (risk === "High") {
    return "high-risk";
  }

  if (risk === "Medium") {
    return "medium-risk";
  }

  return "low-risk";
};

function App() {
  const [selectedNode, setSelectedNode] = useState(null);
  const [search, setSearch] = useState("");

  const handleNodeClick = (event, node) => {
    setSelectedNode(node);
  };

  const nodesWithRisk = nodes.map((node) => {
    const matchesSearch =
      search.trim() !== "" &&
      node.data.label.toLowerCase().includes(search.toLowerCase());

    return {
      ...node,

      className: getRiskClass(node.data.risk),

      style: matchesSearch
        ? {
          boxShadow: "0 0 20px 6px #3b82f6",
          border: "3px solid #3b82f6",
        }
        : {},
    };
  });
  const lowRiskCount = nodes.filter(
    (node) => node.data.risk === "Low"
  ).length;

  const mediumRiskCount = nodes.filter(
    (node) => node.data.risk === "Medium"
  ).length;

  const highRiskCount = nodes.filter(
    (node) => node.data.risk === "High"
  ).length;

  return (
    <div className="app">

      <header className="header">
        <h1>AtmoGraph</h1>
        <p>Supply Chain Ripple Effect Predictor</p>
      </header>

      <main className="graph-container">

        <div className="risk-summary">
          <h3>Risk Overview</h3>

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

        <div className="search-box">
          <input
            type="text"
            placeholder="Search node..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>


        <ReactFlow
          nodes={nodesWithRisk}
          edges={edges}
          onNodeClick={handleNodeClick}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background />
        </ReactFlow>

        {selectedNode && (
          <div className="node-details">

            <h2>{selectedNode.data.label}</h2>

            <p>
              <strong>ID:</strong> {selectedNode.id}
            </p>

            <p>
              <strong>Type:</strong> {selectedNode.data.type}
            </p>

            <p>
              <strong>Location:</strong> {selectedNode.data.location}
            </p>

            <p>
              <strong>Status:</strong> {selectedNode.data.status}
            </p>

            <p>
              <strong>Risk:</strong> {selectedNode.data.risk}
            </p>

            <button onClick={() => setSelectedNode(null)}>
              Close
            </button>

          </div>
        )}

      </main>

    </div>
  );
}

export default App;