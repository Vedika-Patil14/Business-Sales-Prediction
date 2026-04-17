from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)


def calculate_mean(data):
    return sum(data) / len(data)


def calculate_sd(data, mean):
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return math.sqrt(variance)


def calculate_cv(data):
    mean = calculate_mean(data)
    sd = calculate_sd(data, mean)
    if mean == 0:
        return 0.0
    return sd / mean


def calculate_linear_regression(data):
    n = len(data)
    x = list(range(1, n + 1))

    sum_x = sum(x)
    sum_y = sum(data)
    sum_xy = sum(x[i] * data[i] for i in range(n))
    sum_x2 = sum(i * i for i in x)

    denominator = n * sum_x2 - (sum_x ** 2)

    if denominator == 0:
        slope = 0
        intercept = data[-1]
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

    next_x = n + 1
    prediction = slope * next_x + intercept

    mean_y = sum_y / n
    predicted_y = [slope * xi + intercept for xi in x]
    ss_total = sum((yi - mean_y) ** 2 for yi in data)
    ss_res = sum((data[i] - predicted_y[i]) ** 2 for i in range(n))

    if ss_total == 0:
        r_squared = 1.0
    else:
        r_squared = 1 - (ss_res / ss_total)

    return slope, intercept, prediction, r_squared


def moving_average(data, k=3):
    k = min(k, len(data))
    return sum(data[-k:]) / k


def detect_trend(slope, threshold=0.01):
    if slope > threshold:
        return "Increasing"
    elif slope < -threshold:
        return "Decreasing"
    return "Stable"


def select_model(slope, r_squared, cv):
    """
    Improved decision logic:
    1. If trend is clear and R² is good -> Linear Regression
    2. If fluctuation is high -> Moving Average
    3. Otherwise -> Moving Average
    """
    if abs(slope) > 0.01 and r_squared >= 0.7:
        return (
            "Linear Regression",
            "Clear trend detected and R² is high, so Linear Regression is selected."
        )
    elif cv > 0.1:
        return (
            "Moving Average",
            "Data is fluctuating (CV > 0.1) and trend is not reliable, so Moving Average is selected."
        )
    else:
        return (
            "Moving Average",
            "No strong trend detected, so Moving Average is selected."
        )


def confidence_interval(data, prediction, z=1.645):
    mean = calculate_mean(data)
    sd = calculate_sd(data, mean)
    margin = z * sd
    return prediction - margin, prediction + margin


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict-page")
def predict_page():
    return render_template("predict.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json()

        if not payload or "sales" not in payload:
            return jsonify({"error": "Sales data is required."}), 400

        sales = payload["sales"]

        if not isinstance(sales, list):
            return jsonify({"error": "Sales must be a list."}), 400

        if len(sales) < 3:
            return jsonify({"error": "Please enter at least 3 sales values."}), 400

        clean_sales = []
        for value in sales:
            try:
                num = float(value)
                if num < 0:
                    return jsonify({"error": "Sales values cannot be negative."}), 400
                clean_sales.append(num)
            except ValueError:
                return jsonify({"error": "All sales values must be numeric."}), 400

        mean_raw = calculate_mean(clean_sales)
        sd_raw = calculate_sd(clean_sales, mean_raw)
        cv_raw = calculate_cv(clean_sales)

        slope_raw, intercept_raw, lr_prediction_raw, r_squared_raw = calculate_linear_regression(clean_sales)
        ma_prediction_raw = moving_average(clean_sales, 3)

        selected_model, model_reason = select_model(slope_raw, r_squared_raw, cv_raw)

        final_prediction_raw = (
            lr_prediction_raw if selected_model == "Linear Regression" else ma_prediction_raw
        )

        trend = detect_trend(slope_raw)
        ci_lower_raw, ci_upper_raw = confidence_interval(clean_sales, final_prediction_raw)

        return jsonify({
            "mean": round(mean_raw, 2),
            "sd": round(sd_raw, 2),
            "cv": round(cv_raw, 4),
            "trend": trend,
            "slope": round(slope_raw, 2),
            "intercept": round(intercept_raw, 2),
            "r_squared": round(r_squared_raw, 4),
            "linear_regression": round(lr_prediction_raw, 2),
            "moving_average": round(ma_prediction_raw, 2),
            "selected_model": selected_model,
            "model_reason": model_reason,
            "final_prediction": round(final_prediction_raw, 2),
            "ci_lower": round(ci_lower_raw, 2),
            "ci_upper": round(ci_upper_raw, 2)
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)