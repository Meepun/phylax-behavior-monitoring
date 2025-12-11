const socket = io();

// Send chat message
function sendMessage() {
    const msg = document.getElementById("messageInput").value;
    if (!msg) return;

    // Add to chat log
    const chatLog = document.getElementById("chat-log");
    const div = document.createElement("div");
    div.classList.add("message");
    div.textContent = `You: ${msg}`;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;

    socket.emit("send_action", { action: msg });
    document.getElementById("messageInput").value = "";
}

// Chat log from server (other users or system messages)
socket.on("chat", (data) => {
    const chatLog = document.getElementById("chat-log");
    const div = document.createElement("div");
    div.classList.add("message");
    div.textContent = data.text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
});

// Behavior log + FSM updates idk bruh
socket.on("behavior_update", (data) => {
    // Update behavior log under diagram
    const log = document.getElementById("behavior-log");
    log.textContent += `Action: ${data.action} | State: ${data.state} | Behavior: ${data.behavior}\n`;
    log.scrollTop = log.scrollHeight;

    // Update FSM diagram
    renderFSM(data.states, data.transitions, data.state);
});

// ----------------- D3.js FSM rendering ----------------- ewan ko
function renderFSM(states, transitions, currentState) {
    d3.select("#diagram").selectAll("*").remove();
    const width = document.getElementById("diagram").clientWidth;
    const height = document.getElementById("diagram").clientHeight;

    const svg = d3.select("#diagram")
                  .append("svg")
                  .attr("width", width)
                  .attr("height", height);

    const nodes = states.map(s => ({ id: s }));
    const links = transitions.map(t => ({ source: t.from, target: t.to, label: t.label }));

    // Arrowhead for links
    svg.append("defs").append("marker")
       .attr("id", "arrow")
       .attr("viewBox", "0 0 10 10")
       .attr("refX", 10)
       .attr("refY", 5)
       .attr("markerWidth", 6)
       .attr("markerHeight", 6)
       .attr("orient", "auto")
       .append("path")
       .attr("d", "M0,0 L10,5 L0,10 Z")
       .attr("fill", "white");

    const simulation = d3.forceSimulation(nodes)
                         .force("link", d3.forceLink(links).id(d => d.id).distance(150))
                         .force("charge", d3.forceManyBody().strength(-500))
                         .force("center", d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = svg.selectAll("line")
                    .data(links)
                    .enter()
                    .append("line")
                    .attr("stroke", "white")
                    .attr("stroke-width", 2)
                    .attr("marker-end", "url(#arrow)");

    // Draw nodes
    const node = svg.selectAll("circle")
                    .data(nodes)
                    .enter()
                    .append("circle")
                    .attr("r", 25)
                    .attr("fill", d => d.id === currentState ? "red" : "steelblue")
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));

    // Node labels
    const labels = svg.selectAll("text")
                      .data(nodes)
                      .enter()
                      .append("text")
                      .text(d => d.id)
                      .attr("fill", "white")
                      .attr("text-anchor", "middle")
                      .attr("dy", 5)
                      .attr("pointer-events", "none");

    // Tick simulation
    simulation.on("tick", () => {
        link.attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("cx", d => d.x)
            .attr("cy", d => d.y);

        labels.attr("x", d => d.x)
              .attr("y", d => d.y);
    });

    // Drag functions
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
}
