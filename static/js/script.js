const socket = io();

function sendAction() {
    const action = document.getElementById("actionInput").value;
    if (!action) return;
    socket.emit("send_action", { action });
    document.getElementById("actionInput").value = "";
}

socket.on("log", (data) => {
    const term = document.getElementById("terminal");
    term.textContent += data.text + "\n";
    term.scrollTop = term.scrollHeight;
});

socket.on("diagram", (auto) => {
    let graph = "stateDiagram-v2\n";

    auto.transitions.forEach(t => {
        graph += `${t.from} --> ${t.to}: ${t.label}\n`;
    });

    graph += `\nstate ${auto.current}`;

    document.getElementById("diagram").innerHTML =
        `<div class="mermaid">${graph}</div>`;

    mermaid.init();
});
