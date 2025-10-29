from flask import Flask, render_template, request, redirect, url_for
import os
from src.analyze_core import analyze_json_data

app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates"
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
STATIC_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "../static/images")
OUTPUT_CSV_PATH = os.path.join(os.path.dirname(__file__), "../outputs/question_analysis.csv")


@app.route("/")
def index():
    """Landing page: allows user to upload JSON files."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Handle uploaded JSON files and trigger analysis."""
    uploaded_files = request.files.getlist("json_files")

    if not uploaded_files:
        return "No files uploaded!", 400

    # Ensure directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(STATIC_IMAGE_DIR, exist_ok=True)

    # Save uploaded files into /data
    for file in uploaded_files:
        file.save(os.path.join(DATA_DIR, file.filename))

    # Perform analysis
    result = analyze_json_data(DATA_DIR, STATIC_IMAGE_DIR, OUTPUT_CSV_PATH)

    return render_template("report.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)

