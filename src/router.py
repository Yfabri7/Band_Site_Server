from fastapi import APIRouter
from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import models, schemas, auth
from database import get_db, SessionLocal
import json


router = APIRouter()

# A set to track connected player WebSockets
connected_players = set()

# Admin search and song selection page
@router.get("/admin")
async def get_admin_page():
    return {"message": "Welcome to the admin page"}

# Placeholder for HTML (Player's Waiting Page)
@router.get("/player")
async def get_player():
    return {"status": "waiting", "message": "Waiting for next song..."}

# Search for songs by name in the PostgreSQL
@router.get("/search-song")
def search_song(input_song: str, db: Session = Depends(get_db)):
    results = db.query(models.Song).filter(models.Song.song_name.ilike(f"%{input_song}%")).all()
    return results

# Regular user Signup route
@router.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username, 
        hashed_password=hashed_password, 
        instrument=user.instrument, 
        is_admin=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Admin Signup route
# There is a better practice but time pressure made me go for a duplicated code
@router.post("/signupadmin", response_model=schemas.UserOut)
def admin_signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_admin = models.User(
        username=user.username,
        hashed_password=hashed_password,
        instrument=user.instrument,
        is_admin=True
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

# Login route
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "instrument": user.instrument,
        "is_admin": user.is_admin
    }

# WebSocket endpoint for admin to send song updates to players
@router.websocket("/ws/admin")
async def websocket_admin(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            check = await websocket.receive_text()
            print(f"THIS IS CHECK: {check}") # TODO DELETE
            if(check == "quit"):
                for player_ws in connected_players:
                    await player_ws.send_text("quit")
            else:  
                song_name = check
                print(song_name) # TODO DELETE
                db: Session = SessionLocal()
                song = db.query(models.Song).filter(models.Song.song_name.ilike(song_name)).first()
                db.close()
                
                if song:
                    song_data = json.loads(song.lyrics)
                    print(song_data) # TODO DELETE
                    for player_ws in connected_players:
                        await player_ws.send_text(json.dumps({
                            "action": "start_song",
                            "name": song.song_name.lower(),
                            "author": song.author,
                            "lyrics": song_data
                        }))
        except WebSocketDisconnect:
            print("Admin disconnected") # TODO DELETE
            break

# WebSocket endpoint for players to receive real-time song updates
@router.websocket("/ws/player")
async def websocket_player(websocket: WebSocket):
    await websocket.accept()
    connected_players.add(websocket)
    print("Player WebSocket connection accepted. Total players:", len(connected_players)) # TODO DELETE
    try:
        while True:
             data = await websocket.receive_text()
             print(data) # TODO DELETE
    except WebSocketDisconnect:
        connected_players.remove(websocket)
        print("Player disconnected. Total players:", len(connected_players)) # TODO DELETE