from app import app  # Import the FastAPI instance from the app module
from routes import router  # Import the router from the routes module

@app.get("/")  # Define a route for the root URL ("/")
async def read_root() -> dict:  # This function is a coroutine (async) and it returns a dictionary
    return {"Hello"}  # Return a dictionary

app.include_router(router)  # Include the routes defined in the router