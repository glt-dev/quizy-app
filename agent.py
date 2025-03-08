import openai
import time
from constants import OPENAI_API_KEY, ASSISTANT_ID

# Set OpenAI API Key
openai.api_key = OPENAI_API_KEY

def ask_openai_agent(user_name, difficulty):
    """Trigger the OpenAI Assistant and retrieve a multiple-choice question."""
    try:
        # Step 1: Create a new thread
        thread = openai.beta.threads.create()

        # Step 2: Add a message to the thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Livello di difficoltà: {difficulty}."
        )

        # Step 3: Run the Assistant on the thread
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Step 4: Wait for the Assistant to complete the response
        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status in ["completed", "failed"]:
                break  # Stop waiting when finished
            time.sleep(1)  # Wait a second before checking again

        # Step 5: Retrieve the latest messages from the thread
        messages = openai.beta.threads.messages.list(thread_id=thread.id)

        # Step 6: Extract the latest assistant response
        for message in reversed(messages.data):
            if message.role == "assistant":
                print("\n🔹 Assistant Response:", message.content[0].text.value)  # Debug Output
                return message.content[0].text.value  # Extracted text response

        return "Errore: nessuna domanda valida trovata."

    except Exception as e:
        return f"Errore nella generazione della domanda: {str(e)}"
