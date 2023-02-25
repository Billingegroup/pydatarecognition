from pathlib import Path
import yaml
import os

from motor.motor_asyncio import AsyncIOMotorClient

filepath = Path(os.path.abspath(__file__))



# Connect to mongodb

with open(os.path.join(filepath.parent, 'secret_password.yml'), 'r') as f:
    user_secrets = yaml.safe_load(f)
username = user_secrets['username']
password = user_secrets['password']


class MongoClient():
    db_client: AsyncIOMotorClient = None

    async def get_db_client(self) -> AsyncIOMotorClient:
        """Return database client instance."""
        return self.db_client


    async def connect_db(self):
        """Create database connection."""
        self.db_client = AsyncIOMotorClient(
            f'mongodb+srv://{username}:{password}@cluster0.9bj1h.mongodb.net/?retryWrites=true&w=majority'
        #     f'mongodb+srv://{username}:{password}@sidewinder.uc5ro.mongodb.net/?retryWrites=true&w=majority'
         )

    async def close_mongo_connection(self):
        """Close database connection."""
        self.db_client.close()

mongo_client = MongoClient()
