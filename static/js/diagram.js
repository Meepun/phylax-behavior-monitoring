// -----------------------------
// 2D Automata Diagram using D3.js
// -----------------------------

const STATES = ["NORMAL", "FLAGGED_ONCE", "FLAGGED_TWICE", "LOCKED"];
const WIDTH = 1000;
const HEIGHT = 300;

// Color map for states
const STATE_COLORS = {
  "NORMAL": "green",
  "FLAGGED_ONCE": "yellow",
  "FLAGGED_TWICE": "orange",
  "LOCKED": "red"
};

// Create SVG container
const svg = d3.select("#automata-diagram")
  .attr("width", WIDTH)
  .attr("height", HEIGHT);

// Node positions
const nodeX = STATES.map((d, i) => 150 + i * 200);
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

// Draw nodes (grouped for labels + violations)
const nodes = svg.selectAll("g.node")
  .data(STATES)
  .enter()
  .append("g")
  .attr("class", "node")
  .attr("transform", (d, i) => `translate(${nodeX[i]}, ${nodeY})`);

// Add circles 
nodes.append("circle")
  .attr("r", 60)
  .attr("fill", d => STATE_COLORS[d])
  .attr("stroke", "#333")
  .attr("stroke-width", 2);

// Add multi-line labels
nodes.append("text")
  .attr("text-anchor", "middle")
  .attr("dy", d => d === "FLAGGED_ONCE" || d === "FLAGGED_TWICE" ? -10 : 5)
  .selectAll("tspan")
  .data(d => {
    if (d === "FLAGGED_ONCE") return ["FLAGGED", "ONCE"];
    if (d === "FLAGGED_TWICE") return ["FLAGGED", "TWICE"];
    return [d];
  })
  .enter()
  .append("tspan")
  .attr("x", 0)
  .attr("dy", (d, i) => i === 0 ? 0 : 20)
  .text(d => d)
  .attr("fill", "#fff")
  .attr("font-size", "18px")
  .attr("font-weight", "bold")
  .attr("stroke", "#000")   
  .attr("stroke-width", 3)       
  .attr("paint-order", "stroke"); 
  

// empty text element for violations (will be updated dynamically)
nodes.append("text")
  .attr("class", "violations")
  .attr("text-anchor", "middle")
  .attr("y", 90) // 60 radius + 30 padding below circle
  .selectAll("tspan")
  .data([])  // start empty
  .enter()
  .append("tspan");

// -----------------------------
// Dynamic User ID Handling
// -----------------------------

let USER_ID = document.getElementById("user-id-input").value || "test_user_1";

document.getElementById("update-user-btn").addEventListener("click", () => {
  USER_ID = document.getElementById("user-id-input").value.trim();
  updateState();
});

function formatViolation(violation) {
  return violation
    .split("_")             // split by underscore
    .map(word => word[0].toUpperCase() + word.slice(1)) // capitalize each word
    .join(" ");             // join with spaces
}


// Highlight current state and display violations
function highlightState(state, violations = []) {
  // Highlight the circle
  nodes.selectAll("circle")
    .attr("fill", d => d === state ? STATE_COLORS[state] : "#555");

  // Update state label text
  document.getElementById("state-text").textContent = state;

  // Clear previous violations
  nodes.selectAll("text.violations").selectAll("*").remove();

  // Select the active node
  const activeNode = nodes.filter(d => d === state);

  // Add tspans for each violation
  activeNode.select("text.violations")
    .selectAll("tspan")
    .data(violations)
    .enter()
    .append("tspan")
    .attr("x", 0)          // center horizontally
    .attr("dy", (d, i) => i === 0 ? 0 : 20) // line spacing
    .text(d => formatViolation(d))
    .attr("fill", "#fff")
    .attr("font-size", "14px")
    .attr("font-weight", "bold")
    .attr("stroke", "#000")
    .attr("stroke-width", 2)
    .attr("paint-order", "stroke");
}

// Fetch current state every 2 seconds
async function updateState() {
  try {
    const res = await fetch(`/api/state/${USER_ID}`);
    const data = await res.json();

    highlightState(data.state || "NORMAL", data.violations || []);
    document.getElementById("user-id-text").textContent = USER_ID;
  } catch (err) {
    console.error(err);
  }
}

// Initial update and polling
updateState();
setInterval(updateState, 2000);
