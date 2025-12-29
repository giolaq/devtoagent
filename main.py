#!/usr/bin/env python3
"""
Dev.to Article Generator

A CLI application that uses a swarm of AI agents to generate and publish
technical articles to Dev.to with AI-generated cover images.

Usage:
    python main.py "Your article topic here"
    python main.py --file path/to/transcript.txt
    python main.py --content "Your content here"

Environment Variables Required:
    DEV_TO_API_KEY - Your Dev.to API key
    AWS_REGION - AWS region for Bedrock (default: us-east-1)
    IMGBB_API_KEY - (Optional) ImgBB API key for image hosting
"""

import sys
import os
import logging
from dotenv import load_dotenv

from strands.multiagent import Swarm

from agents.writer import create_writer_agent
from agents.image_gen import create_image_agent
from agents.publisher import create_publisher_agent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Enable debug logging for swarm operations
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)


def validate_environment() -> bool:
    """Validate required environment variables are set.

    Returns:
        bool: True if all required variables are set
    """
    required_vars = ["DEV_TO_API_KEY"]
    missing = [var for var in required_vars if not os.environ.get(var)]

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.info("Please set these in your .env file or environment")
        return False

    # Check AWS credentials (can come from various sources)
    if not any([
        os.environ.get("AWS_ACCESS_KEY_ID"),
        os.environ.get("AWS_PROFILE"),
        os.path.exists(os.path.expanduser("~/.aws/credentials"))
    ]):
        logger.warning("No AWS credentials found. Bedrock calls may fail.")

    return True


def create_article_swarm() -> Swarm:
    """Create the article generation swarm with all agents.

    Returns:
        Swarm: Configured swarm with writer, image, and publisher agents
    """
    # Create the specialized agents
    writer_agent = create_writer_agent()
    image_agent = create_image_agent()
    publisher_agent = create_publisher_agent()

    # Create the swarm with writer as entry point
    swarm = Swarm(
        [writer_agent, image_agent, publisher_agent],
        entry_point=writer_agent,
        max_handoffs=10,
        max_iterations=15,
        execution_timeout=600.0,  # 10 minutes
        node_timeout=300.0,       # 5 minutes per agent
    )

    return swarm


def generate_article(input_data: str, input_type: str = "topic") -> dict:
    """Generate a Dev.to article from the given input.

    Args:
        input_data: The input content (topic, file path, or direct content)
        input_type: Type of input - "topic", "file", or "content"

    Returns:
        dict: Result containing article URL and status
    """
    logger.info(f"Starting article generation with input type: {input_type}")

    # Create the swarm
    swarm = create_article_swarm()

    # Craft the initial prompt based on input type
    if input_type == "topic":
        initial_prompt = f"""
        Please write a comprehensive technical article for Dev.to on the following topic:

        Topic: {input_data}

        Requirements:
        1. The article should be engaging, informative, and practical
        2. Include code examples where appropriate
        3. Target intermediate developers as the audience
        4. The article should be 800-1500 words

        Start by writing the article, then coordinate with the image_agent for a cover image,
        and finally work with the publisher_agent to submit it as a draft to Dev.to.
        """
    elif input_type == "file":
        try:
            with open(input_data, 'r', encoding='utf-8') as f:
                content = f.read()
            initial_prompt = f"""
            Please create a comprehensive technical article for Dev.to based on the following content:

            Source Content:
            {content}

            Requirements:
            1. Transform this content into an engaging Dev.to article
            2. Restructure and enhance the content for better readability
            3. Add practical insights and examples where appropriate
            4. Target intermediate developers as the audience
            5. The article should be 800-1500 words

            Start by writing the article, then coordinate with the image_agent for a cover image,
            and finally work with the publisher_agent to submit it as a draft to Dev.to.
            """
        except FileNotFoundError:
            logger.error(f"File not found: {input_data}")
            return {"status": "error", "error": f"File not found: {input_data}"}
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return {"status": "error", "error": f"Error reading file: {e}"}
    else:  # content
        initial_prompt = f"""
        Please create a comprehensive technical article for Dev.to based on the following content:

        Source Content:
        {input_data}

        Requirements:
        1. Transform this content into an engaging Dev.to article
        2. Restructure and enhance the content for better readability
        3. Add practical insights and examples where appropriate
        4. Target intermediate developers as the audience
        5. The article should be 800-1500 words

        Start by writing the article, then coordinate with the image_agent for a cover image,
        and finally work with the publisher_agent to submit it as a draft to Dev.to.
        """

    # Execute the swarm
    try:
        result = swarm(initial_prompt)

        logger.info(f"Swarm completed with status: {result.status}")
        logger.info(f"Agents involved: {[node.node_id for node in result.node_history]}")
        logger.info(f"Total iterations: {result.execution_count}")

        return {
            "status": str(result.status),
            "agents_used": [node.node_id for node in result.node_history],
            "iterations": result.execution_count,
            "execution_time_ms": result.execution_time,
            "result": result
        }

    except Exception as e:
        logger.error(f"Swarm execution failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def main():
    """Main entry point for the CLI application."""
    # Load environment variables from .env file
    load_dotenv()

    # Check for arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python main.py "Your article topic here"')
        print('  python main.py --file path/to/transcript.txt')
        print('  python main.py --file path/to/article.md')
        print('  python main.py --content "Your content here"')
        print("\nExamples:")
        print('  python main.py "Getting Started with Amazon Strands Agents SDK"')
        print('  python main.py --file transcript.txt')
        print('  python main.py --content "$(cat my_article.md)"')
        sys.exit(1)

    # Parse arguments
    input_type = "topic"
    input_data = sys.argv[1]

    if sys.argv[1] == "--file" and len(sys.argv) >= 3:
        input_type = "file"
        input_data = sys.argv[2]
    elif sys.argv[1] == "--content" and len(sys.argv) >= 3:
        input_type = "content"
        input_data = sys.argv[2]

    # Validate environment
    if not validate_environment():
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  Dev.to Article Generator - Powered by Strands Agents")
    print("=" * 60)
    
    if input_type == "topic":
        print(f"\nTopic: {input_data}\n")
    elif input_type == "file":
        print(f"\nInput File: {input_data}\n")
    else:
        print(f"\nInput Content: {input_data[:100]}{'...' if len(input_data) > 100 else ''}\n")
    
    print("Starting agent swarm...")
    print("-" * 60 + "\n")

    # Generate the article
    result = generate_article(input_data, input_type)

    print("\n" + "-" * 60)
    print("RESULT:")
    print("-" * 60)
    print(f"Status: {result['status']}")

    if result['status'] == 'error':
        print(f"Error: {result.get('error', 'Unknown error')}")
    else:
        print(f"Agents used: {' -> '.join(result.get('agents_used', []))}")
        print(f"Iterations: {result.get('iterations', 'N/A')}")
        print(f"Execution time: {result.get('execution_time_ms', 'N/A')}ms")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
