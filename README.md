# CyberSec AI Bot

A comprehensive cybersecurity AI assistant with Telegram integration, web search capabilities, and name/person search functionality.

## Features

- **AI-Powered Cybersecurity Assistant**: Answers cybersecurity questions using OpenAI's GPT models
- **Telegram Bot Integration**: Access the AI assistant through a Telegram bot
- **Dataset Learning**: Upload cybersecurity datasets for the AI to learn from
- **Web Search**: Search the internet for cybersecurity information
- **Person/Name Search**: Find detailed information about individuals across various sources
- **User-Friendly Dashboard**: Monitor system status and manage all features through a clean web interface

## Getting Started

### Prerequisites

- OpenAI API key (for AI capabilities)
- Telegram Bot token (for Telegram integration)

### Setup

1. **Access the Dashboard**: Navigate to the web interface
2. **Configure API Keys**:
   - Go to the "Configuration" tab
   - Enter your OpenAI API key
   - Enter your Telegram Bot token

### Using the Application

#### Uploading Datasets

1. Navigate to the "Dataset Management" tab
2. Fill in the dataset name and description
3. Upload your dataset file
4. The system will process the dataset automatically

#### Using the Search Engine

1. Navigate to the "Search Engine" tab
2. Choose between "Web Search" or "Person Search"
3. Enter your query
4. View the results displayed on the page

#### Using the Telegram Bot

Once configured, you can interact with the Telegram bot using:

- `/start` - Start the bot
- `/help` - Get help information
- `/search [query]` - Search for information
- Or simply send a message with your cybersecurity question

To search for a person, send a message with the format:
```
name: John Smith
```
or
```
person: John Smith
```

## Technical Details

### Architecture

- **Frontend**: React with Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **External APIs**: OpenAI, Telegram Bot API, DuckDuckGo Search

### API Endpoints

- `/api/status` - Get system status
- `/api/datasets` - Get all uploaded datasets
- `/api/dataset/upload` - Upload a new dataset
- `/api/search/web` - Perform a web search
- `/api/search/person` - Search for information about a person
- `/api/chat` - Send a message to the AI assistant
- `/api/config/telegram` - Configure Telegram bot token
- `/api/config/openai` - Configure OpenAI API key

## Learning Capabilities

The AI assistant has the following learning capabilities:

1. **Dataset Learning**: Upload your cybersecurity datasets to train the AI
2. **Continuous Web Learning**: The assistant can search the web for the latest information
3. **Conversation Memory**: The system remembers past interactions to provide more relevant responses

## Privacy and Security

- All sensitive configurations (API keys, tokens) are stored securely
- Search queries and results are saved in the database for reference but can be cleared
- Communications with external APIs are encrypted
