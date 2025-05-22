from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
import uuid
import json
import re
import time
import requests
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import openai
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import shutil

# Setup paths and environment variables
ROOT_DIR = Path(__file__).parent
DATASET_DIR = ROOT_DIR / "datasets"
DATASET_DIR.mkdir(exist_ok=True)

load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize API keys and tokens
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create collections
conversations = db.conversations
search_results = db.search_results
datasets = db.datasets
user_profiles = db.user_profiles

# Initialize OpenAI client if API key is available
openai_client = None
if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Telegram bot instance
telegram_bot = None
if TELEGRAM_BOT_TOKEN:
    telegram_bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class DatasetUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    file_path: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "uploaded"
    
class DatasetUploadCreate(BaseModel):
    name: str
    description: str

class SearchQuery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None
    
class NameSearchQuery(BaseModel):
    name: str
    
class WebSearchQuery(BaseModel):
    query: str
    
class MessageData(BaseModel):
    message: str
    
class TelegramConfig(BaseModel):
    token: str
    
class OpenAIConfig(BaseModel):
    api_key: str

# Utility Functions
async def process_dataset(dataset_id: str, file_path: str):
    """Process uploaded dataset in the background"""
    try:
        # Update status to processing
        await datasets.update_one(
            {"id": dataset_id}, 
            {"$set": {"status": "processing"}}
        )
        
        # Simulate processing (in a real app, you'd analyze the dataset here)
        await asyncio.sleep(2)
        
        # Update status to complete
        await datasets.update_one(
            {"id": dataset_id}, 
            {"$set": {"status": "complete"}}
        )
        
        logger.info(f"Dataset {dataset_id} processed successfully")
    except Exception as e:
        # Update status to failed
        await datasets.update_one(
            {"id": dataset_id}, 
            {"$set": {"status": "failed", "error": str(e)}}
        )
        logger.error(f"Error processing dataset {dataset_id}: {str(e)}")

async def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """Search the web using DuckDuckGo"""
    results = []
    try:
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(query, max_results=max_results)]
            results = search_results
    except Exception as e:
        logger.error(f"Error searching web: {str(e)}")
    return results

async def get_llm_response(prompt: str) -> str:
    """Get response from OpenAI API"""
    if not openai_client:
        return "OpenAI API key not configured."
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return f"Error: {str(e)}"

async def person_search(name: str) -> Dict[str, Any]:
    """Search for information about a person"""
    results = {}
    
    # Search web for the person
    web_results = await web_search(f"{name} profile information", 10)
    
    # Extract relevant information (in a real app, you'd use more sophisticated extraction)
    social_profiles = []
    professional_info = []
    
    for result in web_results:
        title = result.get('title', '').lower()
        if 'linkedin' in title or 'github' in title or 'twitter' in title or 'facebook' in title:
            social_profiles.append(result)
        else:
            professional_info.append(result)
    
    results = {
        "name": name,
        "social_profiles": social_profiles[:3],
        "professional_info": professional_info[:5],
        "raw_results": web_results
    }
    
    return results

# Telegram Bot Handlers
async def start_telegram_bot():
    """Initialize and start the Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not configured")
        return
    
    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("search", search_command))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logger.info("Telegram bot started successfully")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {str(e)}")

async def start_command(update, context):
    """Handle /start command"""
    await update.message.reply_text(
        "Welcome to the Cybersecurity AI Assistant! I can help you with cybersecurity questions, analyze datasets, and search for information.\n\n"
        "Commands:\n"
        "/help - Show available commands\n"
        "/search [query] - Search for information\n"
        "Or just send me a message with your cybersecurity question!"
    )

async def help_command(update, context):
    """Handle /help command"""
    await update.message.reply_text(
        "Here's what I can do for you:\n\n"
        "1. Answer cybersecurity questions\n"
        "2. Search for information about a person or topic\n"
        "3. Learn from datasets you upload through the web interface\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/search [query] - Search for information\n"
        "Or just send me a message with your question!"
    )

async def search_command(update, context):
    """Handle /search command"""
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Please provide a search query. Example: /search vulnerability in Windows 11")
        return
    
    await update.message.reply_text(f"Searching for: {query}...")
    
    # Perform web search
    results = await web_search(query)
    
    if results:
        response = "Here's what I found:\n\n"
        for i, result in enumerate(results[:3], 1):
            response += f"{i}. {result.get('title', 'No title')}\n"
            response += f"   {result.get('body', 'No description')[:100]}...\n"
            response += f"   {result.get('href', 'No link')}\n\n"
    else:
        response = "I couldn't find any relevant information for your query."
    
    await update.message.reply_text(response)
    
    # Save search in database
    search_data = {
        "id": str(uuid.uuid4()),
        "user_id": update.effective_user.id,
        "query": query,
        "results": results,
        "timestamp": datetime.utcnow()
    }
    await search_results.insert_one(search_data)

async def handle_message(update, context):
    """Handle regular text messages"""
    user_text = update.message.text
    user_id = update.effective_user.id
    
    # Check if it's a name search
    if user_text.startswith("name:") or user_text.startswith("person:"):
        name = user_text.split(":", 1)[1].strip()
        await update.message.reply_text(f"Searching for information about: {name}...")
        
        person_info = await person_search(name)
        
        response = f"Information about {name}:\n\n"
        
        if person_info["social_profiles"]:
            response += "Social Profiles:\n"
            for profile in person_info["social_profiles"]:
                response += f"- {profile.get('title', 'Profile')}: {profile.get('href', 'No link')}\n"
            response += "\n"
        
        if person_info["professional_info"]:
            response += "Professional Information:\n"
            for info in person_info["professional_info"][:2]:
                response += f"- {info.get('title', 'Information')}\n"
                response += f"  {info.get('body', 'No details')[:100]}...\n\n"
        
        await update.message.reply_text(response)
        return
    
    # Otherwise treat as a cybersecurity question
    await update.message.reply_text("Thinking about your question...")
    
    # Get AI response
    if openai_client:
        ai_response = await get_llm_response(user_text)
    else:
        # Fallback if no OpenAI API key
        ai_response = "I need my AI capabilities to be configured to answer this properly. Please set up an OpenAI API key."
    
    await update.message.reply_text(ai_response)
    
    # Save conversation to database
    conversation_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "message": user_text,
        "response": ai_response,
        "timestamp": datetime.utcnow()
    }
    await conversations.insert_one(conversation_data)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Cybersecurity AI Assistant API"}

@api_router.get("/status")
async def get_status():
    status = {
        "app": "running",
        "telegram_bot": "configured" if TELEGRAM_BOT_TOKEN else "not configured",
        "openai": "configured" if OPENAI_API_KEY else "not configured",
        "database": "connected" if db else "not connected"
    }
    return status

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status/checks", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/dataset/upload")
async def upload_dataset(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...)
):
    # Generate unique ID for dataset
    dataset_id = str(uuid.uuid4())
    
    # Create file path
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    file_path = f"{DATASET_DIR}/{dataset_id}.{file_extension}"
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create dataset record
    dataset = DatasetUpload(
        id=dataset_id,
        name=name,
        description=description,
        file_path=file_path
    )
    
    # Save to database
    await datasets.insert_one(dataset.dict())
    
    # Process dataset in background
    background_tasks.add_task(process_dataset, dataset_id, file_path)
    
    return {"id": dataset_id, "name": name, "status": "uploaded"}

@api_router.get("/datasets")
async def get_datasets():
    all_datasets = await datasets.find().to_list(1000)
    return all_datasets

@api_router.post("/search/web")
async def search_web_api(query: WebSearchQuery):
    results = await web_search(query.query)
    
    # Save search in database
    search_data = {
        "id": str(uuid.uuid4()),
        "query": query.query,
        "results": results,
        "timestamp": datetime.utcnow()
    }
    await search_results.insert_one(search_data)
    
    return {"query": query.query, "results": results}

@api_router.post("/search/person")
async def search_person_api(query: NameSearchQuery):
    results = await person_search(query.name)
    
    # Save search in database
    search_data = {
        "id": str(uuid.uuid4()),
        "query": f"Person: {query.name}",
        "results": results,
        "timestamp": datetime.utcnow()
    }
    await search_results.insert_one(search_data)
    
    return results

@api_router.post("/chat")
async def chat_api(message_data: MessageData):
    if not openai_client:
        return {"error": "OpenAI API key not configured"}
    
    ai_response = await get_llm_response(message_data.message)
    
    # Save conversation to database
    conversation_data = {
        "id": str(uuid.uuid4()),
        "message": message_data.message,
        "response": ai_response,
        "timestamp": datetime.utcnow()
    }
    await conversations.insert_one(conversation_data)
    
    return {"response": ai_response}

@api_router.post("/config/telegram")
async def configure_telegram(config: TelegramConfig):
    global TELEGRAM_BOT_TOKEN, telegram_bot
    
    try:
        # Validate token by creating a temporary bot
        temp_bot = telegram.Bot(token=config.token)
        await temp_bot.get_me()
        
        # Token is valid, update the .env file
        env_path = ROOT_DIR / '.env'
        with open(env_path, 'r') as file:
            env_content = file.read()
        
        # Replace token in env file
        if 'TELEGRAM_BOT_TOKEN' in env_content:
            env_content = re.sub(
                r'TELEGRAM_BOT_TOKEN=".*?"', 
                f'TELEGRAM_BOT_TOKEN="{config.token}"', 
                env_content
            )
        else:
            env_content += f'\nTELEGRAM_BOT_TOKEN="{config.token}"'
        
        with open(env_path, 'w') as file:
            file.write(env_content)
        
        # Update global variables
        TELEGRAM_BOT_TOKEN = config.token
        telegram_bot = temp_bot
        
        # Start the bot in the background
        asyncio.create_task(start_telegram_bot())
        
        return {"status": "success", "message": "Telegram bot configured successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to configure Telegram bot: {str(e)}"}

@api_router.post("/config/openai")
async def configure_openai(config: OpenAIConfig):
    global OPENAI_API_KEY, openai_client
    
    try:
        # Validate API key by creating a temporary client
        temp_client = openai.OpenAI(api_key=config.api_key)
        # Make a simple API call to validate
        temp_client.models.list()
        
        # API key is valid, update the .env file
        env_path = ROOT_DIR / '.env'
        with open(env_path, 'r') as file:
            env_content = file.read()
        
        # Replace API key in env file
        if 'OPENAI_API_KEY' in env_content:
            env_content = re.sub(
                r'OPENAI_API_KEY=".*?"', 
                f'OPENAI_API_KEY="{config.api_key}"', 
                env_content
            )
        else:
            env_content += f'\nOPENAI_API_KEY="{config.api_key}"'
        
        with open(env_path, 'w') as file:
            file.write(env_content)
        
        # Update global variables
        OPENAI_API_KEY = config.api_key
        openai_client = temp_client
        
        return {"status": "success", "message": "OpenAI API configured successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to configure OpenAI API: {str(e)}"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Start the Telegram bot if token is configured
    if TELEGRAM_BOT_TOKEN:
        asyncio.create_task(start_telegram_bot())
    else:
        logger.warning("Telegram bot not started: Token not configured")
    
    # Log OpenAI configuration status
    if OPENAI_API_KEY:
        logger.info("OpenAI API configured")
    else:
        logger.warning("OpenAI API not configured")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
