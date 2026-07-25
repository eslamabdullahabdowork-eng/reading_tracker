# 📚 Reading Tracker API

A RESTful API for tracking your personal reading list — search for books, add them to your list, and track your reading progress.

🔗 **Live API docs:** https://readingtracker-production.up.railway.app/docs

## Features

- 🔍 Search books via the Google Books API
- ➕ Add books to your personal reading list
- 📖 View your saved books
- ✏️ Update reading status (e.g. want to read, reading, finished)
- 🗑️ Remove books from your list

## Tech Stack

- **Language:** Python
- **Framework:** FastAPI
- **Database:** PostgreSQL (raw SQL via psycopg2 — no ORM)
- **External API:** Google Books API
- **Deployment:** Railway

## Why no ORM?

Queries are written in raw SQL to build a solid understanding of how the API layer talks to the database — full control over queries, indexing, and performance. An ORM layer is planned as the project grows.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books/search` | Search for books via Google Books API |
| GET | `/books` | Get all saved books |
| POST | `/books` | Add a new book to your list |
| PUT | `/books/{id}` | Update a book's reading status |
| DELETE | `/books/{id}` | Remove a book from your list |

## Running Locally

\`\`\`bash
# clone the repo
git clone https://github.com/eslamabdullahabdowork-eng/reading_tracker.git
cd reading_tracker

# install dependencies
pip install -r requirements.txt

# set environment variables (.env)
# DATABASE_URL=your_postgres_connection_string
# GOOGLE_BOOKS_API_KEY=your_api_key

# run the server
uvicorn app.main:app --reload
\`\`\`

## Roadmap

- [ ] User authentication (multi-user support)
- [ ] Migrate to an ORM (SQLAlchemy)
- [ ] Book reviews / ratings
- [ ] Categories & tags

---

Built as a hands-on project to learn backend development — API design, PostgreSQL, and deployment.
