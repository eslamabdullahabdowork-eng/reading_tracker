from fastapi import FastAPI,status,HTTPException
from pydantic import BaseModel
from enum import Enum
import requests
from database import get_connection
import os
from dotenv import load_dotenv
from models import ReadState, BookState

load_dotenv()

app = FastAPI()



# this for getting books from google api:
@app.get("/search")
async def pull_books(q: str):
    r = requests.get('https://www.googleapis.com/books/v1/volumes?', params={"q" : q,"key":os.getenv("GOOGLE_BOOKS_API_KEY")} )
    response_dic = r.json()
    return response_dic

@app.get("/books") # what this endpoint for?
def get_books(read_state: ReadState | None = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if read_state:
            cur.execute("SELECT * FROM reading_state WHERE read_state = %s", (read_state,))
        else:
            cur.execute("SELECT * FROM reading_state")
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()

@app.post("/books/{id}")
def add_book(id: str, read_state : BookState):
    r = requests.get(f'https://www.googleapis.com/books/v1/volumes/{id}',
                      params={"key": os.getenv("GOOGLE_BOOKS_API_KEY")})
    book_data = r.json()
    title = book_data["volumeInfo"]["title"]
    description = book_data["volumeInfo"].get("description", "")
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO reading_state (id, title, description, read_state) VALUES (%s, %s, %s, %s)",
    (id, title, description, read_state.reading_state))
        conn.commit()
        return {"data": "book added"}
    finally:
        cur.close()
        conn.close()


@app.put("/books/{id}")
def update_book(id: str , read_state : BookState):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE reading_state SET read_state = %s WHERE id = %s",
        (read_state.reading_state, id)
        )
        conn.commit()
        return {"book updated to": read_state}
    finally:
        cur.close()
        conn.close()


@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM reading_state WHERE id = %s",
        (id,)
        )
        conn.commit()
        return
    finally:
        cur.close()
        conn.close()