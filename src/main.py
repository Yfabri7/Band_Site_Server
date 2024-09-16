from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from router import router
import json
import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Load the JSON files with song data
with open("hey_jude.json", 'r', encoding='utf-8') as hey_jude_file:
    hey_jude_data = json.load(hey_jude_file)

with open("veech_shelo.json", 'r', encoding='utf-8') as veech_shelo_file:
    veech_shelo_data = json.load(veech_shelo_file)

# Load the songs in DB
def load_songs():
    db: Session = SessionLocal()
    songs = [
        {"song_name": "Hey Jude", "author": "The Beatles", "lyrics": json.dumps(hey_jude_data)},
        {"song_name": "Veech Shelo", "author": "Ariel Zilber", "lyrics": json.dumps(veech_shelo_data)}
    ]
    for song in songs:
        # Check if the song already exists in the database
        existing_song = db.query(models.Song).filter_by(song_name=song['song_name'], author=song['author']).first()
        
        if existing_song:
            print(f"Song '{song['song_name']}' by '{song['author']}' already exists. Skipping.")
        else:
            # If the song does not exist, add it to the database
            db_song = models.Song(**song)
            db.add(db_song)
            print(f"Adding song '{song['song_name']}' by '{song['author']}' to the database.")
    
    db.commit()
    db.close()

class App:
    def __init__(self):
        self.app = FastAPI(title="MoveoBand", version="1.0.0")

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.app.include_router(router)

    async def run(self):
        config = uvicorn.Config(
            app=self.app,
            host="127.0.0.1",
            port=8000,
            lifespan="off",
            access_log=False)
        server = uvicorn.Server(config=config)
        await server.serve()


if __name__ == "__main__":
    load_songs()
    app = App()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.run())
    loop.close()