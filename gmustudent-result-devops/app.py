import os
import sqlite3
from flask import Flask, request, redirect, url_for, render_template_string
import logging

app = Flask(__name__)

# Configure application logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

# HTML page displayed in the browser.
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Result Management System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 40px auto;
            padding: 20px;
            background: #f4f6f8;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
        }
        input, button {
            display: block;
            width: 100%;
            box-sizing: border-box;
            padding: 10px;
            margin: 10px 0;
        }
        button {
            background: #1769aa;
            color: white;
            border: none;
            cursor: pointer;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #eef5ff;
        }
        .error {
            color: #b00020;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Student Result Management</h1>
        <p>Enter marks for three subjects (0 to 100 each).</p>

        <form method="POST" action="/">
            <label>Student name</label>
            <input
                type="text"
                name="name"
                maxlength="80"
                required
                value="{{ name }}"
            >

            <label>Subject 1 marks</label>
            <input type="number" name="m1" min="0" max="100"
                   required value="{{ marks[0] }}">

            <label>Subject 2 marks</label>
            <input type="number" name="m2" min="0" max="100"
                   required value="{{ marks[1] }}">

            <label>Subject 3 marks</label>
            <input type="number" name="m3" min="0" max="100"
                   required value="{{ marks[2] }}">

            <button type="submit">Calculate Result</button>
        </form>

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        {% if result %}
            <div class="result">
                <h2>Student Result</h2>
                <p>Name: {{ result.name }}</p>
                <p>Total: {{ result.total }} / 300</p>
                <p>Percentage: {{ "%.2f"|format(result.percentage) }}%</p>
                <p>Status: <strong>{{ result.status }}</strong></p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""


def calculate_result(name, marks):
    """Calculate a student's total, percentage, and result status."""

    cleaned_name = name.strip()

    if not cleaned_name:
        raise ValueError("Student name is required.")

    if len(cleaned_name) > 80:
        raise ValueError("Student name must be 80 characters or fewer.")

    if len(marks) != 3:
        raise ValueError("Exactly three subject marks are required.")

    validated_marks = []

    for mark in marks:
        if isinstance(mark, bool) or not isinstance(mark, int):
            raise ValueError("Marks must be whole numbers.")

        if mark < 0 or mark > 100:
            raise ValueError("Each subject mark must be between 0 and 100.")

        validated_marks.append(mark)

    total = sum(validated_marks)
    percentage = (total / 300) * 100

    # Passing rule for this teaching example:
    # at least 35 marks in every subject.
    status = (
        "PASS" if all(mark >= 35 for mark in validated_marks)
        else "FAIL"
    )

    return {
        "name": cleaned_name,
        "total": total,
        "percentage": percentage,
        "status": status,
    }


@app.route("/", methods=["GET", "POST"])
def home():
    """Display the form and process submitted marks."""

    name = ""
    marks = ["", "", ""]
    result = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        marks = [
            request.form.get("m1", ""),
            request.form.get("m2", ""),
            request.form.get("m3", ""),
        ]

        try:
            parsed_marks = []

            for mark in marks:
                # Reject decimals and empty values.
                if not mark.isdigit():
                    raise ValueError(
                        "Enter whole-number marks between 0 and 100."
                    )

                parsed_marks.append(int(mark))

            result = calculate_result(name, parsed_marks)

            logger.info(
                "Result calculated successfully for a student."
            )

        except ValueError as exc:
            error = str(exc)
            logger.warning("Invalid result form submission.")

    return render_template_string(
        HTML_PAGE,
        name=name,
        marks=marks,
        result=result,
        error=error,
    )


@app.route("/health", methods=["GET"])
def health():
    """Basic health endpoint for monitoring."""

    return {"status": "healthy"}, 200


if __name__ == "__main__":
    # Use 0.0.0.0 inside Docker so the container port is accessible.
    port = int(os.environ.get("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
