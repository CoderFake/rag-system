# RAG System

A Retrieval Augmented Generation (RAG) system with a beautiful React + Vite frontend and Flask backend.

## Features

- Chat functionality for anonymous users, registered users, and admins
- User authentication (login/register)
- Chat history for registered users
- Knowledge base management for admins
- Multilingual support (Vietnamese and English)
- Responsive design for all devices
- Dark/light theme support

## Tech Stack

### Frontend
- React 18
- TypeScript
- Vite
- Material-UI
- React Router
- i18next for internationalization
- Axios for API requests
- PM2 for production deployment

### Backend
- Flask
- JWT authentication
- ChromaDB for vector storage
- Gemini API for LLM
- MySQL database

## Development

### Prerequisites

- Node.js 16+
- Python 3.9+
- MySQL 8.0+
- Docker and Docker Compose (optional)

### Running with Docker

The easiest way to run the application is using Docker Compose:

```bash
# Build and run with Docker Compose
docker-compose up -d
```

This will start:
- MySQL database on port 3386
- Backend API on port 6868
- Frontend on port 3000

### Running Locally

#### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create a `.env` file in the root directory with the necessary variables for both frontend and backend.

## Project Structure

- `frontend/`: React + Vite frontend application
- `backend/`: Flask backend API
- `mysql/`: MySQL initialization scripts
