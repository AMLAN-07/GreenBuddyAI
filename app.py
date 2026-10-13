from flask import Flask, render_template, request, jsonify
import requests
import csv
import os
from datetime import datetime
from flask import request, jsonify, render_template
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from transformers import pipeline

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:3b"

MISSIONS = [
    "Spend 10 minutes watering your plants.",
    "Observe three different leaves in your garden.",
    "Check whether the soil is dry before watering.",
    "Look for pollinators visiting nearby flowers.",
    "Plant a seed or remove weeds from a garden bed."
]

PLANT_MODEL = "domai-tb/OpenPlants-Identification-ViT-Base-Patch16-224"

plant_classifier = None


def get_plant_classifier():
    global plant_classifier

    if plant_classifier is None:
        plant_classifier = pipeline(
            "image-classification",
            model=PLANT_MODEL,
            device=-1
        )

    return plant_classifier


@app.route("/tasks")
def gardening_tasks():
    return render_template("tasks.html")

@app.route("/")
def home():
    return render_template("index.html", missions=MISSIONS)


@app.route("/api/ask", methods=["POST"])
def ask_gardening_ai():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please enter a gardening question."}), 400

    if len(question) > 1000:
        return jsonify({"error": "Please keep your question under 1000 characters."}), 400

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "stream": False,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are GreenBuddy, a friendly gardening assistant. "
                            "Give practical, beginner-friendly advice. "
                            "Encourage safe outdoor activities. "
                            "When uncertain about a plant or pest, say so."
                        )
                    },
                    {"role": "user", "content": question}
                ]
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        answer = result.get("message", {}).get("content", "")
        if not answer:
            return jsonify({"error": "The AI returned an empty answer."}), 502

        return jsonify({"answer": answer})

    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Ollama is not running. Open Ollama and try again."
        }), 503
    except requests.exceptions.Timeout:
        return jsonify({
            "error": "The AI took too long to respond. Please try again."
        }), 504
    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Could not get a response from the AI model."
        }), 502

@app.route("/api/identify", methods=["POST"])
def identify_plant():
    if "photo" not in request.files:
        return jsonify({"error": "Please upload a plant photo."}), 400

    photo = request.files["photo"]

    if not photo.filename:
        return jsonify({"error": "Choose an image first."}), 400

    # Limit uploaded files to 8 MB.
    image_bytes = photo.stream.read(8 * 1024 * 1024 + 1)

    if len(image_bytes) > 8 * 1024 * 1024:
        return jsonify({"error": "Image must be smaller than 8 MB."}), 413

    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        return jsonify({"error": "Please upload a valid image."}), 400

    try:
        classifier = get_plant_classifier()
        predictions = classifier(image, top_k=3)

        results = [
            {
                "name": item["label"],
                "confidence": round(float(item["score"]) * 100, 1)
            }
            for item in predictions
        ]

        return jsonify({
            "predictions": results,
            "notice": (
                "These are model predictions, not guaranteed "
                "identifications. Check the plant before acting on advice."
            )
        })

    except Exception:
        app.logger.exception("Plant identification failed")
        return jsonify({
            "error": (
                "Plant identification failed. Check your internet "
                "connection for the initial model download and try again."
            )
        }), 503

    
@app.route("/api/care", methods=["POST"])
def plant_care():
    data = request.get_json(silent=True) or {}
    plant = data.get("plant", "").strip()

    if not plant or len(plant) > 150:
        return jsonify({"error": "Please provide a valid plant name."}), 400

    prompt = f"""
    Give beginner-friendly gardening advice for {plant}.
    Include:
    1. Sunlight
    2. Watering
    3. Soil
    4. Common problems
    5. One outdoor activity to do today

    If the plant identification is uncertain, mention that advice
    should be verified before acting on it.
    """

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "stream": False,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are GreenBuddy, a practical gardening assistant."
                    },
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        return jsonify({
            "plant": plant,
            "advice": result["message"]["content"]
        })

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Could not contact Ollama. Check that it is running."
        }), 503


@app.route("/api/plan", methods=["POST"])
def planting_plan():
    data = request.get_json(silent=True) or {}

    location = data.get("location", "Bhubaneswar, Odisha").strip()
    season = data.get("season", "October–November").strip()
    space = data.get("space", "Balcony pots").strip()

    if not location or len(location) > 100:
        return jsonify({"error": "Enter a valid city or region."}), 400

    allowed_seasons = {
        "October–November",
        "December–January",
        "February–March",
        "April–June",
        "July–September"
    }

    allowed_spaces = {
        "Balcony pots",
        "Backyard garden",
        "Indoor containers",
        "Community garden"
    }

    if season not in allowed_seasons or space not in allowed_spaces:
        return jsonify({"error": "Choose a valid season and garden type."}), 400

    prompt = f"""
    You are GreenBuddy, a careful gardening assistant.

    Create a practical planting plan for:
    Location: {location}
    Planning period: {season}
    Growing space: {space}

    Important rules:
    - Consider the local climate instead of assuming a temperate climate.
    - For Bhubaneswar, Odisha, account for warm conditions, seasonal
        rainfall, humidity, and the possibility of heavy rain.
    - Do not claim to have checked live weather or official planting calendars.
    - Treat planting suggestions as candidates, not guaranteed recommendations.
    - Do not claim tomatoes or cucumbers tolerate frost-free or cool conditions
        without explaining their temperature needs.
    - Recommend direct sowing or transplanting only when appropriate.
    - Never prescribe watering on a fixed weekly schedule for every garden.
        Explain how to check soil moisture and adjust for rainfall and containers.
    - Avoid unnecessary deep tilling.
    - Do not invent exact local temperatures, rainfall, or germination results.

    Include:
    1. Three potentially suitable vegetables or herbs, with reasons.
    2. Sunlight and soil guidance.
    3. Watering guidance based on soil moisture.
    4. Three practical outdoor tasks for this week.
    5. One inexpensive beginner gardening project.
    6. A short note about checking local growing conditions.

    Use clear headings and short bullet points.
    Keep the advice beginner-friendly and actionable.
    """
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "stream": False,
                "messages": [
                    {
                        "role": "system",
                        "content": "You provide cautious, practical gardening guidance."
                    },
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        return jsonify({"plan": result["message"]["content"]})

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Could not contact Ollama. Make sure it is running."
        }), 503

@app.route("/feedback")
def feedback_page():
    return render_template("feedback.html")


@app.route("/api/feedback", methods=["POST"])
def save_feedback():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "task",
        "ease",
        "usefulness",
        "would_use",
        "comments",
    ]

    if any(not str(data.get(field, "")).strip()
           for field in required_fields):
        return jsonify({
            "success": False,
            "message": "Please complete all required fields."
        }), 400

    allowed_tasks = {
        "Plant identification",
        "Plant care advice",
        "Planting planner",
        "Outdoor missions",
    }
    allowed_ratings = {"1", "2", "3", "4", "5"}
    allowed_use = {
        "Yes",
        "Maybe",
        "No",
    }

    if data["task"] not in allowed_tasks:
        return jsonify({"success": False,
                        "message": "Invalid task."}), 400

    if str(data["ease"]) not in allowed_ratings:
        return jsonify({"success": False,
                        "message": "Invalid ease rating."}), 400

    if str(data["usefulness"]) not in allowed_ratings:
        return jsonify({"success": False,
                        "message": "Invalid usefulness rating."}), 400

    if data["would_use"] not in allowed_use:
        return jsonify({"success": False,
                        "message": "Invalid answer."}), 400

    comments = str(data["comments"]).strip()

    if len(comments) > 2000:
        return jsonify({"success": False,
                        "message": "Comments must be under 2000 characters."}), 400

    feedback_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "user_feedback.csv"
    )

    file_exists = os.path.exists(feedback_file)

    with open(feedback_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "task",
                "ease",
                "usefulness",
                "would_use",
                "comments",
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "task": data["task"],
            "ease": data["ease"],
            "usefulness": data["usefulness"],
            "would_use": data["would_use"],
            "comments": comments,
        })

    return jsonify({
        "success": True,
        "message": "Thank you! Your feedback has been saved."
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)