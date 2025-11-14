# Podalirius — FastAPI Healthcare Scheduling System

A web application that allows patients to schedule and manage medical appointments
Built with **FastAPI**, **MySQL** and **Redis**, featuring JWT-based authentication and layered architecture

---

## Tech Stack
- **Backend**: Python, FastAPI, SQLModel, MySQL, Redis
- **Frontend**: HTML, Jinja2, JavaScript (vanilla)
- **Validation**: Pydantic
- **Authentication**: jose
- **Testing**: Pytest, FastAPI test client and HTTPie
- **Deployment**: Docker, uv (project manager)

### Libraries
- Redis
- FastAPI
- Pytest
- HTTPie
- Uvicorn
- python-jose
- passlib
- python-dotenv
- sqlmodel
- PyMySQL
- cryptography
- pydantic-settings
- httpx
- fastapi-utils
- typing-inspect
- python-multipart
- Jinja2
- beautifulsoup4

---

## Architecture Overview
The application follows a layered architecture:
- **Web** — Top level where router functions are placed, interact with a user through frontend
- **Service** — Middle level where buisness logic and data preparation are placed
- **Data** — Bottom level where ORM interfaces for CRUD operations and database connection functions are placed
- **Model** — An additional layer which binds all other layers and defines a structure of the project's data

---

## Features
- Docker composed image collecting **FastAPI** application, **MySQL** and **Redis** images
- Custom **JWT-based** authentication system with one-time-password flow
- Integration and unit tests using **Pytest**
- Normalized database architecture

---

## Setup
```bash
git clone https://github.com/Eleverkuhn/Podalirius
cd podalirius
docker compose up --build
pytest -q
```
Visit [localhost](http://localhost:8000)
