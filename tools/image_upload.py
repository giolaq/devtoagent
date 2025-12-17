"""
Image Upload Tool for Strands Agents

Provides functionality to upload images to ImgBB and get public URLs.
"""

import os
import base64
import requests
from strands import tool


@tool
def upload_image(image_path: str) -> dict:
    """Upload an image to ImgBB and get a public URL.

    Args:
        image_path: Path to the local image file to upload

    Returns:
        dict: Response containing the public URL and status
    """
    api_key = os.environ.get("IMGBB_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "message": "IMGBB_API_KEY environment variable not set. Image will not be uploaded.",
            "url": None
        }

    # Check if file exists
    if not os.path.exists(image_path):
        return {
            "status": "error",
            "message": f"Image file not found: {image_path}",
            "url": None
        }

    # Read and encode the image
    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read image file: {str(e)}",
            "url": None
        }

    # Upload to ImgBB
    try:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": api_key,
                "image": image_data,
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                image_url = data["data"]["url"]
                return {
                    "status": "success",
                    "message": f"Image uploaded successfully",
                    "url": image_url,
                    "delete_url": data["data"].get("delete_url"),
                    "display_url": data["data"].get("display_url")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Upload failed: {data.get('error', {}).get('message', 'Unknown error')}",
                    "url": None
                }
        else:
            return {
                "status": "error",
                "message": f"Upload failed with status {response.status_code}: {response.text}",
                "url": None
            }

    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}",
            "url": None
        }
