# AI-Video-and-Image-Generation-System

Welcome to the AI Video and Image Generation System! This project generates motivational videos and images based on user-provided text prompts, storing them for user access. Users are notified when their content is ready and can view it through a simple web interface.

## Features
- **Text-to-Video Generation**: Generates 5 motivational videos using AI tools like RunwayML.
- **Text-to-Image Generation**: Creates 5 motivational images using tools like OpenAI’s DALL·E.
- **Content Management**: Stores generated content in a structured directory format and tracks generation status in a database.
- **User Access**: Provides a web interface for users to view their generated content.
- **Notifications**: Notifies users when their content is ready via email or system notifications.

---


## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd AI-Video-and-Image-Generation-System
cd ai2
```

### Step 2: Install Dependencies
Ensure you have Python 3.8 or above installed.
```bash
pip install -r requirements.txt
```

### Step 3: Update Configuration
- Add API keys for video and image generation in `main.py`.

### Step 4: Run the System
1. Start the video and image generation service:
   ```bash
   python app.py
   ```

---

## Usage
1. **Submit a Text Prompt**: Enter a motivational prompt to generate content.
2. **View Content**:
   - Log in using your unique `user_id`.
   - View generated videos and images in a gallery/grid layout.
   - If content is still processing, a message will be displayed.
3. **Receive Notifications**: Get notified when content is ready via your preferred method.

---

## Dependencies
- **Programming Language**: Python 3.8+
- **AI APIs**:
  - Video Generation API
  - Image Generation API
- **Framework**: Flask (for the web interface)
- **Database**: SQLite (for user and generation data storage)
- **File Storage**: Local file system

Install all dependencies listed in `requirements.txt`.

---

## API Configuration
In `app.py`, add your API keys:
```python
VIDEO_API_KEY = "your_api_key"
IMAGE_API_KEY = "your_api_key"
```


---


## Contribution Guidelines
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with detailed descriptions of your changes.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.



Happy coding! 🚀
