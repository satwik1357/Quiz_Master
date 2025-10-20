# 🎯 Quiz Master - V1  
### *A Flask-based Multi-User Exam Preparation Platform*

---

## 📖 Overview

**Quiz Master - V1** is a multi-user web application built with **Flask**, **Jinja2**, and **Bootstrap**, designed for online exam preparation and quiz management.  
It allows an **Admin (Quiz Master)** to create subjects, chapters, and quizzes, and enables **Users** to register, attempt quizzes, and track their performance.

---

## 🚀 Features

### 👨‍🏫 Admin (Quiz Master)
- 🔐 Secure login (predefined admin account)
- 📘 Create / Edit / Delete **Subjects**
- 📗 Create / Edit / Delete **Chapters**
- 🧩 Create / Edit / Delete **Quizzes**
- 📝 Add / Edit / Delete **Questions (MCQs)**  
- 🔍 Search Users / Subjects / Quizzes
- 📊 View Summary Charts (Users, Quizzes, Scores)

### 👤 User
- 📝 Register and Login
- 📚 Select Subject and Chapter
- 🕓 Attempt Quizzes (with optional Timer)
- 🧾 View Quiz Results & Past Scores
- 📈 Performance Visualization via Charts

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Flask (Python) |
| **Frontend** | Jinja2, HTML5, CSS3, Bootstrap |
| **Database** | SQLite |
| **ORM** | Flask SQLAlchemy |
| **Charts** | Chart.js |
| **Templating** | Jinja2 |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/quiz-master-v1.git
cd quiz-master-v1
