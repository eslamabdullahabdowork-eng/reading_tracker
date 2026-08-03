from fastapi import FastAPI,status,HTTPException
from .models import ReadState, BookState
import requests
import time
from .database import get_connection
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.get("/")
def welcome_user():
    return{"hello !": "welcome to my API !! go to / docs for interactive ui"}


@app.get("/search")
async def pull_books(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    r = None
    for attempt in range(3):
        try:
            r = requests.get('https://www.googleapis.com/books/v1/volumes?',
                              params={"q": q, "key": os.getenv("GOOGLE_BOOKS_API_KEY")},
                              timeout=5)
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt == 2:
                raise HTTPException(status_code=503, detail="Google Books API is unavailable right now")
            time.sleep(1)

    if r is None:
        raise HTTPException(status_code=503, detail="Google Books API is unavailable right now")

    if r.status_code == 404:
        raise HTTPException(status_code=404, detail=f"{q} was not found")
    elif r.status_code >= 500:
        raise HTTPException(status_code=503, detail="Google Books API failed. Please try again later.")

    return r.json()

@app.post("/books/{id}")
def add_book(id: str, read_state: BookState):
    if not id.strip():
        raise HTTPException(status_code=400, detail="Book id cannot be empty")
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM reading_state WHERE id = %s", (id,))
        existing = cur.fetchone()
        if existing:
            raise HTTPException(status_code=409, detail=f"Book with id {id} is already in your saved, if you want to change state try removing it first, or update the list by put button")

        r = None
        for attempt in range(3):
            try:
                r = requests.get(f'https://www.googleapis.com/books/v1/volumes/{id}',
                                  params={"key": os.getenv("GOOGLE_BOOKS_API_KEY")},
                                  timeout=5)
                break
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if attempt == 2:
                    raise HTTPException(status_code=503, detail="Google Books API is unavailable right now")
                time.sleep(1)

        if not r:
            raise HTTPException(status_code=404, detail=f"No book found on Google Books with id {id}")

        book_data = r.json()
        title = book_data["volumeInfo"]["title"]
        description = book_data["volumeInfo"].get("description", "")

        cur.execute("INSERT INTO reading_state (id, title, description, read_state) VALUES (%s, %s, %s, %s)",
                     (id, title, description, read_state.reading_state))
        conn.commit()
        return {"book added": title}
    finally:
        cur.close()
        conn.close()

@app.put("/books/{id}")
def update_book(id: str, read_state: BookState):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE reading_state SET read_state = %s WHERE id = %s",
                     (read_state.reading_state, id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"No book found with id {id}")
        conn.commit()
        return {"book updated to": read_state.reading_state}
    finally:
        cur.close()
        conn.close()

@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM reading_state WHERE id = %s", (id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"No book found with id {id}")
        conn.commit()
        return
    finally:
        cur.close()
        conn.close()

@app.get("/books/saved")
def get_books(state: ReadState | None = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if state:
            cur.execute("SELECT * FROM reading_state WHERE read_state = %s", (state,))
        else:
            cur.execute("SELECT * FROM reading_state")
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()