import { useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  MarkerType,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";
// ========================================
// INITIAL GRAPH DATA
// ========================================

const initialNodes = [
  {
    id: "supplier",
    position: { x: 80, y: 250 },
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
    position: { x: 350, y: 100 },
    data: {
      label: "Factory A",
      type: "Factory",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "warehouse-a",
    position: { x: 620, y: 100 },
    data: {
      label: "Warehouse A",
      type: "Warehouse",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "market-a",
    position: { x: 890, y: 100 },
    data: {
      label: "Market A",
      type: "Market",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "factory-b",
    position: { x: 350, y: 250 },
    data: {
      label: "Factory B",
      type: "Factory",
      location: "India",
      status: "Normal",
      risk: "Medium",
    },
  },

  {
    id: "warehouse-b",
    position: { x: 620, y: 250 },
    data: {
      label: "Warehouse B",
      type: "Warehouse",
      location: "India",
      status: "At Risk",
      risk: "Medium",
    },
  },

  {
    id: "market-b",
    position: { x: 890, y: 250 },
    data: {
      label: "Market B",
      type: "Market",
      location: "India",
      status: "At Risk",
      risk: "Medium",
    },
  },

  {
    id: "factory-c",
    position: { x: 350, y: 400 },
    data: {
      label: "Factory C",
      type: "Factory",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "warehouse-c",
    position: { x: 620, y: 400 },
    data: {
      label: "Warehouse C",
      type: "Warehouse",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },

  {
    id: "market-c",
    position: { x: 890, y: 400 },
    data: {
      label: "Market C",
      type: "Market",
      location: "India",
      status: "Normal",
      risk: "Low",
    },
  },
];


const initialEdges = [
  {
    id: "supplier-factory-a",
    source: "supplier",
    target: "factory-a",
  },
  {
    id: "factory-a-warehouse-a",
    source: "factory-a",
    target: "warehouse-a",
  },
  {
    id: "warehouse-a-market-a",
    source: "warehouse-a",
    target: "market-a",
  },

  {
    id: "supplier-factory-b",
    source: "supplier",
    target: "factory-b",
  },
  {
    id: "factory-b-warehouse-b",
    source: "factory-b",
    target: "warehouse-b",
  },
  {
    id: "warehouse-b-market-b",
    source: "warehouse-b",
    target: "market-b",
  },

  {
    id: "supplier-factory-c",
    source: "supplier",
    target: "factory-c",
  },
  {
    id: "factory-c-warehouse-c",
    source: "factory-c",
    target: "warehouse-c",
  },
  {
    id: "warehouse-c-market-c",
    source: "warehouse-c",
    target: "market-c",
  },
].map((edge) => ({
  ...edge,
  type: "smoothstep",
  markerEnd: {
    type: MarkerType.ArrowClosed,
    width: 18,
    height: 18,
  },
}));


// ========================================
// APP
// ========================================

function App() {
  const [showGraph, setShowGraph] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [loadingGraph, setLoadingGraph] = useState(false);
  const [graphError, setGraphError] = useState(null);

  const [nodes, setNodes, onNodesChange] =
    useNodesState(initialNodes);

  const [edges, setEdges, onEdgesChange] =
    useEdgesState(initialEdges);
// ========================================
// GNN MODEL METRICS
// ========================================
  useEffect(() => {
    const fetchGraph = async () => {
      try {
        setLoadingGraph(true);
        setGraphError(null);

        const response = await fetch(`${API_URL}/graph`);

        if (!response.ok) {
          throw new Error("Failed to fetch graph from backend");
        }

        const data = await response.json();

        const backendNodes = data.nodes.map((node, index) => ({
          id: node.id,
          position: {
            x: (index % 4) * 270 + 80,
            y: Math.floor(index / 4) * 160 + 100,
          },
          data: {
            nodeId: node.id,
            label: node.label || node.id,
            type: node.type || "Unknown",
            location: node.country || "Unknown",
            status: node.disruption ? "Disrupted" : "Normal",
            risk: node.predicted_risk || node.risk || "Low",
            riskScore: node.predicted_delay || 0,
            predictedRisk: node.predicted_risk || node.risk || "Low",
            predictedDelay: node.predicted_delay || 0,

            disruption: node.disruption || null,
            disruptionType: node.disruption_type || null,
            capacity: node.capacity || 0,
          },
        }));

const backendEdges = data.relationships.map((edge) => ({
  id: `${edge.source}-${edge.target}`,
  source: edge.source,
  target: edge.target,
  type: "smoothstep",
  markerEnd: {
    type: MarkerType.ArrowClosed,
    width: 18,
    height: 18,
  },
}));

setNodes(backendNodes);
setEdges(backendEdges);

} catch (error) {
  console.error("Graph API Error:", error);
  setGraphError(error.message);
} finally {
  setLoadingGraph(false);
}
};

fetchGraph();

}, [setNodes, setEdges]);

  const [selectedNode, setSelectedNode] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");
  const [rippleNodes, setRippleNodes] = useState([]);

  const [modelMetrics, setModelMetrics] = useState(null);
  const [rippleResults, setRippleResults] = useState([]);

// ========================================
// GNN MODEL METRICS
// ========================================

useEffect(() => {
  const fetchModelMetrics = async () => {
    try {
      const response = await fetch(
        `${API_URL}/model-metrics`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch model metrics");
      }

      const data = await response.json();

      setModelMetrics(data);

    } catch (error) {
      console.error("Model Metrics Error:", error);
    }
  };

  fetchModelMetrics();
}, []);
  // ========================================
  // RISK COUNTS
  // ========================================

  const riskCounts = useMemo(() => {
    return {
      low: nodes.filter(
        (node) => node.data.risk === "Low"
      ).length,

      medium: nodes.filter(
        (node) => node.data.risk === "Medium"
      ).length,

      high: nodes.filter(
        (node) => node.data.risk === "High"
      ).length,

      critical: nodes.filter(
        (node) => node.data.risk === "Critical"
      ).length,
    };
  }, [nodes]);


  // ========================================
  // SEARCH + FILTER
  // ========================================

  const displayedNodes = useMemo(() => {
    return nodes.map((node) => {
      const matchesSearch =
        node.data.label
          .toLowerCase()
          .includes(searchTerm.toLowerCase());

      const matchesRisk =
        riskFilter === "All" ||
        node.data.risk === riskFilter;

      const isRipple =
        rippleNodes.includes(node.id);

      return {
        ...node,

        hidden: !matchesSearch || !matchesRisk,

        className: `
          risk-${node.data.risk.toLowerCase()}
          ${isRipple ? "ripple-node" : ""}
          ${selectedNode?.id === node.id ? "selected-node" : ""}
        `,

        style: {
          width: 155,
          padding: "12px 14px",
          borderRadius: "10px",
          border:
            isRipple
              ? "2px solid #f97316"
              : selectedNode?.id === node.id
                ? "2px solid #60a5fa"
                : node.data.risk === "Low"
                  ? "1.5px solid #22c55e"
                  : node.data.risk === "Medium"
                    ? "1.5px solid #eab308"
                    : "1.5px solid #ef4444",

          background:
            darkMode
              ? "#0f172a"
              : "#ffffff",

          color:
            darkMode
              ? "#f8fafc"
              : "#0f172a",

          boxShadow:
            isRipple
              ? "0 0 25px rgba(249,115,22,0.55)"
              : node.data.risk === "Low"
                ? "0 0 15px rgba(34,197,94,0.08)"
                : node.data.risk === "Medium"
                  ? "0 0 15px rgba(234,179,8,0.10)"
                  : "0 0 15px rgba(239,68,68,0.10)",
        },
      };
    });
  }, [
    nodes,
    searchTerm,
    riskFilter,
    rippleNodes,
    selectedNode,
    darkMode,
  ]);


  // ========================================
  // RIPPLE EFFECT
  // ========================================

  const calculateRipple = (nodeId) => {
    const affected = new Set();

    const visit = (currentId) => {
      edges.forEach((edge) => {
        if (edge.source === currentId) {
          if (!affected.has(edge.target)) {
            affected.add(edge.target);
            visit(edge.target);
          }
        }
      });
    };

    visit(nodeId);

    return [nodeId, ...Array.from(affected)];
  };


  const simulateRipple = async () => {
    if (!selectedNode) {
      alert("Please select a disrupted node first.");
      return;
    }

    const nodeId = selectedNode.data.nodeId;

    if (!nodeId) {
      alert("Node ID not found.");
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/ripple-effect/node/${encodeURIComponent(nodeId)}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch ripple effect from backend.");
      }

      const data = await response.json();

      setRippleResults(data.ripple_effect || []);

      const affectedNodeIds = data.ripple_effect.map(
        (item) => {
          const node = nodes.find(
            (n) => n.data.label === item.node_name
          );

          return node ? node.id : null;
        }
      ).filter(Boolean);

      setRippleNodes([
        selectedNode.id,
        ...affectedNodeIds,
      ]);

    } catch (error) {
      console.error("Ripple Effect API Error:", error);
      alert("Failed to calculate ripple effect.");
    }
  };


  const clearRipple = () => {
    setRippleNodes([]);
    setRippleResults([]);
  };


  // ========================================
  // NODE CLICK
  // ========================================

  const handleNodeClick = (_, node) => {
    setSelectedNode(node);
  };
  // ========================================
  // AI INSIGHT
  // ========================================

  const aiInsight = useMemo(() => {
    if (!selectedNode) {
      return {
        title: "No Node Selected",
        message:
          "Select a supply chain node to generate an AI-based risk insight.",
        impact: "None",
        recommendation:
          "Select a node from the supply chain graph.",
      };
    }

    // ========================================
    // ACTIVE RIPPLE SIMULATION
    // ========================================

    if (rippleNodes.length > 0) {
      const downstreamCount = rippleNodes.filter(
        (id) => id !== selectedNode.id
      ).length;

      return {
        title: "Ripple Simulation",
        message:
          `${selectedNode.data.label} was selected as the disruption source. ` +
          `The simulated disruption propagates through the connected downstream network.`,
        impact:
          `${downstreamCount} downstream node${downstreamCount !== 1 ? "s" : ""}`,
        recommendation:
          "Review the affected downstream nodes and evaluate alternative routes, suppliers, or inventory buffers.",
      };
    }

    // ========================================
    // NORMAL NODE RISK INSIGHT
    // ========================================

    const downstreamNodes = calculateRipple(selectedNode.id)
      .filter((id) => id !== selectedNode.id)
      .map((id) =>
        nodes.find((node) => node.id === id)
      )
      .filter(Boolean);

    const risk = selectedNode.data.risk;

    let title = "Low Risk";

    let message =
      `${selectedNode.data.label} currently shows low supply chain risk. ` +
      `The connected network appears relatively stable.`;

    let recommendation =
      "Continue regular monitoring of this node.";

    if (risk === "Medium") {
      title = "Potential Disruption";

      message =
        `${selectedNode.data.label} has a medium risk level. ` +
        `A disruption at this node could affect downstream supply chain operations.`;

      recommendation =
        "Monitor connected downstream nodes and prepare alternative routes.";
    }

    if (risk === "High") {
      title = "High Risk Detected";

      message =
        `${selectedNode.data.label} is currently classified as high risk. ` +
        `A disruption could significantly propagate through the supply chain.`;

      recommendation =
        "Take immediate preventive action and evaluate alternative suppliers or routes.";
    }

    if (risk === "Critical") {
      title = "Critical Risk Detected";

      message =
        `${selectedNode.data.label} is currently classified as critical risk. ` +
        `The disruption may cause severe downstream impact across the supply chain.`;

      recommendation =
        "Take immediate mitigation action and evaluate alternative routes, suppliers, or inventory buffers.";
    }

    return {
      title,
      message,
      impact:
        `${downstreamNodes.length} downstream node${downstreamNodes.length !== 1 ? "s" : ""}`,
      recommendation,
    };

  }, [selectedNode, nodes, edges, rippleNodes]);
  // ========================================
  // EXPORT REPORT
  // ========================================

  const exportReport = () => {
    const report = `
AtmoGraph Supply Chain Risk Report
===================================

Total Nodes: ${nodes.length}

Low Risk: ${riskCounts.low}
Medium Risk: ${riskCounts.medium}
High Risk: ${riskCounts.high}
Critical Risk: ${riskCounts.critical}

Selected Node:
${selectedNode ? selectedNode.data.label : "None"}

Ripple Affected Nodes:
${rippleNodes.length}

Generated by AtmoGraph
`;

    const blob = new Blob([report], {
      type: "text/plain",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = "AtmoGraph_Report.txt";

    link.click();

    URL.revokeObjectURL(url);
  };


  // ========================================
  // LANDING PAGE
  // ========================================

  if (!showGraph) {
    return (
      <div className="landing-page">

        <div className="landing-content">

          <div className="landing-badge">
            AI-POWERED SUPPLY CHAIN INTELLIGENCE
          </div>

          <h1>AtmoGraph</h1>

          <h2>
            Supply Chain Ripple Effect Predictor
          </h2>

          <p>
            Visualize interconnected supply chains,
            identify risk, and understand how
            disruptions propagate through the network.
          </p>
          <div className="backend-status">
            <span className="status-dot"></span>
            Backend Connected
          </div>
          <div className="landing-features">

            <div className="feature-card">
              <div>🌐</div>
              <h3>Graph Intelligence</h3>
              <p>
                Model suppliers, factories,
                warehouses and markets as
                interconnected nodes.
              </p>
            </div>

            <div className="feature-card">
              <div>⚠️</div>
              <h3>Risk Analysis</h3>
              <p>
                Identify low, medium and
                high-risk areas in the supply chain.
              </p>
            </div>

            <div className="feature-card">
              <div>🔥</div>
              <h3>Ripple Prediction</h3>
              <p>
                Understand how a disruption
                can propagate downstream.
              </p>
            </div>

          </div>

          <button
            onClick={() => setShowGraph(true)}
          >
            Open Dashboard →
          </button>

        </div>

      </div>
    );
  }


  // ========================================
  // DASHBOARD
  // ========================================

  return (
    <div
      className={`dashboard ${darkMode ? "dark" : "light"
        }`}
    >

      {/* ================================== */}
      {/* SIDEBAR */}
      {/* ================================== */}

      <aside className="sidebar">

        <div className="sidebar-logo">
          <div className="logo-mark">A</div>

          <div>
            <h2>AtmoGraph</h2>
            <span>Supply Intelligence</span>
          </div>
        </div>


        <nav className="sidebar-nav">

          <button className="nav-item active">
            <span>⌂</span>
            Dashboard
          </button>

          <button className="nav-item">
            <span>⌘</span>
            Graph View
          </button>

          <button className="nav-item">
            <span>◫</span>
            Risk Analysis
          </button>

          <button className="nav-item">
            <span>◇</span>
            Scenarios
          </button>

          <button className="nav-item">
            <span>♧</span>
            Alerts
            <span className="alert-badge">3</span>
          </button>

          <button className="nav-item">
            <span>▤</span>
            Reports
          </button>

          <button className="nav-item">
            <span>⚙</span>
            Settings
          </button>

        </nav>


        <div className="system-status">

          <div className="status-title">
            System Status
          </div>

          <div className="status-online">
            <span></span>
            Operational
          </div>

          <p>Last Updated</p>

          <strong>
            07 Sep 2026, 11:30 PM
          </strong>

        </div>

      </aside>


      {/* ================================== */}
      {/* MAIN */}
      {/* ================================== */}

      <main className="main-content">

        {/* TOP BAR */}

        <header className="topbar">

          <div>
            <h1>Supply Chain Dashboard</h1>

            <p>
              Monitor and predict supply chain ripple effects
            </p>
          </div>


          <div className="topbar-actions">

            <button
              className="theme-toggle"
              onClick={() =>
                setDarkMode(!darkMode)
              }
            >
              {darkMode ? "☾" : "☀"}
            </button>

            <button
              className="export-btn"
              onClick={exportReport}
            >
              ↓ &nbsp; Export Report
            </button>

          </div>

        </header>


        {/* ================================== */}
        {/* SUMMARY CARDS */}
        {/* ================================== */}

        <section className="summary-grid">

          <div className="dashboard-card risk-card">

            <h3>Risk Overview</h3>

            <div className="risk-row">
              <span>
                <i className="dot low"></i>
                Low Risk
              </span>

              <strong className="green">
                {riskCounts.low}
              </strong>
            </div>

            <div className="risk-row">
              <span>
                <i className="dot medium"></i>
                Medium Risk
              </span>

              <strong className="yellow">
                {riskCounts.medium}
              </strong>
            </div>

            <div className="risk-row">
              <span>
                <i className="dot high"></i>
                High Risk
              </span>

              <strong className="red">
                {riskCounts.high}
              </strong>
            </div>
            <div className="risk-row">
              <span>
                <i className="dot critical"></i>
                Critical Risk
              </span>

              <strong className="red">
                {riskCounts.critical}
              </strong>
            </div>

            <div className="total-row">
              Total Nodes
              <strong>{nodes.length}</strong>
            </div>

          </div>


          <div className="dashboard-card scenario-card">

            <h3>Active Scenario</h3>

            <strong>
              {selectedNode
                ? `${selectedNode.data.label} Selected`
                : "No Active Disruption"}
            </strong>

            <p>
              {rippleNodes.length > 0
                ? `${rippleNodes.length} nodes affected by ripple effect`
                : 'Select a node and click "Simulate Ripple" to start'}
            </p>

          </div>


          <div className="dashboard-card search-card">

            <label>Search Node</label>

            <div className="search-wrapper">

              <input
                type="text"
                placeholder="Search node..."
                value={searchTerm}
                onChange={(e) =>
                  setSearchTerm(e.target.value)
                }
              />

              <span>⌕</span>

            </div>

          </div>


          <div className="dashboard-card filter-card">

            <label>Filter by Risk</label>

            <select
              value={riskFilter}
              onChange={(e) =>
                setRiskFilter(e.target.value)
              }
            >
              <option value="All">All</option>
              <option value="Low">Low Risk</option>
              <option value="Medium">Medium Risk</option>
              <option value="High">High Risk</option>
              <option value="Critical">Critical Risk</option>
            </select>

          </div>


          <button
            className="simulate-btn"
            onClick={simulateRipple}
          >
            <span>〽</span>
            Simulate Ripple
          </button>

        </section>


        {/* ================================== */}
        {/* GRAPH + DETAILS */}
        {/* ================================== */}

        <section className="graph-section">

          <div className="graph-header">

            <div>
              <h2>Supply Chain Network</h2>

              <p>
                Interactive global supply chain graph
              </p>
            </div>

            {rippleNodes.length > 0 && (
              <button
                className="clear-ripple"
                onClick={clearRipple}
              >
                Clear Ripple
              </button>
            )}

          </div>


          <div className="graph-wrapper">

            <ReactFlow
              nodes={displayedNodes}
              edges={edges.map((edge) => ({
                ...edge,

                animated:
                  rippleNodes.includes(edge.source) &&
                  rippleNodes.includes(edge.target),

                style:
                  rippleNodes.includes(edge.source) &&
                    rippleNodes.includes(edge.target)
                    ? {
                      stroke: "#f97316",
                      strokeWidth: 3,
                    }
                    : {
                      stroke: darkMode
                        ? "#64748b"
                        : "#94a3b8",
                      strokeWidth: 1.8,
                    },
              }))}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={handleNodeClick}
              fitView
              minZoom={0.4}
              maxZoom={1.5}
              nodesDraggable={true}
              nodesConnectable={false}
            >

              <Background
                gap={20}
                size={1}
                color={
                  darkMode
                    ? "#334155"
                    : "#cbd5e1"
                }
              />

              <Controls />

            </ReactFlow>


            {/* ================================== */}
            {/* NODE DETAILS */}
            {/* ================================== */}

            {selectedNode && (

              <div className="node-details-panel">

                <button
                  className="close-details"
                  onClick={() =>
                    setSelectedNode(null)
                  }
                >
                  ×
                </button>

                <div className="node-icon">
                  {selectedNode.data.type === "Factory"
                    ? "🏭"
                    : selectedNode.data.type === "Warehouse"
                      ? "🏢"
                      : selectedNode.data.type === "Market"
                        ? "🛒"
                        : "🚚"}
                </div>

                <h2>
                  {selectedNode.data.label}
                </h2>

                <span
                  className={`risk-badge ${selectedNode.data.risk.toLowerCase()}`}
                >
                  {selectedNode.data.risk} Risk
                </span>


                <div className="details-list">

                  <div>
                    <span>Type</span>
                    <strong>
                      {selectedNode.data.type}
                    </strong>
                  </div>

                  <div>
                    <span>Location</span>
                    <strong>
                      {selectedNode.data.location}
                    </strong>
                  </div>

                  <div>
                    <span>Status</span>
                    <strong
                      className={
                        selectedNode.data.status === "Normal"
                          ? "green"
                          : "yellow"
                      }
                    >
                      {selectedNode.data.status}
                    </strong>
                  </div>

                  <div>
                    <span>Risk Level</span>
                    <strong>
                      {selectedNode.data.risk}
                    </strong>
                  </div>

                  <div>
                    <span>ID</span>
                    <strong>
                      {selectedNode.id}
                    </strong>
                  </div>

                </div>


                <div className="connected-section">

                  <h3>Connected To</h3>

                  <div>
                    <span>↑</span>
                    Upstream
                    <strong>
                      {edges.find(
                        (edge) =>
                          edge.target === selectedNode.id
                      )
                        ? nodes.find(
                          (node) =>
                            node.id ===
                            edges.find(
                              (edge) =>
                                edge.target ===
                                selectedNode.id
                            ).source
                        )?.data.label
                        : "None"}
                    </strong>
                  </div>

                  <div>
                    <span>↓</span>
                    Downstream
                    <strong>
                      {edges.find(
                        (edge) =>
                          edge.source === selectedNode.id
                      )
                        ? nodes.find(
                          (node) =>
                            node.id ===
                            edges.find(
                              (edge) =>
                                edge.source ===
                                selectedNode.id
                            ).target
                        )?.data.label
                        : "None"}
                    </strong>
                  </div>

                </div>
                <div className="ai-insight">

                  <div className="ai-insight-header">
                    <span>🤖</span>
                    <h3>AI Supply Chain Insight</h3>
                  </div>

                  <div className="ai-insight-status">
                    {aiInsight.title}
                  </div>

                  <p>
                    {aiInsight.message}
                  </p>

                  <div className="ai-insight-impact">
                    <span>Ripple Impact</span>
                    <strong>{aiInsight.impact}</strong>
                  </div>

                  <div className="ai-insight-recommendation">
                    <span>Recommendation</span>
                    <p>
                      {aiInsight.recommendation}
                    </p>
                  </div>

                </div>


                <button
                  className="view-details-btn"
                  onClick={simulateRipple}
                >
                  Simulate Ripple
                </button>

              </div>

            )}

          </div>

        </section>
        {/* ================================== */}
        {/* GNN RESULTS */}
        {/* ================================== */}

        <section className="results-grid">

          {/* MODEL PERFORMANCE */}

          <div className="analytics-card model-performance">

            <h3>GNN Model Performance</h3>

            <p className="results-subtitle">
              Ripple GCN V2 · Held-out test scenarios
            </p>

            {modelMetrics ? (

              <div className="metrics-grid">

                <div className="metric-box">
                  <span>MAE</span>
                  <strong>
                    {modelMetrics.mae}
                  </strong>
                  <small>days</small>
                </div>

                <div className="metric-box">
                  <span>RMSE</span>
                  <strong>
                    {modelMetrics.rmse}
                  </strong>
                  <small>days</small>
                </div>

                <div className="metric-box">
                  <span>R²</span>
                  <strong>
                    {modelMetrics.r2}
                  </strong>
                  <small>score</small>
                </div>

                <div className="metric-box">
                  <span>Predictions</span>
                  <strong>
                    {modelMetrics.test_predictions}
                  </strong>
                  <small>test samples</small>
                </div>

              </div>

            ) : (

              <p className="results-loading">
                Loading model performance...
              </p>

            )}

          </div>


          {/* RIPPLE PREDICTION */}

          <div className="analytics-card ripple-results-card">

            <h3>Ripple Prediction</h3>

            <p className="results-subtitle">
              Predicted downstream impact
            </p>

            {rippleResults.length > 0 ? (

              <div className="ripple-results-list">

                {rippleResults.map((item) => (

                  <div
                    className="ripple-result-row"
                    key={item.node_id}
                  >

                    <div className="ripple-node-info">

                      <strong>
                        {item.node_name}
                      </strong>

                      <span>
                        {item.node_type}
                      </span>

                    </div>

                    <div className="ripple-delay">

                      <strong>
                        {Number(item.predicted_delay).toFixed(2)}
                      </strong>

                      <span>
                        days
                      </span>

                    </div>

                    <div
                      className={
                        `ripple-risk ${item.risk.toLowerCase()}`
                      }
                    >
                      {item.risk}
                    </div>

                  </div>

                ))}

              </div>

            ) : (

              <div className="empty-results">

                <span>〽</span>

                <p>
                  Run a ripple simulation to view
                  predicted downstream delays.
                </p>

              </div>

            )}

          </div>


          {/* RIPPLE GRAPH */}

          <div className="analytics-card ripple-chart-card">

            <h3>Ripple Impact Graph</h3>

            <p className="results-subtitle">
              Predicted delay across affected nodes
            </p>

            {rippleResults.length > 0 ? (

              <div className="ripple-chart">

                {rippleResults.map((item) => {

                  const delay =
                    Number(item.predicted_delay) || 0;

                  const maxDelay =
                    Math.max(
                      ...rippleResults.map(
                        (node) =>
                          Number(node.predicted_delay) || 0
                      ),
                      1
                    );

                  const width =
                    Math.max(
                      (delay / maxDelay) * 100,
                      3
                    );

                  return (

                    <div
                      className="chart-row"
                      key={item.node_id}
                    >

                      <div className="chart-label">
                        {item.node_name}
                      </div>

                      <div className="chart-track">

                        <div
                          className="chart-bar"
                          style={{
                            width: `${width}%`
                          }}
                        />

                      </div>

                      <div className="chart-value">
                        {delay.toFixed(2)}d
                      </div>

                    </div>

                  );

                })}

              </div>

            ) : (

              <div className="empty-results">

                <span>📊</span>

                <p>
                  The ripple graph will appear after
                  simulation.
                </p>

              </div>

            )}

          </div>

        </section>
        {/* ================================== */}
        {/* BOTTOM ANALYTICS */}
        {/* ================================== */}

        <section className="analytics-grid">


          {/* RISK DISTRIBUTION */}

          <div className="analytics-card">

            <h3>Risk Distribution</h3>

            <div className="distribution">

              <div className="donut">
                <div>
                  <strong>
                    {nodes.length}
                  </strong>
                  <span>Nodes</span>
                </div>
              </div>

              <div className="distribution-list">

                <div>
                  <span>
                    <i className="dot low"></i>
                    Low Risk
                  </span>

                  <strong>
                    {Math.round(
                      (riskCounts.low /
                        nodes.length) *
                      100
                    )}%
                  </strong>
                </div>

                <div>
                  <span>
                    <i className="dot medium"></i>
                    Medium Risk
                  </span>

                  <strong>
                    {Math.round(
                      (riskCounts.medium /
                        nodes.length) *
                      100
                    )}%
                  </strong>
                </div>

                <div>
                  <span>
                    <i className="dot high"></i>
                    High Risk
                  </span>

                  <strong>
                    {Math.round(
                      (riskCounts.high /
                        nodes.length) *
                      100
                    )}%
                  </strong>
                </div>
                <div>
                  <span>
                    <i className="dot critical"></i>
                    Critical Risk
                  </span>

                  <strong>
                    {Math.round(
                      (riskCounts.critical /
                        nodes.length) *
                      100
                    )}%
                  </strong>
                </div>

              </div>

            </div>

          </div>


          {/* RECENT ALERTS */}

          <div className="analytics-card">

            <div className="analytics-heading">

              <h3>Recent Alerts</h3>

              <span>View All</span>

            </div>

            <div className="alert-list">

              <div>
                <span className="alert-icon red-bg">
                  !
                </span>

                <p>
                  Delay predicted in Warehouse B
                </p>

                <small>25 min ago</small>
              </div>

              <div>
                <span className="alert-icon yellow-bg">
                  !
                </span>

                <p>
                  Medium risk at Factory B
                </p>

                <small>40 min ago</small>
              </div>

              <div>
                <span className="alert-icon green-bg">
                  ✓
                </span>

                <p>
                  All systems operational
                </p>

                <small>1 hr ago</small>
              </div>

            </div>

          </div>


          {/* SCENARIO HISTORY */}

          <div className="analytics-card">

            <div className="analytics-heading">

              <h3>Scenario History</h3>

              <span>View All</span>

            </div>

            <div className="scenario-history">

              <div>
                <p>Supplier Disruption</p>
                <span className="impact high-impact">
                  High Impact
                </span>
                <small>Today, 11:15 PM</small>
              </div>

              <div>
                <p>Factory B Shutdown</p>
                <span className="impact medium-impact">
                  Medium Impact
                </span>
                <small>Yesterday</small>
              </div>

              <div>
                <p>Warehouse C Delay</p>
                <span className="impact low-impact">
                  Low Impact
                </span>
                <small>30 Aug 2026</small>
              </div>

            </div>

          </div>

        </section>


        <footer className="dashboard-footer">
          AtmoGraph © 2026 · Supply Chain Intelligence Platform
        </footer>

      </main>

    </div>
  );
}

export default App;