from io import BytesIO
import base64
import gradio as gr
import time
import requests

OLLAMA_SERVER = "http://127.0.0.1:11434"

def ask_ollama(image, prompt):
    if image is None or not prompt:
        return "Please upload an image and enter a prompt."

    # Convert PIL image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode()

    payload = {
        "model": "llava:7b",
        "prompt": prompt,
        "stream": False,
        "images": [image_base64]
    }

    try:
        print("Sending request to Ollama...")
        start_time = time.time()
        response = requests.post(f"{OLLAMA_SERVER}/api/generate", json=payload, timeout=100)
        response.raise_for_status()  # Ensure we catch HTTP errors
        response_data = response.json()
        end_time = time.time()

        print("Ollama response:", response_data)  # Debugging print

        # Extract response text
        model_output = response_data.get("response", "No response received")
        return model_output

    except requests.exceptions.Timeout:
        return "Error: Request to Ollama timed out. Make sure the Ollama server is running."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Ensure it's running on the correct port."
    except Exception as e:
        return f"Unexpected error: {e}"

iface = gr.Interface(
    fn=ask_ollama,
    inputs=[gr.Image(type="pil"), gr.Textbox(placeholder="Enter your prompt")],
    outputs="text",
    title="Ollama Chatbot",
    description="Upload an image and enter a prompt to interact with the Ollama model."
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=8002, share = True)