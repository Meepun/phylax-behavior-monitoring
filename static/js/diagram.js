// -----------------------------
// 2D Automata Diagram using D3.js
// -----------------------------
const urlParams = new URLSearchParams(window.location.search);
const USER_ID = urlParams.get("user_id") || "test_user_1"; // dynamic user ID

const STATES = ["NORMAL", "FLAGGED_ONCE", "FLAGGED_TWICE", "LOCKED"];
const WIDTH = 800;
const HEIGHT = 200;

// Create SVG container
const svg = d3.select("#automata-diagram")
  .attr("width", WIDTH)
  .attr("height", HEIGHT);

// Node positions
const nodeX = STATES.map((d, i) => 100 + i * 150);
const nodeY = HEIGHT / 2;

// Arrow marker
svg.append("defs").append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 -5 10 10")
  .attr("refX", 10)
  .attr("refY", 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-5L10,0L0,5")
  .attr("fill", "#aaa");

// Draw edges
for (let i = 0; i < STATES.length - 1; i++) {
  svg.append("line")
    .attr("x1", nodeX[i])
    .attr("y1", nodeY)
    .attr("x2", nodeX[i + 1])
    .attr("y2", nodeY)
    .attr("stroke", "#aaa")
    .attr("stroke-width", 2)
    .attr("marker-end", "url(#arrow)");
}

// Draw nodes
const nodes = svg.selectAll("circle")
  .data(STATES)
  .enter()
  .append("circle")
  .attr("cx", (d, i) => nodeX[i])
  .attr("cy", nodeY)
  .attr("r", 40) // larger circles
  .attr("fill", "#555");

// Add labels
svg.selectAll("text")
  .data(STATES)
  .enter()
  .append("text")
  .attr("x", (d, i) => nodeX[i])
  .attr("y", nodeY + 5)
  .attr("text-anchor", "middle")
  .attr("fill", "#fff")
  .text(d => d);

// Highlight current state
function highlightState(state) {
  nodes.attr("fill", d => d === state ? "#ff0000" : "#555");
  document.getElementById("state-text").textContent = state;
}

// Fetch current state every 2 seconds
async function updateState() {
  try {
    const res = await fetch(`/api/state/${USER_ID}`);
    const data = await res.json();

    highlightState(data.state || "NORMAL");
    document.getElementById("score-text").textContent = data.score || 0;
    
    // Show which user ID is being fetched
    document.getElementById("user-id-text").textContent = USER_ID;
  } catch (err) {
    console.error(err);
  }
}

// Initial update and polling
updateState();
setInterval(updateState, 2000);
