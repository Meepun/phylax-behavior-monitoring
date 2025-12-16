const svg = d3.select("svg");
const width = +svg.attr("width");
const height = +svg.attr("height");

const userId = "test_user_1"; // Change this to visualize another user

// Arrow marker
svg.append("defs").append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 -5 10 10")
  .attr("refX", 20)
  .attr("refY", 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-5L10,0L0,5")
  .attr("fill", "#0984e3");

fetch(`/api/session/${userId}/state_diagram`)
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      console.error(data.error);
      return;
    }

    const currentState = data.current_state;
    const nodes = data.states.map(s => ({ id: s, isCurrent: s === currentState }));
    const links = data.transitions.map(t => ({
      source: t.from,
      target: t.to,
      label: t.triggered_by.length ? t.triggered_by.join(", ") : "No action"
    }));

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(200))
      .force("charge", d3.forceManyBody().strength(-600))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(50));

    // Links
    const link = svg.append("g")
      .attr("class", "links")
      .selectAll("path")
      .data(links)
      .join("path")
      .attr("stroke", "#0984e3")
      .attr("stroke-width", 2)
      .attr("fill", "none")
      .attr("marker-end", "url(#arrow)");

    // Link labels
    const linkLabels = svg.append("g")
      .attr("class", "link-labels")
      .selectAll("text")
      .data(links)
      .join("text")
      .attr("font-size", 12)
      .attr("fill", "#2d3436")
      .attr("text-anchor", "middle")
      .attr("dy", -5)
      .text(d => d.label);

    // Nodes
    const node = svg.append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(nodes)
      .join("g")
      .attr("class", "node")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    node.append("circle")
      .attr("r", 30)
      .attr("fill", d => d.isCurrent ? "#fd8233" : "#6c5ce7")
      .attr("stroke", "#2d3436")
      .attr("stroke-width", 2);

    node.append("text")
      .text(d => d.id)
      .attr("fill", "black")
      .attr("font-size", 14)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle");

    simulation.on("tick", () => {
      // Draw curved links
      link.attr("d", d => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy) * 1.5;

        // Self-loop
        if (d.source.id === d.target.id) {
          return `M${d.source.x},${d.source.y} 
                  C${d.source.x - 40},${d.source.y - 40} 
                   ${d.source.x + 40},${d.source.y - 40} 
                   ${d.target.x},${d.target.y}`;
        }

        return `M${d.source.x},${d.source.y} A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
      });

      // Position labels at the middle of link
      linkLabels.attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2 - 10);

      node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  })
  .catch(err => console.error("Error fetching state diagram:", err));
