const socket = io();

function sendMessage() {
    const msg = document.getElementById("messageInput").value;
    if (!msg) return;

    // Add to chat log immediately
    const chatLog = document.getElementById("chat-log");
    const div = document.createElement("div");
    div.classList.add("message");
    div.textContent = `You: ${msg}`;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;

    socket.emit("send_action", { action: msg });
    document.getElementById("messageInput").value = "";
}

// Receive log messages from server sumtn idk
socket.on("log", (data) => {
    const chatLog = document.getElementById("chat-log");
    const div = document.createElement("div");
    div.classList.add("message");
    div.textContent = data.text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
});

// Receive FSM data and render
socket.on("diagram", (auto) => {
    renderFSM(auto.states, auto.transitions, auto.current);
});

// D3.js rendering
function renderFSM(states, transitions, currentState) {
    d3.select("#diagram").selectAll("*").remove();
    const width = document.getElementById("diagram").clientWidth;
    const height = document.getElementById("diagram").clientHeight;

    const svg = d3.select("#diagram").append("svg")
                  .attr("width", width)
                  .attr("height", height);

    const nodes = states.map((s, i) => ({ id: s, x: 100 + i*150, y: height/2 }));
    const links = transitions.map(t => ({
        source: t.from,
        target: t.to,
        label: t.label
    }));

    // Draw links
    svg.selectAll("line")
       .data(links)
       .enter()
       .append("line")
       .attr("x1", d => nodes.find(n => n.id === d.source).x)
       .attr("y1", d => nodes.find(n => n.id === d.source).y)
       .attr("x2", d => nodes.find(n => n.id === d.target).x)
       .attr("y2", d => nodes.find(n => n.id === d.target).y)
       .attr("stroke", "white")
       .attr("stroke-width", 2)
       .attr("marker-end", "url(#arrow)");

    // Arrowhead
    svg.append("defs").append("marker")
       .attr("id", "arrow")
       .attr("viewBox", "0 0 10 10")
       .attr("refX", 10)
       .attr("refY", 5)
       .attr("markerWidth", 6)
       .attr("markerHeight", 6)
       .attr("orient", "auto-start-reverse")
       .append("path")
       .attr("d", "M0,0 L10,5 L0,10 z")
       .attr("fill", "white");

    // Draw nodes
    svg.selectAll("circle")
       .data(nodes)
       .enter()
       .append("circle")
       .attr("cx", d => d.x)
       .attr("cy", d => d.y)
       .attr("r", 25)
       .attr("fill", d => d.id === currentState ? "red" : "steelblue");

    // Node labels
    svg.selectAll("text")
       .data(nodes)
       .enter()
       .append("text")
       .text(d => d.id)
       .attr("x", d => d.x)
       .attr("y", d => d.y + 5)
       .attr("text-anchor", "middle")
       .attr("fill", "white")
       .attr("font-size", "14px");
}
