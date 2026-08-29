import { useState } from "react";
import { ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import "./App.css";

const nodes = [
  {
    id: "supplier",
    position: { x: 50, y: 250 },
    data: { label: "Supplier" },
  },

  {
    id: "factory-a",
    position: { x: 300, y: 100 },
    data: { label: "Factory A" },
  },
  {
    id: "factory-b",
    position: { x: 300, y: 250 },
    data: { label: "Factory B" },
  },
  {
    id: "factory-c",
    position: { x: 300, y: 400 },
    data: { label: "Factory C" },
  },

  {
    id: "warehouse-a",
    position: { x: 550, y: 100 },
    data: { label: "Warehouse A" },
  },
  {
    id: "warehouse-b",
    position: { x: 550, y: 250 },
    data: { label: "Warehouse B" },
  },
  {
    id: "warehouse-c",
    position: { x: 550, y: 400 },
    data: { label: "Warehouse C" },
  },

  {
    id: "market-a",
    position: { x: 800, y: 100 },
    data: { label: "Market A" },
  },
  {
    id: "market-b",
    position: { x: 800, y: 250 },
    data: { label: "Market B" },
  },
  {
    id: "market-c",
    position: { x: 800, y: 400 },
    data: { label: "Market C" },
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

function App() {
  const [selectedNode, setSelectedNode] = useState(null);

  const handleNodeClick = (event, node) => {
    setSelectedNode(node);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>AtmoGraph</h1>
        <p>Supply Chain Ripple Effect Predictor</p>
      </header>

      <main className="graph-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={handleNodeClick}
        />

        {selectedNode && (
          <div className="node-details">
            <h2>{selectedNode.data.label}</h2>

            <p>
              <strong>ID:</strong> {selectedNode.id}
            </p>

            <p>
              <strong>Status:</strong> Normal
            </p>

            <p>
              <strong>Risk:</strong> Low
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