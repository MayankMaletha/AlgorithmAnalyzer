# Algorithm Visualizer — Backend

FastAPI backend that powers step-by-step DSA visualization with Gemini AI explanations.

## 🚀 Quick Start

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # Fill in your API keys
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for interactive API docs.

---

## 📁 Project Structure

```
backend/
├── main.py                    # App entry point
├── requirements.txt
├── .env
├── algorithms/
│   ├── sorting.py             # Bubble, Selection, Insertion, Merge, Quick, Heap
│   ├── searching.py           # Linear Search, Binary Search
│   ├── graph.py               # BFS, DFS, Dijkstra, Bellman-Ford, Kruskal, Prim
│   └── dp.py                  # Fibonacci, 0/1 Knapsack, LCS, LIS
├── models/
│   └── requests.py            # Pydantic request/response models
├── routes/
│   ├── algorithms.py          # REST endpoints
│   ├── ai.py                  # Gemini AI endpoints
│   └── websocket.py           # Real-time WebSocket streaming
├── services/
│   └── gemini_service.py      # Google Gemini integration
└── utils/
    └── step_engine.py         # Universal Step format (core concept)
```

---

## 🔌 API Endpoints

### Algorithms
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/algorithm/list` | All available algorithms |
| GET | `/algorithm/{name}/complexity` | Time/space complexity |
| POST | `/algorithm/run` | Run sorting algorithm |
| POST | `/search/run` | Run searching algorithm |
| POST | `/graph/run` | Run graph algorithm |
| POST | `/dp/run` | Run DP algorithm |

### AI (requires GEMINI_API_KEY)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/ai/explain` | Full algorithm explanation |
| POST | `/ai/step-explain` | Explain a specific step |
| POST | `/ai/code` | Generate code in any language |

### WebSocket
```
ws://localhost:8000/ws/algorithm
```

---

## 📦 Step Engine Format

Every algorithm returns a list of `Step` objects:

```json
{
  "type": "compare | swap | visit | update | select | found | not_found | complete",
  "description": "Human-readable explanation",
  "indices": [0, 1],
  "array": [64, 25, 12, 22, 11],
  "extra": {}
}
```

This unified format means the frontend animates **all** algorithms with the same logic.

---

## 📡 WebSocket Usage

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/algorithm');

ws.send(JSON.stringify({
  type: "sort",
  algorithm: "bubble_sort",
  array: [64, 34, 25, 12, 22, 11, 90],
  delay_ms: 300   // ms between steps (0-2000)
}));

ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  // msg.type: "start" | "step" | "done" | "error"
  if (msg.type === "step") {
    animateStep(msg.data);   // msg.step_index, msg.total_steps
  }
};
```

---

## 🧪 Example Requests

### Sorting
```bash
curl -X POST http://localhost:8000/algorithm/run \
  -H "Content-Type: application/json" \
  -d '{"algorithm": "merge_sort", "array": [38, 27, 43, 3, 9, 82, 10]}'
```

### Graph (Dijkstra)
```bash
curl -X POST http://localhost:8000/graph/run \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "dijkstra",
    "graph": {
      "0": [["1", 4], ["2", 1]],
      "1": [["3", 1]],
      "2": [["1", 2], ["3", 5]],
      "3": []
    },
    "start": "0"
  }'
```

### AI Explain
```bash
curl -X POST http://localhost:8000/ai/explain \
  -H "Content-Type: application/json" \
  -d '{"algorithm": "quick_sort"}'
```

---

## 🏗️ Architecture Overview

```
┌────────────────────────────┐
│      Frontend (HTML/JS)    │
└────────────┬───────────────┘
             │ WebSocket
             ▼
┌────────────────────────────┐
│       FastAPI Backend      │
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│     WebSocket Router       │
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│   Algorithm Dispatcher     │
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│   Algorithm Modules        │
│ (sorting, graph, dp, etc.) │
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│       Step Engine          │
└────────────┬───────────────┘
             ▼
      Stream Steps → Frontend
```

## 🔄 Data Flow
User Input → Frontend → WebSocket → Backend
        ↓
Algorithm Execution → Step Generation
        ↓
Streaming Steps → Frontend
        ↓
Real-time Visualization

## 🎥 Frontend Integration
Uses WebSocket for real-time updates
Receives streamed steps
Animates visualization dynamically

## 🚀 Advanced Features (Implemented)

### 🔐 JWT Authentication

* Secure user authentication using JSON Web Tokens (JWT)
* Passwords hashed using bcrypt via Passlib
* Token-based access control for protected routes
* `/auth/register`, `/auth/login`, `/auth/me` endpoints implemented
* Stateless authentication (no server-side session storage)

**Tech Stack:**

* FastAPI Security
* python-jose (JWT)
* Passlib (bcrypt hashing)

---

### 🗄️ PostgreSQL User History

* Integrated PostgreSQL database for persistent storage
* Stores user data and activity history
* SQLAlchemy ORM used for database modeling
* Environment-based configuration using `.env`

**Features:**

* User registration & login stored in DB
* Scalable schema design for future analytics
* Ready for storing algorithm run history

**Tech Stack:**

* PostgreSQL
* SQLAlchemy
* psycopg2

---

### 🤖 AI Step Explanations

* Integrated AI-powered explanations for algorithm steps
* Backend generates contextual explanations for each step
* Frontend displays explanations alongside visualization

**Features:**

* Real-time explanation of algorithm behavior
* Enhances learning and understanding
* Can be extended with LLM APIs (Gemini / OpenAI)

**Future Scope:**

* "Explain this step" button
* Natural language Q&A for algorithms

**Tech Stack:**

* LLM API (Gemini / OpenAI)
* FastAPI backend integration


## 📌 Future Improvements
- ⚡ Redis caching
- 📊 Algorithm comparison mode
- 🎨 Advanced frontend (React)