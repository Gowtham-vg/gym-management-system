<div align="center">

# 🏋️ Gym Management System

### Modern Full-Stack Gym Management & Equipment Sales Web Application

*A complete Gym Management solution built with **Python (Flask)**, **MySQL**, and modern web technologies.*

<p>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web_App-000000?style=for-the-badge&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

</p>

<p>

![GitHub Repo stars](https://img.shields.io/github/stars/Gowtham-vg/gym-management-system?style=flat-square)
![GitHub forks](https://img.shields.io/github/forks/Gowtham-vg/gym-management-system?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/Gowtham-vg/gym-management-system?style=flat-square)
![GitHub repo size](https://img.shields.io/github/repo-size/Gowtham-vg/gym-management-system?style=flat-square)

</p>

---

## 📖 Overview

The **Gym Management System** is a full-stack web application designed to simplify gym administration and enhance the experience for both members and administrators.

It provides secure authentication, workout tracking, membership management, equipment sales, admin dashboards, and automated password recovery using OTP verification.

---

# ✨ Features

## 👤 Member Module

- 🔐 Secure Registration & Login
- 🔑 Forgot Password using Email OTP
- 🔒 Bcrypt Password Hashing
- 💳 Membership Management
- 📅 Workout Session Booking
- 📊 Progress Tracking
- 🔥 Calories Burned Tracking
- 💪 Workout Plans
- 🥗 Diet Plans
- 🛒 Equipment Store

---

## 👨‍💼 Admin Module

- 🔐 Separate Admin Login
- 🛡 Security Key Protection
- 👥 Manage Members
- ➕ Add Equipment
- ✏ Edit Equipment
- ❌ Delete Equipment
- 🖼 Image Upload Support
- 📋 View Registered Users
- 📈 Dashboard Management

---

# 🚀 Technology Stack

| Category | Technologies |
|-----------|--------------|
| **Backend** | Python, Flask |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Database** | MySQL |
| **Authentication** | Flask-Bcrypt |
| **Email Service** | Gmail SMTP |
| **Reports** | ReportLab PDF |
| **File Uploads** | Werkzeug |
| **Version Control** | Git & GitHub |

---

# 🏗 System Architecture

```text
               User
                │
                ▼
      HTML • CSS • JavaScript
                │
                ▼
          Flask Application
                │
      ┌─────────┴─────────┐
      ▼                   ▼
 MySQL Database      SMTP Email
      │                   │
      ▼                   ▼
Workout Data        OTP Verification
Members
Equipment
Sessions
```

---

# 📂 Project Structure

```text
gym-management-system
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── static
│   ├── css
│   ├── js
│   ├── images
│   └── uploads
│
└── templates
    ├── index.html
    ├── login.html
    ├── register.html
    ├── forgot_password.html
    ├── reset_password.html
    ├── user_dashboard.html
    ├── admin_dashboard.html
    ├── equipment.html
    ├── workout_plans.html
    ├── workout_details.html
    └── ...
```

---

# ⚙ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/Gowtham-vg/gym-management-system.git

cd gym-management-system
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Configure MySQL

Create a database named

```text
gym_management
```

Import your SQL schema.

---

## 4️⃣ Create .env

```env
SECRET_KEY=your_secret_key

DB_HOST=localhost

DB_USER=root

DB_PASSWORD=your_mysql_password

DB_NAME=gym_management

MAIL_EMAIL=your_email@gmail.com

MAIL_PASSWORD=your_gmail_app_password
```

---

## 5️⃣ Run the Application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

# 🔒 Security Features

- ✅ Password Hashing using Flask-Bcrypt
- ✅ Environment Variables for Credentials
- ✅ OTP-based Password Reset
- ✅ Secure Session Authentication
- ✅ Separate Admin Authentication
- ✅ Sensitive Credentials excluded using `.gitignore`

---

# 📦 Requirements

```
Flask

Flask-Bcrypt

Flask-Mail

mysql-connector-python

python-dotenv

Werkzeug

ReportLab
```

or

```bash
pip install -r requirements.txt
```

---

# 🚀 Future Enhancements

- 🤖 AI Workout Recommendation
- 📱 Mobile Responsive Dashboard
- 💳 Online Payment Integration
- 📷 QR Attendance System
- ☁ Cloud Deployment
- 📈 Analytics Dashboard
- 📩 Email Notifications
- 📅 Trainer Scheduling

---

# 👨‍💻 Author

## Gowtham B

**MCA Graduate | Full Stack Developer**

🔗 GitHub

https://github.com/Gowtham-vg

🔗 LinkedIn

https://www.linkedin.com/in/gowtham-b-developer/

---

<div align="center">

### ⭐ If you found this project useful, consider giving it a Star!

**Made with ❤️ by Gowtham B**

</div>
