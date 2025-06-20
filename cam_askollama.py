import cv2
import base64
import time
import requests
import numpy as np
import threading
from io import BytesIO
from PIL import Image
from queue import Queue
import textwrap  # For wrapping long text

OLLAMA_SERVER = "http://127.0.0.1:11434"
CAMERA_INDEX = 0  # Change if needed
VIDEO_PATH = r"C:\Users\hyper\Downloads\AlexanderMelde SPHAR-Dataset master videos-murdering\uccrime_Shooting031_x264.mp4"

# Initialize video capture with a lower resolution for better speed
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduce resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 40)  # Try increasing FPS

# Global variable to store the last Ollama response
last_result = "Processing..."
lock = threading.Lock()
frame_queue = Queue(maxsize=1)  # Queue to hold only 1 frame at a time

def ask_ollama():
    """Continuously process frames from the queue for fall detection."""
    global last_result

    while True:
        frame = frame_queue.get()  # Get latest frame (blocks if empty)

        # Convert OpenCV frame (BGR) to PIL (RGB)
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Convert PIL image to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=30)  # Lower quality for speed
        image_base64 = base64.b64encode(buffered.getvalue()).decode()

        payload = {
            "model": "llava:7b",
            "prompt": ("List the physical risks and threats to human lives in the image and give percentage confidence score. If no risks are present, say 'No risks present'."),
            "stream": False,
            "images": [image_base64]
        }

        try:
            response = requests.post(f"{OLLAMA_SERVER}/api/generate", json=payload, timeout=30)
            response.raise_for_status()
            response_data = response.json()

            # Update last result in a thread-safe manner
            with lock:
                last_result = response_data.get("response", "No response received")

        except requests.exceptions.Timeout:
            with lock:
                last_result = "Error: Timeout"
        except requests.exceptions.ConnectionError:
            with lock:
                last_result = "Error: Connection failed"
        except Exception as e:
            with lock:
                last_result = f"Error: {e}"

        time.sleep(1)  # Limit to 1 request per second

# Start the worker thread to process frames
ollama_thread = threading.Thread(target=ask_ollama, daemon=True)
ollama_thread.start()

# Start the camera loop
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

frame_skip = 5  # Only process 1 frame every 5 frames

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Resize for faster processing
    frame_resized = cv2.resize(frame, (640, 480))

    # Only send every 10th frame to Ollama
    if frame_queue.empty():  # Ensure only 1 request is processed at a time
        frame_queue.put(frame_resized)

    # Display latest Ollama result with word wrapping
    with lock:
        text = last_result
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        text_color = (0, 0, 0)  # Black text
        bg_color = (255, 255, 255)  # White background
        text_x, text_y = 10, 30
        max_width = 400  # Maximum text width before wrapping

        # Split text into multiple lines if it's too long
        wrapped_text = textwrap.wrap(text, width=40)  # Adjust width for wrapping
        line_height = 25  # Space between lines

        # Calculate background size dynamically based on text lines
        text_w = max(cv2.getTextSize(line, font, font_scale, thickness)[0][0] for line in wrapped_text)
        text_h = line_height * len(wrapped_text)

        # Draw semi-transparent background rectangle
        overlay = frame.copy()
        alpha = 0.6  # Transparency factor
        cv2.rectangle(overlay, (text_x - 5, text_y - 20), 
                      (text_x + text_w + 10, text_y + text_h), bg_color, cv2.FILLED)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Draw the text line by line
        for i, line in enumerate(wrapped_text):
            y_position = text_y + (i * line_height)
            cv2.putText(frame, line, (text_x, y_position), font, font_scale, text_color, thickness, cv2.LINE_AA)

    # Show the frame
    cv2.imshow("Fall Detection", frame)

    # Break on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
