let salesChartInstance = null;

function setValidationMsg(msg) {
  document.getElementById("validationMsg").textContent = msg;
}

async function predictSales() {
  setValidationMsg("");

  const rawInput = document.getElementById("salesInput").value.trim();

  if (!rawInput) {
    setValidationMsg("Please enter at least 3 sales values.");
    return;
  }

  const salesValues = rawInput
    .split(/[\s,]+/)
    .map(v => Number(v))
    .filter(v => !isNaN(v));

  if (salesValues.length < 3) {
    setValidationMsg("Please enter at least 3 valid numeric values.");
    return;
  }

  if (salesValues.some(v => v < 0)) {
    setValidationMsg("Sales values cannot be negative.");
    return;
  }

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ sales: salesValues })
    });

    const result = await response.json();

    if (!response.ok) {
      setValidationMsg(result.error || "Something went wrong.");
      return;
    }

    document.getElementById("meanValue").textContent = result.mean;
    document.getElementById("stdValue").textContent = result.sd;
    document.getElementById("cvValue").textContent = result.cv;
    document.getElementById("trendValue").textContent = result.trend;

    document.getElementById("selectedModel").textContent = result.selected_model;
    document.getElementById("modelReason").textContent = result.model_reason;

    document.getElementById("lrValue").textContent = result.linear_regression;
    document.getElementById("maValue").textContent = result.moving_average;
    document.getElementById("finalPrediction").textContent = result.final_prediction;
    document.getElementById("slopeValue").textContent = result.slope;
    document.getElementById("r2Value").textContent = result.r_squared;
    document.getElementById("ciValue").textContent = `${result.ci_lower} to ${result.ci_upper}`;

    drawChart(salesValues, result.final_prediction);

  } catch (error) {
    setValidationMsg("Could not connect to server. Is Flask running?");
  }
}

function drawChart(actualSales, prediction) {
  const ctx = document.getElementById("salesChart").getContext("2d");

  if (salesChartInstance) {
    salesChartInstance.destroy();
  }

  const labels = actualSales.map((_, i) => `Month ${i + 1}`);
  labels.push(`Month ${actualSales.length + 1}`);

  const chartData = [...actualSales, prediction];

  salesChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Sales",
        data: chartData,
        borderColor: "#38bdf8",
        backgroundColor: "rgba(56, 189, 248, 0.18)",
        fill: true,
        tension: 0.3,
        borderWidth: 3,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: "#f1f5f9"
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: "#f1f5f9"
          },
          grid: {
            color: "rgba(255,255,255,0.08)"
          }
        },
        y: {
          ticks: {
            color: "#f1f5f9"
          },
          grid: {
            color: "rgba(255,255,255,0.08)"
          }
        }
      }
    }
  });
}