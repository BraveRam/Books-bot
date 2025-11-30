import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
ADMINS_ID = [int(admin_id) for admin_id in os.getenv("ADMINS_ID", "").split(",") if admin_id.strip()] 
