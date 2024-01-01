from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI()

# Set debug mode
debug = True

# List of allowed origins for CORS
origins = [
    "http://localhost.com",
    "https://localhost.com",
    "http://localhost",
    "http://localhost:3001",
    "http://sokaris.link:3001",
    "http://sokaris.link",
    "http://assistant.sokaris.link",
    "https://fr.sokaris.link",
    "http://fr.sokaris.link",
    "http://localhost:3008",
    "https://localhost:3008",
    "http://127.0.0.1:3008",
    "http://fr.sokaris.link",
    "http://127.0.0.1:3001",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins to allow
    allow_credentials=True,  # Allow credentials
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allow methods
    allow_headers=["*"],  # Allow all headers
)