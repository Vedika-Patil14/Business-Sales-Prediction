from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)


def calculate_mean(data):
    return sum(data) / len(data)


def calculate_sd(data, mean):
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return math.sqrt(variance)


def moving_average(data, k=3):
    k = min(k, len(data))
    recent = data[-k:]
    return sum(recent) / len(recent)


def linear_regression_prediction(data):
    n = len(data)
    x = list(range(1, n + 1))

    sum_x = sum(x)
    sum_y = sum(data)
    sum_xy = sum(x[i] * data[i] for i in range(n))
    sum_x2 = sum(i * i for i in x)

    denominator = (n * sum_x2 - sum_x ** 2)

    if denominator == 0:
        return data[-1]

    m = (n * sum_xy - sum_x * sum_y) / denominator
    c = (sum_y - m * sum_x) / n

    next_x = n + 1
    prediction = m * next_x + c
    return prediction


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict-page")
def predict_page():
    return render_template("predict.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data or "sales" not in data:
            return jsonify({"error": "No sales data received"}), 400

        sales = data.get("sales", [])

        if not isinstance(sales, list) or len(sales) < 3:
            return jsonify({"error": "Enter at least 3 sales values"}), 400

        sales = [float(x) for x in sales]

        mean = calculate_mean(sales)
        sd = calculate_sd(sales, mean)
        cv = sd / mean if mean != 0 else 0

        lr_prediction = linear_regression_prediction(sales)
        ma_prediction = moving_average(sales, 3)

        if cv < 0.1:
            model = "Linear Regression"
            final_prediction = lr_prediction
        else:
            model = "Moving Average"
            final_prediction = ma_prediction

        return jsonify({
            "mean": round(mean, 2),
            "sd": round(sd, 2),
            "cv": round(cv, 4),
            "linear_regression": round(lr_prediction, 2),
            "moving_average": round(ma_prediction, 2),
            "selected_model": model,
            "final_prediction": round(final_prediction, 2)
        })

    except ValueError:
        return jsonify({"error": "Please enter only numeric sales values"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)