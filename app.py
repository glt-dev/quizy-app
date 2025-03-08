from flask import Flask, render_template, request, redirect, url_for
import json
from agent import ask_openai_agent

app = Flask(__name__)

# Load or create progress JSON file
JSON_FILE = "progress.json"
try:
    with open(JSON_FILE, "r") as f:
        progress = json.load(f)
except FileNotFoundError:
    progress = {"players": {}}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        player_name = request.form["player_name"].strip()
        difficulty = request.form["difficulty"]

        if player_name not in progress["players"]:
            progress["players"][player_name] = {"score": 0}

        return redirect(url_for("quiz", player_name=player_name, difficulty=difficulty))

    return render_template("index.html")

@app.route("/quiz/<player_name>", methods=["GET", "POST"])
def quiz(player_name):
    message = ""
    points = progress["players"][player_name]["score"]
    difficulty = request.args.get("difficulty", "Facile")

    # Handle answer submission
    if request.method == "POST" and "answer" in request.form:
        user_answer = request.form.get("answer")
        correct_answer = request.form.get("correct_answer")

        # Difficulty-based scoring
        points_per_difficulty = {"Facile": 1, "Medio": 3, "Difficile": 5}

        if user_answer == correct_answer:
            points += points_per_difficulty[difficulty]
            progress["players"][player_name]["score"] = points
            message = f"✅ Risposta corretta! +{points_per_difficulty[difficulty]} punti."
        else:
            message = f"❌ Risposta errata! La risposta corretta era: {correct_answer}"

        # Save progress
        with open(JSON_FILE, "w") as f:
            json.dump(progress, f, indent=4)

        return render_template("quiz.html",
                               player_name=player_name,
                               question=request.form.get("question"),
                               options={
                                   "A": request.form.get("option_A"),
                                   "B": request.form.get("option_B"),
                                   "C": request.form.get("option_C")
                               },
                               correct_answer=correct_answer,
                               message=message,
                               points=points,
                               difficulty=difficulty)

    # Generate a new question ONLY when clicking "Genera un'altra domanda"
    response = ask_openai_agent(player_name, difficulty)
    lines = [line.strip() for line in response.split("\n") if line.strip()]

    question_text = lines[0].replace("Domanda:", "").strip()
    options = {
        "A": lines[2].replace("A)", "").strip(),
        "B": lines[3].replace("B)", "").strip(),
        "C": lines[4].replace("C)", "").strip(),
    }
    correct_answer = lines[5].replace("Risposta corretta:", "").strip().split("【")[0]

    return render_template("quiz.html",
                           player_name=player_name,
                           question=question_text,
                           options=options,
                           correct_answer=correct_answer,
                           message=message,
                           points=points,
                           difficulty=difficulty)

@app.route("/leaderboard")
def leaderboard():
    sorted_players = sorted(progress["players"].items(), key=lambda x: x[1]["score"], reverse=True)
    return render_template("leaderboard.html", leaderboard=sorted_players)

if __name__ == "__main__":
    app.run(debug=True)
