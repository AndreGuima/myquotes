# MyQuotes App

> 📝 Full-stack quotes application — FastAPI backend + React Native (Expo) frontend + MySQL + Pytest + Docker

<p align="center">
 <img src="https://img.shields.io/badge/python-3.13-blue" />
 <img src="https://img.shields.io/badge/fastapi-ready-brightgreen" />
 <img src="https://img.shields.io/badge/expo-react_native-blueviolet" />
 <img src="https://img.shields.io/badge/tests-pytest-success" />
 <img src="https://img.shields.io/badge/docker-compose-blue" />
</p>

## 📦 Stack

| Layer       | Technology                               |
| ----------- | ---------------------------------------- |
| Backend     | Python, FastAPI, SQLAlchemy, Pydantic V2 |
| Database    | MySQL (Docker)                           |
| Frontend    | Expo + React Native + Axios              |
| Testing     | Pytest + Testcontainers                  |
| Environment | Docker Compose + Venv                    |

---

## 🚀 Quick Start

### 🧠 Backend — API
Starting prod-like env

```bash
./scripts/start.sh
```

Starting dev mode env
```bash
docker compose up -d mysql # Sobe apenas o banco em docker
cd ~/MyQuotes
./backend/run-dev.sh
```
Run Tests
```bash
source backend/venv/bin/activate
pytest -v backend/tests/
```

Backend runs at: **[http://localhost:8000](http://localhost:8000)**
http://localhost:8000/docs

### 📱 Frontend — Expo

```bash
cd ~/MyQuotes/frontend
npx expo start --clear
```

Abra no celular com Expo Go ou via navegador:

📱 Mobile: escaneie o QR Code

💻 Web: http://localhost:8081


---

## 🧹 System Clean Up

| Action                  | Command                                 |
| ----------------------- | --------------------------------------- |
| Stop backend containers | `./scripts/stop.sh`                     |
| Clear Expo cache        | `cd frontend && npx expo start --clear` |
| Remove Docker leftovers | `docker system prune -f`                |

---

## ✅ Status

* CRUD quotes ✅
* Integration tests ✅
* Mobile + Web UI ✅
* Docker runtime ✅

---

Made with ❤️ and caffeine ☕

