let chart = null;

function filtrar() {
    const params = new URLSearchParams({
        equipo: document.getElementById("equipo").value,
        metrica: document.getElementById("metrica").value,
        parte: document.getElementById("parte").value,
        local: document.getElementById("local").value,
        condicion: document.getElementById("condicion").value,
        valor: document.getElementById("valor").value
    });

    fetch("/filtrar?" + params.toString())
        .then(r => r.json())
        .then(data => {
            const fechas = data.resultados.map(r => r.fecha + " vs " + r.vs);
            const valores = data.resultados.map(r => r.valor);
            const colores = data.resultados.map(r => r.cumple ? "green" : "red");

            document.getElementById("porcentaje").innerText =
                "Cumplimiento: " + data.porcentaje + "%";

            if (chart) chart.destroy();

            chart = new Chart(document.getElementById("grafico"), {
                type: "bar",
                data: {
                    labels: fechas,
                    datasets: [{
                        label: "Valor",
                        data: valores,
                        backgroundColor: colores
                    }]
                }
            });
        });
}
