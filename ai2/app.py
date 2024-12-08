from flask import Flask, request, render_template, jsonify, url_for,  send_from_directory
import sqlite3
import os
import datetime
import requests
import json
import time

app = Flask(__name__)

# Directory for storing generated content
BASE_DIR = "generated_content"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Database setup
DB_PATH = "database.db"
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_content (
                            user_id TEXT PRIMARY KEY,
                            prompt TEXT,
                            video_paths TEXT,
                            image_paths TEXT,
                            status TEXT,
                            generated_at TEXT
                        )''')
        conn.commit()

init_db()

# Helper function to save content paths to the database
def save_to_db(user_id, prompt, video_paths, image_paths, status):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO user_content 
                          (user_id, prompt, video_paths, image_paths, status, generated_at)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (user_id, prompt, ",".join(video_paths), ",".join(image_paths), status, datetime.datetime.now()))
        conn.commit()

# Helper function to fetch status from the database
def get_status_from_db(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_content WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

# Function to generate video using the provided video generation code
def generate_video(user_id, prompt):
    API_KEY = 'Enter_Your_API_KEY'
    url = 'https://api.novita.ai/v3/async/txt2video'

    # Prepare the prompts based on the user prompt
    prompts = [
        {"prompt": f"{prompt} - frame {i + 1}", "frames": 20} for i in range(6)  # Adjust the number of prompts as needed
    ]

    # Calculate total frames
    total_frames = sum([p["frames"] for p in prompts])
    print(f"Total frames: {total_frames}")

    # Prepare the request payload
    payload = {
        "model_name": "dreamshaper_8_93211.safetensors",
        "height": 512,
        "width": 768,
        "steps": 20,
        "seed": -1,
        "prompts": prompts,
        "negative_prompt": "nsfw, ng_deepnegative_v1_75t, badhandv4, (worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), watermark",
        "guidance_scale": 7.5,
        "closed_loop": False,
        "clip_skip": 3
    }

    # Set up the headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    API_KEY = 'Enter_Your_API_KEY'

    # Make the POST request to start video generation
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check for successful request
    if response.status_code == 200:
        task_id = response.json().get('task_id')
        print(f"Video generation started successfully. Task ID: {task_id}")
        return task_id
    else:
        print(f"Failed to start video generation. Status code: {response.status_code}, Response: {response.text}")
        return None
API_KEY = 'Enter_Your_API_KEY'
headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

# Function to save an image from a URL
def save_image_from_url(json_response, output_directory, file_name):
    image_url = json_response.get("url")
    if not image_url:
        return None

    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, file_name)

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with open(output_file_path, "wb") as file:
            file.write(response.content)
        return output_file_path
    except requests.exceptions.RequestException:
        return None


# Updated function to handle saving images properly
def save_images(response_json, user_id):
    # Create the directory if it doesn't exist
    save_dir = f"generated_content/{user_id}"
    os.makedirs(save_dir, exist_ok=True)

    if not isinstance(response_json, list):
        print("Error: response_json is not a list or valid response.")
        return

    for idx, image_info in enumerate(response_json):
        try:
            if not isinstance(image_info, dict):
                print(f"Invalid data at index {idx}: {image_info}. Skipping.")
                continue

            # Extract the URL from the JSON
            image_url = image_info.get("url")
            if not image_url:
                print(f"No URL found for image {idx}. Skipping.")
                continue
            
            # Download and save the image
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                file_path = os.path.join(save_dir, f"image_{idx + 1}.jpg")
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Image {idx + 1} saved at {file_path}")
            else:
                print(f"Failed to download image {idx + 1}. HTTP Status: {response.status_code}")
        
        except Exception as e:
            print(f"Error while processing image {idx + 1}: {e}")


# Updated get_video_result function to only take task_id as argument
def get_video_result(task_id,user_id):
    status_url = f'https://api.novita.ai/v3/async/task-result?task_id={task_id}'
    max_retries = 10  # Number of times to check before giving up
    wait_time = 30  # Time to wait between checks in seconds

    for attempt in range(max_retries): 
        status_response = requests.get(status_url, headers= headers)

        if status_response.status_code == 200:
            task_info = status_response.json()
            status = task_info.get('task', {}).get('status')
            
            if status == 'TASK_STATUS_SUCCEED':
                video_url = task_info['videos'][0]['video_url']
                print(f"Video generated successfully. Download link: {video_url}")
                # Download the video and save it locally
                user_dir = os.path.join(BASE_DIR, user_id)
                os.makedirs(user_dir, exist_ok=True)
                video_filename = f"{user_id}_video.mp4"
                video_filepath = os.path.join(user_dir, video_filename)

                try:
                    video_response = requests.get(video_url, stream=True)
                    if video_response.status_code == 200:
                        with open(video_filepath, 'wb') as video_file:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                video_file.write(chunk)
                        print(f"Video saved successfully at {video_filepath}")
                        return video_filepath  # Return the local path to the video
                    else:
                        print(f"Failed to download video. Status code: {video_response.status_code}")
                except Exception as e:
                    print(f"Error downloading video: {e}")

                return None  # Indicate failure to download
            elif status in ['TASK_STATUS_FAILED', 'TASK_STATUS_CANCELED']:
                print("Video generation failed or was canceled.")
                return None  # Indicate failure
            else:
                print(f"Video generation still in progress. Attempt {attempt + 1}/{max_retries}")
        else:
            print(f"Failed to retrieve video status. Status code: {status_response.status_code}, Response: {status_response.text}")
        
        # Wait before retrying
        time.sleep(wait_time)

    print("Video generation check timed out.")
    return None  # Indicate timeout

# Route for the main page
@app.route("/")
def index():
    return render_template("index.html")

# Route to handle content generation
@app.route("/generate", methods=["POST"])
def generate_content():
    user_id = request.form.get("user_id")
    prompt = request.form.get("prompt")

    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Set initial status
    save_to_db(user_id, prompt, [], [], "Processing")

    # Generate images
    image_paths = []
    for i in range(5):
        response = requests.post(
            "https://ai-text-to-image-generator-api.p.rapidapi.com/realistic",
            json={"inputs": prompt},
            headers={
                "x-rapidapi-key": "Enter_Your_API_Key",
                "x-rapidapi-host": "ai-text-to-image-generator-api.p.rapidapi.com",
                "Content-Type": "application/json"
            }
        )
        if response.status_code == 200:
            image_file_name = f"image_{i + 1}.jpg"
            image_path = save_image_from_url(response.json(), user_dir, image_file_name)
            if image_path:
                image_paths.append(image_path)
        else:
            print(f"Failed to generate image {i + 1}. Status code: {response.status_code}, Response: {response.text}")

    # Generate video and get video path
    video_paths = []
    task_id = generate_video(user_id, prompt)
    if task_id:
        video_path = get_video_result(task_id, user_id)
        if video_path:
            video_paths.append(video_path)

    # Update status to Completed
    save_to_db(user_id, prompt, video_paths, image_paths, "Completed")

    # Return the user-specific content page link
    user_content_link = url_for('user_content', user_id=user_id, _external=True)
    return jsonify({"message": "Content generation completed!", "link": user_content_link})

# Route to check status
@app.route("/status", methods=["GET"])
def check_status():
    user_id = request.args.get("user_id")
    user_data = get_status_from_db(user_id)

    if user_data:
        base_url = request.host_url.rstrip('/')
        image_links = [url_for('static', filename=path.replace(BASE_DIR + '/', ''), _external=True) for path in user_data[3].split(",") if path]
        video_links = [path for path in user_data[2].split(",") if path]  # Directly use video URLs if saved

        response = {
            "user_id": user_data[0],
            "prompt": user_data[1],
            "video_paths": video_links,
            "image_paths": image_links,
            "status": user_data[4],
            "generated_at": user_data[5]
        }
        return jsonify(response)
    else:
        return jsonify({"error": "No data found for the provided User ID"}), 404

# Serve the 'generated_content' folder as a static folder
@app.route('/generated_content/<path:filename>')
def serve_generated_content(filename):
    return send_from_directory('generated_content', filename)

# Route to display user content
@app.route('/generated_content/<user_id>')
def user_content(user_id):
    user_dir = os.path.join('generated_content', user_id)
    if not os.path.exists(user_dir):
        return render_template('error.html', message="User content not found.")
    
    # Check generation status
    status = "Completed"  # Replace with your database query

    # Fetch video and image paths
    videos = []
    images = []
    if status == "Completed":
        for file in os.listdir(user_dir):
            file_path = f"/generated_content/{user_id}/{file}"  # Updated path
            if file.endswith('.mp4'):
                videos.append(file_path)
            elif file.endswith('.jpg') or file.endswith('.png'):
                images.append(file_path)
    
    return render_template('user_content.html', user_id=user_id, status=status, videos=videos, images=images)

if __name__ == "__main__":
    app.run(debug=True)
