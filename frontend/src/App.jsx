import { ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const nodes = [
  {
    id: "supplier",
    position: { x: 50, y: 100 },
    data: { label: "Supplier" },
  },
  {
    id: "factory",
    position: { x: 250, y: 100 },
    data: { label: "Factory" },
  },
  {
    id: "port",
    position: { x: 450, y: 100 },
    data: { label: "Port" },
  },
  {
    id: "warehouse",
    position: { x: 650, y: 100 },
    data: { label: "Warehouse" },
  },
  {
    id: "market",
    position: { x: 850, y: 100 },
    data: { label: "Market" },
  },
];

const edges = [
  {
    id: "supplier-factory",
    source: "supplier",
    target: "factory",
  },
  {
    id: "factory-port",
    source: "factory",
    target: "port",
  },
  {
    id: "port-warehouse",
    source: "port",
    target: "warehouse",
  },
  {
    id: "warehouse-market",
    source: "warehouse",
    target: "market",
  },
];

function App() {
  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}

export default App;