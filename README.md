# Gym Management System

A full-stack web application for managing gym operations, built with Python (Flask) and MySQL.

## Features

**Member Side**
- Register and log in with secure password hashing (bcrypt)
- Forgot password flow with OTP sent via email
- View and upgrade membership plans
- Browse and book workout sessions
- Track workout progress (sets, reps, calories burned)
- View diet plans and equipment

**Admin Side**
- Separate admin login with security key protection
- Add, edit, and remove gym members
- Manage gym equipment (with image upload)
- View all registered users

## Tech Stack

- **Backend:** Python, Flask, MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Auth:** Flask-Bcrypt (password hashing), Session-based login
- **Email:** SMTP (Gmail) for OTP delivery
- **PDF Generation:** ReportLab
- **File Uploads:** Werkzeug
- **Version Control:** Git

## Project Structure

```
gym-management-system/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── .gitignore
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/            # Uploaded equipment images
└── templates/
    ├── index.html
    ├── login.html
    ├── register.html
    ├── user_dashboard.html
    ├── admin_dashboard.html
    ├── workout_plans.html
    ├── workout_details.html
    ├── equipment.html
    └── ...
```

## Getting Started

### Prerequisites

- Python 3.8+
- MySQL
- pip

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/Gowtham-vg/gym-management-system.git
cd gym-management-system
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up the database**

Create a MySQL database named `gym_management` and import the schema:
```bash
mysql -u root -p gym_management < schema.sql
```

**4. Configure environment variables**

Create a `.env` file in the root folder:
```
SECRET_KEY=your_secret_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=gym_management
MAIL_EMAIL=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
```

> To get a Gmail App Password: Google Account → Security → 2-Step Verification → App Passwords

**5. Run the app**
```bash
python app.py
```

Open your browser and go to: `http://127.0.0.1:5000`

## Requirements

Create a `requirements.txt` file with:
```
flask
flask-bcrypt
flask-mail
mysql-connector-python
reportlab
werkzeug
python-dotenv
```

Generate it automatically with:
```bash
pip freeze > requirements.txt
```

## Security Note

This project uses environment variables to store sensitive credentials. Never commit your `.env` file or hardcode passwords in source code.

Add this to your `.gitignore`:
```
.env
static/uploads/
__pycache__/
*.pyc
```

## Author

**Gowtham B**  
MCA Graduate | Full Stack Developer  
[LinkedIn](https://.linkedin.com/in/gowtham-b-developer) · [GitHub](https://github.com/Gowtham-vg)
