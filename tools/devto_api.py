"""
Dev.to API Tool for Strands Agents

Provides tools for interacting with the Dev.to (Forem) API to create articles.
"""

import os
import requests
from strands import tool


@tool
def create_devto_article(
    title: str,
    body_markdown: str,
    tags: str,
    description: str,
    cover_image_url: str = ""
) -> dict:
    """Create a draft article on Dev.to.

    Args:
        title: The title of the article
        body_markdown: The full article content in markdown format
        tags: Comma-separated list of tags (max 4 tags)
        description: A short description/summary of the article
        cover_image_url: URL to the cover image (optional)

    Returns:
        dict: Response containing article URL and status
    """
    api_key = os.environ.get("DEV_TO_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "message": "DEV_TO_API_KEY environment variable not set"
        }

    # Parse tags - dev.to expects a list of strings, max 4 tags
    tag_list = [tag.strip().lower().replace(" ", "") for tag in tags.split(",")][:4]

    # Build the article payload
    article_data = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "published": False,  # Save as draft
            "tags": tag_list,
            "description": description[:140] if len(description) > 140 else description
        }
    }

    # Add cover image if provided
    if cover_image_url:
        article_data["article"]["main_image"] = cover_image_url

    # Make the API request
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://dev.to/api/articles",
            json=article_data,
            headers=headers,
            timeout=30
        )

        if response.status_code == 201:
            data = response.json()
            return {
                "status": "success",
                "message": "Article created as draft",
                "article_id": data.get("id"),
                "article_url": data.get("url"),
                "edit_url": f"https://dev.to/{data.get('path')}/edit" if data.get('path') else None,
                "title": data.get("title")
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to create article: {response.status_code}",
                "details": response.text
            }

    except requests.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }
