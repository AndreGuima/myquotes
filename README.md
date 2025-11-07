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

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v   # ✅ ensure tests pass
cd ..
./scripts/start.sh # start prod-like env
```

Backend runs at: **[http://localhost:8000](http://localhost:8000)**

### 📱 Frontend — Expo

```bash
cd frontend
npm install
npx expo start --clear
```

Web: [http://localhost:8081](http://localhost:8081)
Mobile: open Expo Go & scan QR code

### 🌐 Environment Variables

Create files like:

`.env`

```
API_URL=http://localhost:8000
```

`.env.development`

```
API_URL=http://YOUR_LOCAL_IP:8000
```

> ℹ️ For Android device testing, backend **cannot** be `localhost`

---

## 🧪 Run Tests (Backend)

```bash
cd backend
source venv/bin/activate
pytest -v
```

---

## 🧹 System Clean Up

| Action                  | Command                                 |
| ----------------------- | --------------------------------------- |
| Stop backend containers | `./scripts/stop.sh`                     |
| Clear Expo cache        | `cd frontend && npx expo start --clear` |
| Remove Docker leftovers | `docker system prune -f`                |

---

## 📁 Project Structure

```
MyQuotes/
 ├── backend/         # FastAPI + MySQL
 ├── frontend/        # Expo app
 ├── database/
 ├── scripts/
 └── docker-compose.yml
```

---

## ✅ Status

* CRUD quotes ✅
* Integration tests ✅
* Mobile + Web UI ✅
* Docker runtime ✅

---

## 🛣️ Roadmap

* 🔐 Auth (JWT)
* 🌍 Deploy backend (Railway / Render)
* 📱 Publish mobile app
* 🧪 GitHub Actions CI

---

## 🤝 Contributing

Pull requests welcome.

---

## 📝 License

MIT — use freely, build better!

---

Made with ❤️ and caffeine ☕

