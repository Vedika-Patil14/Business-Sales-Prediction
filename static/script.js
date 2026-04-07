let salesChartInstance = null;

async function predictSales() {
  const salesInput = document.getElementById("salesInput").value.trim();

  if (!salesInput) {
    alert("Please enter sales values.");
    return;
  }

  const salesValues = salesInput
    .split(/[\s,]+/)
    .map(value => Number(value))
    .filter(value => !isNaN(value));

  if (salesValues.length < 3) {
    alert("Please enter at least 3 valid sales values.");
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
      alert(result.error || "Something went wrong");
      return;
    }

    document.getElementById("meanValue").textContent = result.mean;
    document.getElementById("stdValue").textContent = result.sd;
    document.getElementById("cvValue").textContent = result.cv;
    document.getElementById("modelValue").textContent = result.selected_model;

    document.getElementById("predictionDetails").innerHTML = `
      <p><strong>Linear Regression Prediction:</strong> ${result.linear_regression}</p>
      <p><strong>Moving Average Prediction:</strong> ${result.moving_average}</p>
      <p><strong>Final Selected Model:</strong> ${result.selected_model}</p>
      <p><strong>Predicted Next Month Sales:</strong> ${result.final_prediction}</p>
    `;

    drawChart(salesValues, result.final_prediction);
  } catch (error) {
    console.error("Error:", error);
    alert("Error connecting to server.");
  }
}

function drawChart(values, prediction) {
  const canvas = document.getElementById("salesChart");
  const ctx = canvas.getContext("2d");

  const labels = values.map((_, index) => `Month ${index + 1}`);
  labels.push("Next Month");

  const actualData = [...values, null];
  const predictionData = new Array(values.length).fill(null);
  predictionData.push(prediction);

  if (salesChartInstance) {
    salesChartInstance.destroy();
  }

  salesChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Actual Sales",
          data: actualData,
          borderColor: "#38bdf8",
          backgroundColor: "rgba(56, 189, 248, 0.2)",
          borderWidth: 3,
          tension: 0.35,
          fill: false,
          pointRadius: 5,
          pointHoverRadius: 7
        },
        {
          label: "Next Month Prediction",
          data: predictionData,
          borderColor: "#f59e0b",
          backgroundColor: "rgba(245, 158, 11, 0.2)",
          borderWidth: 3,
          borderDash: [6, 6],
          tension: 0.35,
          fill: false,
          pointRadius: 6,
          pointHoverRadius: 8
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: "#1f2937",
            font: {
              size: 13,
              weight: "bold"
            }
          }
        },
        tooltip: {
          backgroundColor: "#0f172a",
          titleColor: "#ffffff",
          bodyColor: "#ffffff"
        }
      },
      scales: {
        x: {
          ticks: {
            color: "#374151",
            font: {
              size: 12
            }
          },
          grid: {
            color: "rgba(0,0,0,0.06)"
          }
        },
        y: {
          ticks: {
            color: "#374151",
            font: {
              size: 12
            }
          },
          grid: {
            color: "rgba(0,0,0,0.06)"
          },
          beginAtZero: false
        }
      }
    }
  });
}