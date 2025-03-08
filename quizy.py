import tkinter as tk
import json
import random
from agent import ask_openai_agent

# Load or create progress JSON file
JSON_FILE = "progress.json"
try:
    with open(JSON_FILE, "r") as f:
        progress = json.load(f)
except FileNotFoundError:
    progress = {"players": {}}

# GUI Setup
root = tk.Tk()
root.title("Badanti Knowledge Game")

# UI Elements
player_label = tk.Label(root, text="Inserisci il tuo nome:")
player_label.pack()

player_entry = tk.Entry(root)
player_entry.pack()

difficulty_label = tk.Label(root, text="Seleziona la difficoltà:")
difficulty_label.pack()

difficulty_var = tk.StringVar(root)
difficulty_var.set("Facile")  # Default difficulty

difficulty_dropdown = tk.OptionMenu(root, difficulty_var, "Facile", "Medio", "Difficile")
difficulty_dropdown.pack()

question_label = tk.Label(root, text="Premi 'Genera domanda' per partire.", wraplength=400, justify="left")
question_label.pack()

generate_button = tk.Button(root, text="Genera la domanda")
generate_button.pack()

# Radio Buttons for Multiple Choice
choice_var = tk.StringVar()
choice_var.set(None)  # Default to no selection

option_a = tk.Radiobutton(root, text="Opzione A", variable=choice_var, value="A")
option_b = tk.Radiobutton(root, text="Opzione B", variable=choice_var, value="B")
option_c = tk.Radiobutton(root, text="Opzione C", variable=choice_var, value="C")

option_a.pack()
option_b.pack()
option_c.pack()

submit_button = tk.Button(root, text="Invia risposta")
submit_button.pack()

result_label = tk.Label(root, text="I risultati appariranno qui.")
result_label.pack()

score_label = tk.Label(root, text="Punteggio: 0")
score_label.pack()

# Logic to Track Questions & Answers
current_question = ""
correct_answer = ""


def generate_question_for_ui():
    """Fetch a multiple-choice question from OpenAI Agent and display it correctly."""
    global current_question, correct_answer
    player_name = player_entry.get().strip()
    difficulty = difficulty_var.get()  # Get selected difficulty

    if not player_name:
        result_label.config(text="Inserisci il nome!")
        return

    # Get question from OpenAI Agent
    response = ask_openai_agent(player_name, difficulty)

    # Print response for debugging
    print("\n🔹 Full API Response in GUI:", response)

    # Parse response
    try:
        lines = [line.strip() for line in response.split("\n") if line.strip()]  # Remove empty lines
        print("\n🔹 Parsed Lines:", lines)  # Debug Output

        # Extract Question
        question_text = lines[0].replace("Domanda:", "").strip()

        # Extract Options
        options = {
            "A": lines[2].replace("A)", "").strip(),
            "B": lines[3].replace("B)", "").strip(),
            "C": lines[4].replace("C)", "").strip(),
        }

        # Extract Correct Answer
        correct_answer = lines[5].replace("Risposta corretta:", "").strip().split("【")[0]  # Remove citation reference

        # Print extracted values for debugging
        print("\n✅ Extracted Question:", question_text)
        print("✅ Options:", options)
        print("✅ Correct Answer:", correct_answer)

        # Update UI
        question_label.config(text=question_text)
        option_a.config(text=f"A) {options['A']}")
        option_b.config(text=f"B) {options['B']}")
        option_c.config(text=f"C) {options['C']}")
        choice_var.set(None)

    except IndexError:
        result_label.config(text="Errore nel parsing della domanda.")
        return



def submit_answer():
    """Submit the selected multiple-choice answer to OpenAI Agent and update score."""
    global correct_answer
    player_name = player_entry.get().strip()
    user_answer = choice_var.get()

    if not player_name:
        result_label.config(text="Inserisci il nome!")
        return

    if not user_answer:
        result_label.config(text="Seleziona una risposta prima di inviare!")
        return

    # Ensure the player exists in the progress JSON
    if player_name not in progress["players"]:
        progress["players"][player_name] = {"score": 0}  # Initialize player with score 0

    # Validate answer
    if user_answer == correct_answer:
        result_label.config(text="Risposta corretta! 🎉")
        progress["players"][player_name]["score"] += 1  # Increase score
    else:
        result_label.config(text=f"Risposta errata! La risposta giusta era: {correct_answer}")

    # Save progress
    with open(JSON_FILE, "w") as f:
        json.dump(progress, f, indent=4)

    # Update UI
    score_label.config(text=f"Punteggio: {progress['players'][player_name]['score']}")


generate_button.config(command=generate_question_for_ui)
submit_button.config(command=submit_answer)

root.mainloop()
