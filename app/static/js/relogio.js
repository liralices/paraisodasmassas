function atualizarRelogio() {
    const agora = new Date();
    const data = agora.toLocaleDateString("pt-BR", {
        weekday: "long",
        day: "2-digit",
        month: "long",
        year: "numeric",
    });
    const hora = agora.toLocaleTimeString("pt-BR");

    const elData = document.getElementById("relogio-data");
    const elHora = document.getElementById("relogio-hora");
    if (elData) elData.textContent = data.charAt(0).toUpperCase() + data.slice(1);
    if (elHora) elHora.textContent = hora;
}

atualizarRelogio();
setInterval(atualizarRelogio, 1000);
