# Occupational Safety and Health Chatbot

A multimodal AI-powered chatbot that analyzes workplace images for safety hazards and generates detailed safety reports based on DOSH Malaysia regulations.

## 🚀 Features

- **Image Analysis**: Upload workplace images for AI-powered safety hazard detection
- **Safety Report Generation**: Automatic generation of detailed safety reports in Word format
- **User Information Management**: Track user details and sector information
- **Feedback System**: Built-in feedback mechanism for continuous improvement
- **Export Capabilities**: Export analysis results as Word documents
- **JSON Data Storage**: Automatic storage of analysis data in JSON format

## 📋 Prerequisites

- Python 3.8 or higher
- Ollama server running locally (http://127.0.0.1:11434)
- Required Python packages (see Installation section)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is installed and running:
- Download Ollama from [ollama.ai](https://ollama.ai)
- Install and start the Ollama server
- The server should be running at http://127.0.0.1:11434

## ⚙️ Configuration

The application uses the following default configurations:
- Ollama Server: http://127.0.0.1:11434
- Default Model: llava:13b
- Server Port: 8002
- Request Timeout: 200 seconds

You can modify these settings in the `safety_regulations_askollama.py` file:
```python
OLLAMA_SERVER = "http://127.0.0.1:11434"
MODEL_USED = "llava:13b"
REQUEST_TIMEOUT = 200
```

## 🚀 Running the Application

1. Start the Ollama server if not already running
2. Run the application:
```bash
python safety_regulations_askollama.py
```
3. Access the application at:
   - Local: http://localhost:8002
   - Public URL: Will be provided in the console after launch

## 📁 Project Structure

```
├── safety_regulations_askollama.py  # Main application file
├── requirements.txt                 # Required Python packages
├── uploaded_data/                   # Directory for uploaded images and analysis
├── user_reports/                    # Directory for user feedback reports
└── README.md                        # This documentation file
```

### Important Files and Folders
- `safety_regulations_askollama.py`: The main application file that contains all core functionality
- `requirements.txt`: Contains all required Python packages for the system
- `uploaded_data/`: Stores uploaded images, analysis reports, and JSON data
- `user_reports/`: Stores user feedback and reports in JSON format

### Non-Essential Files
The following files and folders are not required for running the system:
- `askollama.py`
- `cam_askollama.py`
- `rag.py`
- `video_askollama.py`
- `rag_data/`
- `testing_img/`
- `__pycache__/`
- `.gradio/`

## 💻 Usage

1. **User Information**
   - Enter your name
   - Enter your staff ID
   - Select your sector from the dropdown

2. **Image Analysis**
   - Upload a workplace image
   - (Optional) Add a description of the activity
   - Click "Start" to begin analysis

3. **View Results**
   - Review the analysis in the markdown format
   - Click "Export Report Analysis" to generate a Word document
   - Download the generated report

4. **Provide Feedback**
   - Click "SHARE YOUR THOUGHTS" to expand the feedback section
   - Rate your experience
   - Provide feedback or report issues
   - Submit your feedback

## 🔧 Available Models

The application supports multiple models:
- llava:7b
- bakllava:7b
- gemma3:12b
- llava:13b (default)
- qwen2.5vl:7b

To change the model, modify the `MODEL_USED` variable in the code.

## 📊 Data Storage

- **Analysis Data**: Stored in `uploaded_data/` directory
  - Images: `[timestamp]_image.png`
  - Analysis: `[timestamp]_analysis.docx`
  - JSON data: `[timestamp].json`

- **User Reports**: Stored in `user_reports/` directory
  - Feedback: `[timestamp]_report.json`

## 🤝 Contributing

For any issues or improvements:
1. Create a detailed issue report
2. Provide steps to reproduce
3. Include relevant screenshots or logs

## 📝 License

[Your License Information]

## 👥 Contact

For support or questions, contact:
[Your Contact Information]

## 🔄 Version History

- v1.0.0: Initial release
  - Basic image analysis functionality
  - Word document generation
  - User feedback system
  - JSON data storage 