# Dev.to Article Generator

> An intelligent multi-agent system that automatically generates, illustrates, and publishes technical articles to Dev.to using AI.

## Overview

Dev.to Article Generator is a powerful CLI application built with the [Amazon Strands Agents SDK](https://github.com/awslabs/amazon-strands) that leverages a swarm of specialized AI agents to create publication-ready technical articles. The system uses Claude 3.5 Sonnet via Amazon Bedrock to write engaging content, generate cover images, and publish directly to your Dev.to account.

## Features

- **Multi-Agent Architecture**: Three specialized agents working together
  - **Writer Agent**: Creates well-structured technical articles with code examples
  - **Image Agent**: Generates cover images using Stable Diffusion via Bedrock
  - **Publisher Agent**: Automatically publishes articles to Dev.to as drafts

- **Intelligent Content Generation**
  - Markdown-formatted articles optimized for Dev.to
  - Automatic code syntax highlighting
  - Well-structured sections with headings
  - SEO-friendly tags and descriptions

- **Cover Image Integration**
  - AI-generated cover images
  - Automatic image upload to ImgBB
  - Images embedded directly in article content

- **Automated Publishing**
  - Direct integration with Dev.to API
  - Articles saved as drafts for review
  - Automatic tag and metadata management
  - Cover image insertion into article body

## Architecture

The application uses a **Swarm Architecture** where specialized agents collaborate through conversation history to accomplish complex tasks.

```
┌─────────────────────────────────────────────────────────────┐
│                     User Input (Topic)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    SWARM ORCHESTRATOR                       │
│              (Strands Multi-Agent Framework)                │
└─────────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│    WRITER    │ │    IMAGE     │ │  PUBLISHER   │
│    AGENT     │ │    AGENT     │ │    AGENT     │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        ▼               ▼               ▼
    Article         Cover Image      Dev.to API
   (Markdown)      (Generated +      (Published
                    Uploaded)          Draft)
```

### Agent Workflow

1. **Writer Agent** (`agents/writer.py`)
   - Receives the article topic
   - Generates comprehensive technical content in markdown
   - Outputs structured data: TITLE, TAGS, DESCRIPTION, BODY
   - Hands off to Image Agent

2. **Image Agent** (`agents/image_gen.py`)
   - Receives article context from conversation history
   - Generates cover image using Stable Diffusion (Bedrock)
   - Uploads image to ImgBB for public URL
   - Passes IMAGE_URL to Publisher Agent

3. **Publisher Agent** (`agents/publisher.py`)
   - Extracts article components from conversation history
   - Finds IMAGE_URL from Image Agent's message
   - Inserts cover image at beginning of article body
   - Publishes to Dev.to using the API
   - Returns article URL and confirmation

### Data Flow

Agents communicate through **conversation history** rather than direct data passing:

```
Writer Agent Output:
├── TITLE: Python Type Hints: A Practical Guide
├── TAGS: python, programming, tutorial, typing
├── DESCRIPTION: Learn how to use Python type hints...
└── BODY: [Full markdown article content]

Image Agent Output:
├── Generated Image: output/cover_image.png
└── IMAGE_URL: https://i.ibb.co/xxxxx/image.png

Publisher Agent:
├── Extracts: TITLE, TAGS, DESCRIPTION, BODY
├── Finds: IMAGE_URL
├── Inserts: ![Cover Image](IMAGE_URL) into BODY
└── Publishes: Complete article to Dev.to
```

## Prerequisites

- **Python 3.11+**
- **AWS Account** with access to Amazon Bedrock
- **Dev.to Account** and API key
- **ImgBB Account** (optional, for image hosting)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/devtoagent.git
cd devtoagent
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure AWS Credentials

Set up AWS credentials for Bedrock access:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

### 5. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required
DEV_TO_API_KEY=your_dev_to_api_key

# Optional (for image upload)
IMGBB_API_KEY=your_imgbb_api_key

# AWS Configuration
AWS_REGION=us-east-1
```

#### Getting API Keys

**Dev.to API Key:**
1. Visit https://dev.to/settings/extensions
2. Generate a new API key
3. Copy and paste into `.env`

**ImgBB API Key** (Optional):
1. Visit https://api.imgbb.com/
2. Sign up for a free account
3. Get your API key
4. Add to `.env`

> **Note:** Without ImgBB API key, cover images will still be generated but won't be uploaded. They'll be saved locally in the `output/` directory.

## Usage

### Basic Usage

Generate and publish an article from different input types:

**From a topic:**
```bash
python main.py "Your Article Topic Here"
```

**From a file (transcript, markdown, etc.):**
```bash
python main.py --file path/to/your/content.txt
python main.py --file transcript.md
```

**From direct content:**
```bash
python main.py --content "Your content here"
# Or from a file using shell substitution:
python main.py --content "$(cat my_article.md)"
```

### Examples

**Example 1: Generate a Python tutorial**
```bash
python main.py "Getting Started with FastAPI"
```

**Example 2: Write about Docker**
```bash
python main.py "Docker Best Practices for Production"
```

**Example 4: Transform a video transcript**
```bash
python main.py --file conference_talk_transcript.txt
```

**Example 5: Convert existing markdown content**
```bash
python main.py --file technical_notes.md
```

**Example 6: Process content directly**
```bash
python main.py --content "Today I learned about microservices architecture..."
```

### What Happens Next

1. The Writer Agent creates a comprehensive article (30-60 seconds)
2. The Image Agent generates and uploads a cover image (60-90 seconds)
3. The Publisher Agent publishes to Dev.to (10-20 seconds)
4. You receive the article URL to review and publish

### Output

```
============================================================
  Dev.to Article Generator - Powered by Strands Agents
============================================================

Topic: Getting Started with Python Type Hints

Starting agent swarm...
------------------------------------------------------------

[Writer Agent generates article...]
[Image Agent creates cover image...]
[Publisher Agent publishes to Dev.to...]

------------------------------------------------------------
RESULT:
------------------------------------------------------------
Status: Status.COMPLETED
Agents used: writer_agent -> image_agent -> publisher_agent
Iterations: 3
Execution time: 197478ms
============================================================

Article URL: https://dev.to/username/article-slug
```

## Project Structure

```
devtoagent/
├── agents/                  # AI agent definitions
│   ├── __init__.py
│   ├── writer.py           # Article writing agent
│   ├── image_gen.py        # Cover image generation agent
│   └── publisher.py        # Dev.to publishing agent
│
├── tools/                   # Tool definitions for agents
│   ├── __init__.py
│   ├── devto_api.py        # Dev.to API integration
│   └── image_upload.py     # ImgBB image upload tool
│
├── output/                  # Generated images (gitignored)
│
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## How It Works

### 1. Swarm Initialization

When you run the application, it creates a Swarm with three agents:

```python
swarm = Swarm(
    [writer_agent, image_agent, publisher_agent],
    entry_point=writer_agent,
    max_handoffs=10,
    max_iterations=15,
    execution_timeout=600.0
)
```

### 2. Writer Agent Execution

The Writer Agent receives your topic and:
- Analyzes the subject matter
- Generates a compelling title
- Creates well-structured content with code examples
- Outputs structured data with clear markers:

```markdown
TITLE: Docker Containers: A Practical Guide

TAGS: docker, devops, containers, programming

DESCRIPTION: Learn Docker containers from basics to best practices

BODY:
## Introduction
Docker has revolutionized...
[Full article content]
```

### 3. Image Generation

The Image Agent:
- Analyzes the article topic
- Generates a prompt for Stable Diffusion
- Creates a cover image (1024x1024, modern tech aesthetic)
- Uploads to ImgBB if API key is available
- Returns: `IMAGE_URL: https://i.ibb.co/xxxxx/image.png`

### 4. Publishing

The Publisher Agent:
- Scans the entire conversation history
- Extracts: TITLE, TAGS, DESCRIPTION, BODY
- Finds: IMAGE_URL (if available)
- Prepends image to article body:
  ```markdown
  ![Cover Image](https://i.ibb.co/xxxxx/image.png)

  ## Introduction
  [Rest of article...]
  ```
- Calls Dev.to API to create draft article
- Returns article URL

### 5. Conversation History

All agents share context through conversation history:

```
Message 1 (User): "Write article about Docker"
Message 2 (Writer): "TITLE: Docker Guide\nTAGS: docker\n..."
Message 3 (Writer->Image): "Handoff to image_agent"
Message 4 (Image): "IMAGE_URL: https://..."
Message 5 (Image->Publisher): "Handoff to publisher_agent"
Message 6 (Publisher): "Article published at https://dev.to/..."
```

## Configuration

### Agent Customization

You can customize agent behavior by modifying their system prompts:

**Writer Agent** (`agents/writer.py`):
- Article length
- Writing style
- Code example requirements
- Target audience

**Image Agent** (`agents/image_gen.py`):
- Image style and aesthetics
- Color schemes
- Aspect ratio

**Publisher Agent** (`agents/publisher.py`):
- Default tags
- Publishing settings

### Swarm Parameters

Adjust swarm behavior in `main.py`:

```python
swarm = Swarm(
    [writer_agent, image_agent, publisher_agent],
    entry_point=writer_agent,
    max_handoffs=10,        # Maximum agent handoffs
    max_iterations=15,      # Maximum total iterations
    execution_timeout=600.0, # 10 minute timeout
    node_timeout=300.0       # 5 minute per-agent timeout
)
```

## Troubleshooting

### Common Issues

**"DEV_TO_API_KEY environment variable not set"**
- Solution: Add your Dev.to API key to `.env` file

**"AWS credentials not found"**
- Solution: Run `aws configure` or set AWS environment variables

**"Image upload failed"**
- Solution: Add ImgBB API key to `.env`, or continue without it (image will be saved locally)

**"Article generation timeout"**
- Solution: Increase `execution_timeout` in `main.py`
- Check your AWS Bedrock service limits

**Articles are too short/long**
- Solution: Modify the WRITER_SYSTEM_PROMPT in `agents/writer.py`
- Adjust the word count requirement in `main.py`

### Debug Mode

Enable detailed logging:

```python
# In main.py, change logging level
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Usage

### Custom Article Requirements

Modify the initial prompt in `main.py`:

```python
initial_prompt = f"""
Please write a comprehensive technical article for Dev.to on: {topic}

Requirements:
1. Target audience: Senior developers
2. Include 5+ code examples
3. Add a "Common Pitfalls" section
4. Include external references
5. 1500-2000 words
"""
```

### Using Different Models

Change the Bedrock model in agent definitions:

```python
model = BedrockModel(
    model_id="us.anthropic.claude-3-5-sonnet-20250222-v2:0",
    region_name="us-east-1"
)
```

### Batch Article Generation

Create multiple articles:

```bash
for topic in "FastAPI" "Docker" "Kubernetes"; do
    python main.py "$topic"
    sleep 60  # Wait between generations
done
```

## Dependencies

- **strands-agents**: Amazon Strands Agents SDK
- **boto3**: AWS SDK for Python
- **requests**: HTTP library
- **python-dotenv**: Environment variable management

See `requirements.txt` for complete list.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Amazon Strands Agents SDK](https://github.com/awslabs/amazon-strands)
- Powered by [Claude 3.5 Sonnet](https://www.anthropic.com/claude) via Amazon Bedrock
- Cover images generated with Stable Diffusion
- Published to [Dev.to](https://dev.to)

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

**Made with AI agents for AI-powered content creation** 🤖✨
