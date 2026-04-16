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

    return round(slope, 2), round(intercept, 2), round(prediction, 2), round(r_squared, 4)


def moving_average(data, k=3):
    k = min(k, len(data))
    return round(sum(data[-k:]) / k, 2)


def detect_trend(slope):
    if slope > 0:
        return "Increasing"
    elif slope < 0:
        return "Decreasing"
    return "Stable"


def select_model(cv):
    if cv > 1:
        return "Moving Average", "CV > 1, so Moving Average is selected."
    else:
        return "Linear Regression", "CV < 1, so Linear Regression is selected."


def confidence_interval(data, prediction, z=1.645):
    mean = calculate_mean(data)
    sd = calculate_sd(data, mean)
    margin = z * sd
    return round(prediction - margin, 2), round(prediction + margin, 2)


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
            except:
                return jsonify({"error": "All sales values must be numeric."}), 400

        mean = round(calculate_mean(clean_sales), 2)
        sd = round(calculate_sd(clean_sales, mean), 2)
        cv = round(calculate_cv(clean_sales), 4)

        slope, intercept, lr_prediction, r_squared = calculate_linear_regression(clean_sales)
        ma_prediction = moving_average(clean_sales, 3)

        selected_model, model_reason = select_model(cv)

        final_prediction = lr_prediction if selected_model == "Linear Regression" else ma_prediction
        trend = detect_trend(slope)
        ci_lower, ci_upper = confidence_interval(clean_sales, final_prediction)

        return jsonify({
            "mean": mean,
            "sd": sd,
            "cv": cv,
            "trend": trend,
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
            "linear_regression": lr_prediction,
            "moving_average": ma_prediction,
            "selected_model": selected_model,
            "model_reason": model_reason,
            "final_prediction": final_prediction,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)