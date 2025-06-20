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
VIDEO_PATH = r"C:\Users\hyper\Downloads\video test data set\Old People Falling - With Sad Music.mp4"

# Initialize video capture
cap = cv2.VideoCapture(VIDEO_PATH)

# Global variable to store the last Ollama response
last_result = "Processing..."
lock = threading.Lock()
frame_queue = Queue(maxsize=1)  # Queue to hold only 1 frame at a time
result_queue = Queue(maxsize=1)  # Queue to hold only 1 result at a time

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
            "prompt": ("Respond in 1 sentence (Yes or No) and include confidence score, Is there any falling event? If no falling event are present, say: 'No. Confidence: 100%."),
            "stream": False,
            "images": [image_base64],
        }

        try:
            response = requests.post(f"{OLLAMA_SERVER}/api/generate", json=payload, timeout=30)
            response.raise_for_status()
            response_data = response.json()

            # Update last result in a thread-safe manner
            with lock:
                last_result = response_data.get("response", "No response received")

            # Put the result in the result queue
            result_queue.put(last_result)

        except requests.exceptions.Timeout:
            with lock:
                last_result = "Error: Timeout"
            result_queue.put(last_result)
        except requests.exceptions.ConnectionError:
            with lock:
                last_result = "Error: Connection failed"
            result_queue.put(last_result)
        except Exception as e:
            with lock:
                last_result = f"Error: {e}"
            result_queue.put(last_result)

        time.sleep(1)  # Limit to 1 request per second

# Start the worker thread to process frames
ollama_thread = threading.Thread(target=ask_ollama, daemon=True)
ollama_thread.start()

# Start the video processing loop
frame_skip = 2  # Process every 2nd frame
frame_count = 0

# Create a named window
cv2.namedWindow("Risk Detection", cv2.WINDOW_NORMAL)  # Create a resizable window
cv2.resizeWindow("Risk Detection", 1280, 720)  # Set the desired window size (e.g., 1280x720)

# Define the display window dimensions
display_width = 1280
display_height = 720

# Get the frame rate of the video
fps = cap.get(cv2.CAP_PROP_FPS)
frame_delay = int(1000 / fps)  # Delay in milliseconds

current_result = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # End of video

    frame_count += 1

    # Skip frames
    if frame_count % frame_skip != 0:
        continue  # Skip this frame

    # Get original frame dimensions
    original_height, original_width = frame.shape[:2]

    # Calculate aspect ratios
    aspect_ratio = original_width / original_height
    display_aspect_ratio = display_width / display_height

    # Determine new dimensions while maintaining aspect ratio
    if aspect_ratio > display_aspect_ratio:
        # Frame is wider than display
        new_width = display_width
        new_height = int(display_width / aspect_ratio)
    else:
        # Frame is taller than display
        new_height = display_height
        new_width = int(display_height * aspect_ratio)

    # Resize the frame
    frame_resized = cv2.resize(frame, (new_width, new_height))

    # Create a black canvas to place the resized frame
    canvas = np.zeros((display_height, display_width, 3), dtype=np.uint8)

    # Calculate the position to center the frame
    x_offset = (display_width - new_width) // 2
    y_offset = (display_height - new_height) // 2

    # Place the resized frame on the canvas
    canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = frame_resized

    # Send every frame to Ollama
    if frame_queue.empty():
        frame_queue.put(canvas)

    # Check if a new result is available
    try:
        new_result = result_queue.get(block=False)
        current_result = new_result
    except:
        pass

    # Display the current result
    if current_result is not None:
        font = cv2.FONT_HERSHEY_SIMPLEX
        max_width = 150  # Max characters per line
        max_lines = 20   # Maximum lines to display

        # Wrap text into multiple lines
        wrapped_text = textwrap.wrap(current_result, width=max_width)[:max_lines]

        # Dynamically adjust font scale based on the number of lines
        base_font_scale = 0.3  # Default font size
        base_thickness = 1
        min_font_scale = 0.3   # Smallest allowed font
        min_thickness = 1

        # Reduce font size if text is too long
        scale_factor = max(1, len(wrapped_text) / max_lines)  # Adjust scale
        font_scale = max(min_font_scale, base_font_scale / scale_factor)
        thickness = max(min_thickness, base_thickness // scale_factor)

        # Define text box size based on content
        text_x, text_y = 10, 30
        line_height = int(30 * font_scale)  # Adjusted line spacing
        box_width = 800  # Fixed width
        box_height = line_height * len(wrapped_text) + 20  # Adjust height

        # Draw semi-transparent background rectangle (dynamically sized)
        overlay = canvas.copy()
        alpha = 0.6
        cv2.rectangle(overlay, (text_x - 5, text_y - 20), 
                    (text_x + box_width, text_y + box_height), (255, 255, 255), cv2.FILLED)
        cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)

        # Draw each line of wrapped text
        for i, line in enumerate(wrapped_text):
            y_position = text_y + (i * line_height)
            cv2.putText(canvas, line, (text_x, y_position), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

    # Show the frame
    cv2.imshow("Risk Detection", canvas)

    # Break on 'q' key press
    if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()