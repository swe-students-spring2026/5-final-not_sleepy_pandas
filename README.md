# PennyWise

[![Backend CI](https://github.com/swe-students-spring2026/5-final-not_sleepy_pandas/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-not_sleepy_pandas/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/swe-students-spring2026/5-final-not_sleepy_pandas/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-not_sleepy_pandas/actions/workflows/frontend-ci.yml)
[![Database CI](https://github.com/swe-students-spring2026/5-final-not_sleepy_pandas/actions/workflows/database-ci.yml/badge.svg)](https://github.com/swe-students-spring2026/5-final-not_sleepy_pandas/actions/workflows/database-ci.yml)

## Overview

A personal finance tracker that helps users manage their money by tracking income and expenses, visualizing spending trends with interactive charts, and setting budgets.

## Features

- Track income and expense transactions
- Visualize monthly summaries, spending trends, and top categories
- Set per-category budgets and monitor spending against limits
- User registration and JWT-based authentication

---

## Team

- [Harry Wu](https://github.com/harrywzl)
- [Tuo Zhang](https://github.com/TuoZhang0902)
- [Claire Wu](https://github.com/clairewwwwww)
- [Karen Maza](https://github.com/KarenMazaDelgado)
- [Hanson Huang](https://github.com/Hansonhzh)

---

## Live Deployment

- [Web App](http://YOUR_DROPLET_IP:3000)

Deployed on DigitalOcean via Docker Hub images and GitHub Actions CI/CD.

---

## Docker Hub Images

- [Backend](https://hub.docker.com/r/YOUR_USERNAME/pennywise-backend)
- [Frontend](https://hub.docker.com/r/YOUR_USERNAME/pennywise-frontend)
- [Database](https://hub.docker.com/r/YOUR_USERNAME/pennywise-database)

---

## Option 1: Quick Start (Recommended)

### Prerequisites

- Docker Desktop installed and running

### Run the full system

```bash
docker compose up --build
```

Optional (background mode):

```bash
docker compose up --build -d
```

Stop everything:

```bash
docker compose down
```

Stop everything and remove volumes:

```bash
docker compose down -v
```

---

## Access the Services

- Frontend → http://localhost:3000
- Backend API → http://localhost:5001
- MongoDB → localhost:27017

---

## Option 2: Run Locally Without Docker (for Development)

### 1. Start MongoDB

```bash
docker run --name pennywise-mongo -p 27017:27017 -d mongo:7
```

### 2. Setup Backend

```bash
pipenv install --dev
pipenv shell
```

Set environment variables:

```bash
export MONGO_URI=mongodb://localhost:27017
export MONGO_DB_NAME=pennywise
export JWT_SECRET=dev-secret
```

Run:

```bash
python -m backend.app
```

### 3. Setup Frontend

```bash
pip install -r frontend/requirements.txt
```

Set environment variables:

```bash
export BACKEND_URL=http://localhost:5000
export FLASK_SECRET=dev-frontend-secret
```

Run:

```bash
cd frontend
python app.py
```

### 4. Seed the Database (optional)

```bash
pip install pymongo python-dotenv bcrypt
python database/seed.py
```



