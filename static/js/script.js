const socket = io();   

function sendMessage() {
    const msg = document.getElementById("messageInput").value;
    if (!msg) return;

    const chatLog = document.getElementById("chat-log");
    const div = document.createElement("div");
    div.classList.add("message");
    div.textContent = `You: ${msg}`;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;

    socket.emit("send_action", { action: msg });
    document.getElementById("messageInput").value = "";
}

socket.on("chat", (data) => {
    const chatLog = document.getElementById("chat-log");
    const div = document.createElement("div");
    div.classList.add("message");
    div.textContent = data.text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
});

// eto ung logs saa baba nung diagram
socket.on("behavior_update", (data) => {
    const log = document.getElementById("behavior-log");
    
    const entry = document.createElement("div");
    entry.textContent = `Action: ${data.action} | State: ${data.state} | Behavior: ${data.behavior}`;
    
    if (data.behavior === "normal") entry.style.color = "lime";
    else if (data.behavior === "suspicious") entry.style.color = "orange";
    else if (data.behavior === "malicious") entry.style.color = "red";
    
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;

    renderFSM(data.states, data.transitions, data.state);
});

// idk kung ano ginagawa ko basta ewan asdfghjkl
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

    const link = svg.selectAll("line")
                    .data(links)
                    .enter()
                    .append("line")
                    .attr("stroke", "white")
                    .attr("stroke-width", 2)
                    .attr("marker-end", "url(#arrow)");

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

    const labels = svg.selectAll("text")
                      .data(nodes)
                      .enter()
                      .append("text")
                      .text(d => d.id)
                      .attr("fill", "white")
                      .attr("text-anchor", "middle")
                      .attr("dy", 5)
                      .attr("pointer-events", "none");

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

// experiment4