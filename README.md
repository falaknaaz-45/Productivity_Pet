# 🐉 Productivity Pet

A gamified productivity application where users complete tasks to grow and evolve their virtual pet companion. Built with Flask (Python) backend and vanilla JavaScript frontend.

## 📋 Project Overview

**Productivity Pet** is an interactive web application that combines task management with pet simulation to motivate users to stay productive. As users complete tasks, they earn XP that helps their virtual pet evolve through different stages, from an egg to a legendary dragon.

### Project Classification
- **Domain:** Productivity (June - Birth Month)
- **Application Type:** Gamified App (9 - Last digit of roll number)
- **Technology:** Python with AI-assisted testing (Favorite Technology)

## ✨ Features

### Core Functionality
- **User Authentication:** Secure registration and login with JWT tokens
- **Task Management:** Create, complete, and delete tasks with priority levels (Low, Medium, High)
- **Virtual Pet System:** Watch your pet evolve through 5 stages based on your productivity
- **Gamification:** Earn XP, level up, maintain streaks, and unlock achievements
- **Pet Care:** Feed your pet, monitor health, happiness, and hunger stats
- **Achievement System:** Unlock badges for milestones and accomplishments
- **Activity Logging:** Track all your productivity activities

### Pet Evolution Stages
1. 🥚 **Egg** (0 XP)
2. 🐣 **Baby** (100 XP)
3. 🐥 **Teen** (500 XP)
4. 🐉 **Adult** (1,500 XP)
5. 🐲 **Legendary** (3,500 XP)

### Task Priorities & XP Rewards
- **Low Priority:** 5 XP
- **Medium Priority:** 10 XP
- **High Priority:** 20 XP
- **Bonus:** +5 XP for completing tasks 2+ days early

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 3.0.0
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** JWT (Flask-JWT-Extended)
- **CORS:** Flask-CORS for cross-origin requests
- **Scheduler:** APScheduler for periodic tasks

### Frontend
- **HTML5/CSS3:** Responsive design with gradients and animations
- **Vanilla JavaScript:** No frameworks, pure JS for interactivity
- **REST API Integration:** Fetch API for backend communication

### Testing
- **pytest:** Python testing framework
- **pytest-cov:** Code coverage reporting
- **pytest-flask:** Flask-specific testing utilities

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/falaknaaz-45/Productivity_Pet.git
cd Productivity_Pet
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize the database**
```bash
python run.py
```
The database will be automatically created on first run.

## 🚀 Running the Application

1. **Start the Flask server**
```bash
python run.py
```
The server will start at `http://127.0.0.1:5000`

2. **Open the frontend**
- Navigate to `http://127.0.0.1:5000` in your browser
- Or open `templates/index.html` directly in a browser

3. **Create an account**
- Click on the "Register" tab
- Fill in your details and name your pet
- Start completing tasks to grow your pet!

## 📊 Project Structure

```
Productivity_Pet/
│
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── models/                  # Database models
│   │   ├── user.py              # User model with auth
│   │   ├── pet.py               # Pet model with evolution logic
│   │   ├── task.py              # Task model with XP calculation
│   │   ├── achievement.py       # Achievement system
│   │   └── activity_log.py      # Activity tracking
│   │
│   └── routes/                  # API endpoints
│       ├── auth.py              # Authentication routes
│       ├── tasks.py             # Task management routes
│       ├── pets.py              # Pet interaction routes
│       └── achievements.py      # Achievement routes
│
├── templates/
│   └── index.html               # Frontend single-page app
│
├── config.py                    # Application configuration
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile (Protected)

### Tasks
- `GET /api/tasks/` - Get all user tasks (Protected)
- `POST /api/tasks/` - Create new task (Protected)
- `POST /api/tasks/<id>/complete` - Complete task (Protected)
- `DELETE /api/tasks/<id>` - Delete task (Protected)

### Pet
- `GET /api/pet/` - Get pet status (Protected)
- `POST /api/pet/feed` - Feed pet (Protected)

### Achievements
- `GET /api/achievements/` - Get user achievements (Protected)

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## 🎮 How to Use

1. **Register & Login:** Create your account and name your pet
2. **Add Tasks:** Click "Add Task" and specify priority level
3. **Complete Tasks:** Check off completed tasks to earn XP
4. **Watch Your Pet Grow:** Your pet evolves as you gain XP
5. **Feed Your Pet:** Keep your pet happy and healthy by feeding it (costs 5 XP)
6. **Unlock Achievements:** Complete milestones to earn badges
7. **Maintain Streaks:** Complete tasks daily to build your streak

## 🤖 AI Usage in Development

This project was developed using AI assistance across the full Software Development Lifecycle:

- **Planning:** AI-generated user stories and requirements
- **Design:** AI-assisted database schema and architecture diagrams
- **Implementation:** AI-assisted code generation and debugging
- **Testing:** AI-generated unit tests and test cases
- **Documentation:** AI-assisted documentation and README

## 🔒 Security Features

- Password hashing with Werkzeug
- JWT token-based authentication
- Protected API endpoints
- CORS configuration for secure cross-origin requests
- SQL injection prevention through SQLAlchemy ORM

## 📈 Future Enhancements

- Social features (friends, leaderboards)
- Multiple pet species to choose from
- Pet customization options
- Mobile app version
- Real-time notifications
- Task categories and filtering
- Calendar view for deadlines
- Data export functionality

## 🐛 Known Issues

- Pet health decay scheduler not yet implemented
- Recurring tasks feature incomplete
- Achievement unlock notifications need improvement

## 👤 Author

**Falak Naaz**
- GitHub: [@falaknaaz-45](https://github.com/falaknaaz-45)
- Project: AI-Enhanced Software Development Final Term Project

## 📄 License

This project is created for educational purposes as part of a university course on AI-Enhanced Software Development.

## 🙏 Acknowledgments

- Course instructor for project requirements
- AI tools (ChatGPT, Claude) for development assistance
- Flask and Python community for excellent documentation

---

**Note:** This project demonstrates the integration of AI tools throughout the Software Development Lifecycle (SDLC) as required by the course curriculum.
