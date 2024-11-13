import json
import os
from datetime import datetime

import markdown
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = "blog_posts"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize posts.json if it doesn't exist
metadata_path = os.path.join(UPLOAD_FOLDER, "posts.json")
if not os.path.exists(metadata_path):
    with open(metadata_path, "w") as f:
        json.dump([], f, indent=2)


@app.route("/api/blog/post", methods=["POST"])
def create_post():
    try:
        # Print request data for debugging
        print("Request Content-Type:", request.content_type)
        print("Request Data:", request.get_data())

        # Handle both form data and JSON input
        if request.content_type and "application/json" in request.content_type:
            try:
                data = request.get_json(force=True)
                title = data.get("title")
                content = data.get("content")
            except Exception as e:
                print("JSON parsing error:", str(e))
                return jsonify({"success": False, "message": "Invalid JSON data"}), 400
        else:
            title = request.form.get("title")
            content = request.form.get("content")

        if not title or not content:
            return (
                jsonify(
                    {"success": False, "message": "Title and content are required"}
                ),
                400,
            )

        # Generate filename from title and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{title.lower().replace(' ', '_')}.md"

        # Save the post
        post_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(post_path, "w") as f:
            f.write(content)

        metadata = {
            "title": title,
            "date": datetime.now().strftime("%B %d, %Y"),
            "filename": filename,
            "content": content,  # Include content in metadata
        }

        metadata_path = os.path.join(UPLOAD_FOLDER, "posts.json")
        posts = []

        # Load existing posts if file exists
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                posts = json.load(f)

        # Append new post
        posts.append(metadata)

        # Save updated posts
        with open(metadata_path, "w") as f:
            json.dump(posts, f, indent=2)

        return jsonify({"success": True, "message": "Post created successfully"})
    except Exception as e:
        print("Error creating post:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/blog/posts", methods=["GET"])
def get_posts():
    try:
        metadata_path = os.path.join(UPLOAD_FOLDER, "posts.json")
        print("Fetching posts from:", metadata_path)

        # Initialize empty posts.json if it doesn't exist
        if not os.path.exists(metadata_path):
            print("posts.json doesn't exist, creating new file")
            with open(metadata_path, "w") as f:
                json.dump([], f, indent=2)
            return jsonify({"success": True, "posts": []})

        # Read existing posts
        with open(metadata_path, "r") as f:
            try:
                posts = json.load(f)
                print(f"Loaded {len(posts)} posts from posts.json")
                for post in posts:
                    print(f"Post title: {post.get('title')}")
            except json.JSONDecodeError as e:
                print("Error decoding posts.json:", str(e))
                # Reset file if JSON is invalid
                posts = []
                with open(metadata_path, "w") as f:
                    json.dump(posts, f, indent=2)

        # Sort posts by date (newest first)
        posts.sort(
            key=lambda x: datetime.strptime(x.get("date", ""), "%B %d, %Y"),
            reverse=True,
        )

        response_data = {"success": True, "posts": posts}
        print("Sending response:", json.dumps(response_data, indent=2))

        # Add CORS headers explicitly
        response = jsonify(response_data)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print("Error getting posts:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

    except Exception as e:
        print("Error getting posts:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
