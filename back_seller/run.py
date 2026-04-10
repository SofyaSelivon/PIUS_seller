import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

port = int(os.getenv("PORT", 8000))


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        reload=True
    )