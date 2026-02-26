let chart = null;

function filtrar() {
    const params = new URLSearchParams({
        equipo: document.getElementById("equipo").value,
        metrica: document.getElementById("metrica").value,
        parte: document.getElementById("parte").value,
        local: document.getElementById("local").value,
        condicion: document.getElementById("condicion").value,
        valor: document.getElementById("valor").value || ""
    });

    fetch("/filtrar?" + params.toString())
        .then(r => r.json())
        .then(data => {
            const fechas = data.resultados.map(r => r.fecha + " vs " + r.vs);
            const valores = data.resultados.map(r => r.valor);
            let colores;
            if (data.porcentaje === null) {
                // sin filtro → barras azules
                colores = data.resultados.map(_ => "steelblue");
            } else {
                // con filtro → verde/rojo
                colores = data.resultados.map(r => r.cumple ? "green" : "red");
            }

            if (data.porcentaje === null) {
                document.getElementById("porcentaje").innerText = "";
            } else {
                document.getElementById("porcentaje").innerText = "Cumplimiento: " + data.porcentaje + "%";
            }

            if (chart) chart.destroy();

            chart = new Chart(document.getElementById("grafico"), {
                type: "bar",
                plugins: [ChartDataLabels],
                data: {
                    labels: fechas,
                    datasets: [{
                        label: "Valor",
                        data: valores,
                        backgroundColor: colores
                    }]
                },
                options: {
                    plugins: { 
                        legend: { 
                            display: false
                        }, 
                        datalabels: { 
                            anchor: 'start', 
                            align: 'start', 
                            offset: 6,
                            color: '#000', 
                            font: { 
                                weight: 'bold', 
                                size: 14 
                            }, 
                            formatter: (value) => value 
                        } 
                    },
                    
                    scales: { 
                        y: { 
                            ticks: { 
                                precision: 0, // 🔥 fuerza a usar solo enteros 
                                callback: function(value) { 
                                    return Number.isInteger(value) ? value : null; 
                                } 
                            } 
                        } 
                    } 
                }
            });
        });
}









