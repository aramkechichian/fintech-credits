# Fintech API

FastAPI application for fintech challenge.

## Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose (for containerized setup)

### Local Development

1. Install dependencies and run the application:
```bash
make up
```

This will:
- Install dependencies automatically
- Start MongoDB in Docker
- Run the FastAPI application

The API will be available at `http://localhost:8000`

**Alternative commands:**
- `make run` - Development mode with auto-reload (also starts MongoDB)
- `make down` - Stop the application and MongoDB

### Docker Setup

1. Build and start containers:
```bash
make docker-up
```

This will start:
- MongoDB on port 27017
- FastAPI on port 8000

2. Stop containers:
```bash
make docker-down
```

## Endpoints

- `GET /health` - Health check endpoint
- `GET /test` - Test endpoint to verify API is working

## Environment Variables

Create a `.env` file with:
```
MONGODB_URL=mongodb://localhost:27017
FINTECH_ENV=dev
```

## Testing

```bash
make test
```
