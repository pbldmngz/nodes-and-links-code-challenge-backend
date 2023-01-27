from flask import Flask, jsonify, request
from flask_cors import CORS

from utils.format_nodes import format_nodes
import csv
import io
import json


app = Flask(__name__)
CORS(app)


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")

    input_files = []
    for file in files:
        if file and file.filename.endswith(".csv"):
            data = []
            stream = io.StringIO(
                file.stream.read().decode("UTF8"), newline=None
            )
            reader = csv.reader(stream)
            for row in reader:
                data.append(row)
            input_files.append(data)

    adjacency_matrix, date_matrix = input_files

    # try:
    formatted_nodes = format_nodes(adjacency_matrix, date_matrix[1:])

    with open("ultra_minimal_database.json", "w") as file:
        file.write(json.dumps(formatted_nodes))

    return jsonify({"message": "Successfully uploaded!"}), 200
    # except Exception:
    #     return jsonify({"message": "Failed to upload!"}), 418


@app.route("/download", methods=["GET"])
def download():
    try:
        with open("ultra_minimal_database.json", "r") as file:
            data = file.read()
            return jsonify(data), 200
    except Exception:
        return jsonify({"message": "Failed to download!"}), 404


if __name__ == "__main__":
    app.run()
