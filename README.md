# Nexus — AI-Augmented Project Management Platform

A full-stack project management platform where an NLP model automatically assigns priority scores to tasks based on their descriptions. Built with FastAPI, PostgreSQL, React, Docker, and deployed on AWS EC2.

---

## Features

- **User Authentication** — Register and login with JWT tokens and bcrypt password hashing
- **Project Management** — Create and manage multiple projects per user
- **AI Task Prioritization** — NLP model reads task descriptions and automatically assigns Low / Medium / High / Critical priority
- **REST API** — Full CRUD API with auto-generated Swagger docs at `/docs`
- **Containerized** — Entire stack runs with a single `docker compose up`
- **CI/CD** — Auto-deploys to AWS EC2 on every push to `main` via GitHub Actions
- **Load Tested** — Validated under 500 concurrent users using Locust

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | PostgreSQL + SQLAlchemy |
| Authentication | JWT tokens + bcrypt |
| NLP | HuggingFace Transformers (keyword-based priority scoring) |
| Frontend | React + Tailwind CSS + Vite |
| Containerization | Docker + Docker Compose |
| Deployment | AWS EC2 (Ubuntu) |
| CI/CD | GitHub Actions |
| Load Testing | Locust |

---

## Project Structure

```
nexus/
├── app/
│   ├── main.py               # FastAPI app entrypoint
│   ├── database.py           # SQLAlchemy engine and session
│   ├── models/
│   │   └── models.py         # User, Project, Task ORM models
│   ├── routers/
│   │   ├── auth.py           # /auth/register, /auth/login, /auth/me
│   │   ├── projects.py       # CRUD for projects
│   │   └── tasks.py          # CRUD for tasks + NLP priority scoring
│   └── core/
│       └── security.py       # JWT + bcrypt utilities
├── nexus-frontend/           # React frontend
│   └── src/
│       └── App.jsx           # Single-page app (login, projects, tasks)
├── Dockerfile                # Backend container
├── docker-compose.yml        # Backend + PostgreSQL services
├── locustfile.py             # Load test (500 concurrent users)
├── .github/
│   └── workflows/
│       └── deploy.yml        # GitHub Actions CI/CD pipeline
└── requirements.txt
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL
- Docker (optional)

### Run Locally (without Docker)

**1. Clone the repo**
```bash
git clone https://github.com/Sanjay180803/Nexus.git
cd Nexus
```

**2. Set up Python environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

**3. Configure environment**
```bash
# Create .env file
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/taskmanager
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

**4. Create the database**
```bash
psql -U postgres
CREATE DATABASE taskmanager;
\q
```

**5. Start the backend**
```bash
uvicorn app.main:app --reload
```

**6. Start the frontend**
```bash
cd nexus-frontend
npm install
npm run dev
```

Visit `http://localhost:5173` for the app or `http://localhost:8000/docs` for the API.

---

### Run with Docker

```bash
docker compose up --build
```

API available at `http://localhost:8000`

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create a new account |
| POST | `/auth/login` | Login and receive JWT token |
| GET | `/auth/me` | Get current user info |

### Projects
| Method | Endpoint | Description |
|---|---|---|
| POST | `/projects/` | Create a project |
| GET | `/projects/` | List all your projects |
| GET | `/projects/{id}` | Get a single project |

### Tasks
| Method | Endpoint | Description |
|---|---|---|
| POST | `/tasks/{project_id}/tasks` | Create task (AI assigns priority) |
| GET | `/tasks/{project_id}/tasks` | List all tasks in a project |
| PATCH | `/tasks/{project_id}/tasks/{task_id}` | Update a task |

---

## AI Priority Scoring

When a task is created, the description is analyzed and automatically assigned one of four priority levels:

| Priority | Example keywords |
|---|---|
| Critical | crash, down, security, breach, emergency |
| High | bug, error, broken, fail, fix |
| Medium | update, improve, feature, add |
| Low | everything else |

Example:
```json
{
  "title": "Server is down",
  "description": "Production database crashed, all users locked out"
}
```
Response: `"priority": "critical"`

---

## Deployment

The app is deployed on AWS EC2. Every push to `main` triggers the GitHub Actions workflow which:
1. SSHs into the EC2 instance
2. Pulls the latest code
3. Rebuilds the Docker container
4. Restarts the service

---

## Load Testing

Run Locust to simulate 500 concurrent users:

```bash
pip install locust
locust -f locustfile.py --host=http://your-server-ip:8000
```

Open `http://localhost:8089`, set 500 users, ramp up 10/second, click Start.

---

## Resume Bullets

- Built AI-augmented project management platform using FastAPI and PostgreSQL, integrating NLP model for automatic task prioritization across user-created workflows
- Designed JWT authentication system with bcrypt password hashing supporting multi-user project and task management
- Containerized application with Docker and deployed on AWS EC2 with automated CI/CD pipeline via GitHub Actions
- Validated system performance under 500 concurrent users using Locust load testing framework
