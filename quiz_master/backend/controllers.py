#App routes
from flask import Flask,render_template,request,url_for,redirect,session
from .models import *
from flask import current_app as app
from datetime import datetime
from sqlalchemy import func
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

# Import the app object from app.py
# from app import app

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        usr=User_Info.query.filter_by(email=uname,password=pwd).first()
        
        if usr and usr.role==0: #Existed and admin
            session['user_id'] = usr.id
            session['user_type'] = 'admin'
            session['user_name'] = usr.full_name
            return redirect(url_for("admin_dashboard",name=usr.full_name))
        elif usr and usr.role==1: #Existed and normal user
            session['user_id'] = usr.id
            session['user_type'] = 'user'
            session['user_name'] = usr.full_name
            return redirect(url_for("user_dashboard",id=usr.id,name=usr.full_name))
        else:
            return render_template("login.html",msg="Invalid user credentials...")

    return render_template("login.html",msg="")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # extract form data
        user_name = request.form['user_name']
        password = request.form['password']
        full_name = request.form['full_name']
        location = request.form['location']
        pin_code = request.form['pin_code']

        new_user = User_Info(
            full_name=full_name,
            email=user_name,
            password=password,
            address=location,
            pin_code=pin_code,
            role=1  #all registered users are regular users
        )
        db.session.add(new_user)
        db.session.commit()


        return redirect(url_for('signin'))  # after successful registration

    return render_template('signup.html')  # this shows the signup form



# Admin dashboard
@app.route("/admin/<name>")
def admin_dashboard(name):
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for('signin'))
        
    # Get all subjects
    subjects = Subject.query.all()
    
    # Calculate statistics
    stats = {
        'total_students': User_Info.query.filter_by(role=1).count(),
        'total_quizzes': Quiz.query.count(),
        'quizzes_taken': Score.query.count(),
        'average_score': db.session.query(db.func.avg(Score.total_scored)).scalar() or 0.0
    }
    
    return render_template("admin/admin_dashboard.html", 
                         name=name, 
                         subjects=subjects,
                         stats=stats)

# User dashboard
@app.route("/user/<id>/<name>")
def user_dashboard(id, name):
    if 'user_type' not in session or session['user_type'] != 'user' or str(session['user_id']) != str(id):
        return redirect(url_for('signin'))
        
    subjects = Subject.query.all()
    return render_template("user/user_dashboard.html", id=id, name=name, subjects=subjects)

# Add subject (admin only)
@app.route("/add_subject/<name>", methods=["GET", "POST"])
def add_subject(name):
    if request.method == "POST":
        subject_name = request.form.get("name")
        description = request.form.get("description")
        subject = Subject(name=subject_name, description=description)
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("admin/add_subject.html", name=name)

# Add chapter (admin only)
@app.route("/add_chapter/<subject_id>/<name>", methods=["GET", "POST"])
def add_chapter(subject_id, name):
    if request.method == "POST":
        chapter_name = request.form.get("name")
        description = request.form.get("description")
        chapter = Chapter(name=chapter_name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("admin/add_chapter.html", subject_id=subject_id, name=name)

# Add quiz (admin only)
@app.route("/add_quiz/<chapter_id>/<name>", methods=["GET", "POST"])
def add_quiz(chapter_id, name):
    if request.method == "POST":
        quiz_name = request.form.get("name")
        date_of_quiz = request.form.get("date_of_quiz")
        time_duration = request.form.get("time_duration")
        quiz = Quiz(name=quiz_name, date_of_quiz=date_of_quiz, time_duration=time_duration, chapter_id=chapter_id)
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("admin/add_quiz.html", chapter_id=chapter_id, name=name)

# Add question (admin only)
@app.route("/add_question/<quiz_id>/<name>", methods=["GET", "POST"])
def add_question(quiz_id, name):
    if request.method == "POST":
        question_statement = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        correct_option = request.form.get("correct_option")
        
        try:
            # Create and save the question
            question = Question(
                question_statement=question_statement,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                correct_option=correct_option,
                quiz_id=quiz_id
            )
            db.session.add(question)
            db.session.commit()
            return redirect(url_for("admin_dashboard", name=name))
        except Exception as e:
            print(f"Error adding question: {str(e)}")
            db.session.rollback()
            return render_template("admin/add_question.html", quiz_id=quiz_id, name=name, error="Failed to add question. Please try again.")
            
    return render_template("admin/add_question.html", quiz_id=quiz_id, name=name)

# Attempt quiz (user only)
@app.route("/quiz/<quiz_id>/<user_id>", methods=["GET", "POST"])
def attempt_quiz(quiz_id, user_id):
    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if request.method == "POST":
        total_score = 0
        for question in questions:
            selected_option = request.form.get(f"question_{question.id}")
            if selected_option == question.correct_option:
                total_score += 1
        score = Score(user_id=user_id, quiz_id=quiz_id, total_scored=total_score, time_stamp_of_attempt=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(score)
        db.session.commit()
        # Redirect to a quiz results page to display the score
        return redirect(url_for("quiz_results", quiz_id=quiz_id, user_id=user_id, score=total_score, total=len(questions)))
    return render_template("quiz/quiz.html", quiz=quiz, questions=questions, user_id=user_id)

# Quiz results page
@app.route("/quiz_results/<quiz_id>/<user_id>/<score>/<total>")
def quiz_results(quiz_id, user_id, score, total):
    user = User_Info.query.get(user_id)  # Fetch the user object
    return render_template("quiz/quiz_results.html", quiz_id=quiz_id, user_id=user_id, score=score, total=total, user=user)

# Edit subject (admin only)
@app.route("/edit_subject/<subject_id>/<name>", methods=["GET", "POST"])
def edit_subject(subject_id, name):
    subject = Subject.query.get(subject_id)
    if request.method == "POST":
        subject.name = request.form.get("name")
        subject.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("admin/edit_subject.html", subject=subject, name=name)

# Edit chapter (admin only)
@app.route("/edit_chapter/<chapter_id>/<name>", methods=["GET", "POST"])
def edit_chapter(chapter_id, name):
    chapter = Chapter.query.get(chapter_id)
    if request.method == "POST":
        chapter.name = request.form.get("name")
        chapter.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("admin/edit_chapter.html", chapter=chapter, name=name)

# Edit quiz (admin only)
@app.route("/edit_quiz/<quiz_id>/<name>", methods=["GET", "POST"])
def edit_quiz(quiz_id, name):
    quiz = Quiz.query.get(quiz_id)
    if request.method == "POST":
        quiz.name = request.form.get("name")
        quiz.date_of_quiz = request.form.get("date_of_quiz")
        quiz.time_duration = request.form.get("time_duration")
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("admin/edit_quiz.html", quiz=quiz, name=name)

# Edit question (admin only)
@app.route("/edit_question/<question_id>/<name>", methods=["GET", "POST"])
def edit_question(question_id, name):
    question = Question.query.get(question_id)
    if request.method == "POST":
        question.question_statement = request.form.get("question_statement")
        question.option1 = request.form.get("option1")
        question.option2 = request.form.get("option2")
        question.option3 = request.form.get("option3")
        question.option4 = request.form.get("option4")
        question.correct_option = request.form.get("correct_option")
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("admin/edit_question.html", question=question, name=name)

# Delete subject (admin only)
@app.route("/delete_subject/<subject_id>/<name>", methods=["GET"])
def delete_subject(subject_id, name):
    subject = Subject.query.get(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for("admin_dashboard", name=name))

# Delete chapter (admin only)
@app.route("/delete_chapter/<chapter_id>/<name>", methods=["GET"])
def delete_chapter(chapter_id, name):
    chapter = Chapter.query.get(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for("admin_dashboard", name=name))

# Delete quiz (admin only)
@app.route("/delete_quiz/<quiz_id>/<name>", methods=["GET"])
def delete_quiz(quiz_id, name):
    quiz = Quiz.query.get(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for("admin_dashboard", name=name))

# Delete question (admin only)
@app.route("/delete_question/<question_id>/<name>", methods=["GET"])
def delete_question(question_id, name):
    question = Question.query.get(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("admin_dashboard", name=name))

# Search functionality (admin only)
from sqlalchemy import or_

from sqlalchemy.sql import func

from sqlalchemy.sql import func
from flask import render_template, request, redirect, url_for
from sqlalchemy import or_

@app.route("/search/<name>", methods=["GET", "POST"])
def search(name):
    if request.method == "POST":
        search_text = request.form.get("search_text")

        # Filtered search results
        subjects = Subject.query.filter(Subject.name.ilike(f"%{search_text}%")).all()
        chapters = Chapter.query.filter(Chapter.name.ilike(f"%{search_text}%")).all()
        quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{search_text}%")).all()
        users = User_Info.query.filter(
            or_(
                User_Info.full_name.ilike(f"%{search_text}%"),
                User_Info.email.ilike(f"%{search_text}%"),
                User_Info.address.ilike(f"%{search_text}%")
            )
        ).all()

        # Performance Overview
        total_students = User_Info.query.count()
        total_quizzes = Quiz.query.count()
        quizzes_taken = Score.query.count()
        average_score = db.session.query(func.avg(Score.total_scored)).scalar()
        average_score = round(average_score or 0, 2)

        return render_template(
            "admin/admin_dashboard.html",
            name=name,
            subjects=subjects,
            chapters=chapters,
            quizzes=quizzes,
            users=users,
            search_text=search_text,
            searching=True,
            total_students=total_students,
            total_quizzes=total_quizzes,
            total_attempts=quizzes_taken,
            average_score=average_score
        )

    return redirect(url_for("admin_dashboard", name=name))



@app.route('/user_search/<int:user_id>/<username>', methods=['POST'])
def user_search(user_id, username):
    search_text = request.form.get('search_text').lower()

    subjects = Subject.query.filter(Subject.name.ilike(f"%{search_text}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{search_text}%")).all()
    quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{search_text}%")).all()  # Use correct field name

    return render_template(
        'user/user_search_results.html',
        name=username,
        id=user_id,
        search_text=search_text,
        subjects=subjects,
        chapters=chapters,
        quizzes=quizzes,
    )





#for summary chart
from flask import Flask, render_template, request, redirect, url_for
from .models import db, User_Info, Subject, Chapter, Quiz, Question, Score
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io
import base64

# Summary page (admin only)
@app.route("/admin_summary/<name>")
def admin_summary(name):
    try:
        # Fetch all scores and related data
        scores = db.session.query(
            Score,
            Quiz.name.label('quiz_name'),
            User_Info.full_name.label('user_name')
        ).join(Quiz).join(User_Info).all()

        # Organize data for visualization
        quiz_data = {}
        for score, quiz_name, user_name in scores:
            if quiz_name not in quiz_data:
                quiz_data[quiz_name] = {
                    'total_attempts': 0,
                    'total_score': 0,
                    'average_score': 0,
                    'students': set()
                }
            quiz_data[quiz_name]['total_attempts'] += 1
            quiz_data[quiz_name]['total_score'] += score.total_scored
            quiz_data[quiz_name]['students'].add(user_name)

        # Calculate averages
        for quiz in quiz_data.values():
            quiz['average_score'] = quiz['total_score'] / quiz['total_attempts'] if quiz['total_attempts'] > 0 else 0

        # Create performance graph
        plt.figure(figsize=(12, 6))
        quiz_names = list(quiz_data.keys())
        avg_scores = [quiz_data[quiz]['average_score'] for quiz in quiz_names]
        
        plt.bar(quiz_names, avg_scores, color='#0d6efd')
        plt.xlabel("Quiz Name")
        plt.ylabel("Average Score")
        plt.title("Quiz Performance Overview")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close()

        return render_template(
            "admin/admin_summary.html",
            name=name,
            plot_url=plot_url,
            quiz_data=quiz_data
        )
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return render_template(
            "admin/admin_summary.html",
            name=name,
            error="Failed to generate summary. Please try again."
        )

# User summary page
@app.route("/user_summary/<user_id>")
def user_summary(user_id):
    # Check if user is logged in and authorized
    if 'user_type' not in session or str(session['user_id']) != str(user_id):
        return redirect(url_for('signin'))

    try:
        # Fetch the user
        user = User_Info.query.get(user_id)
        if not user:
            return redirect(url_for('signin'))
        
        # Fetch scores with quiz names for the specific user
        scores = db.session.query(
            Score,
            Quiz.name.label('quiz_name')
        ).join(Quiz).filter(Score.user_id == user_id).all()

        if not scores:
            return render_template("user/user_summary.html", 
                                plot_url=None, 
                                id=user_id, 
                                name=user.full_name,
                                message="No quizzes attempted yet.")

        # Prepare data for the bar graph
        quiz_names = [score[1] for score in scores]  # Use index 1 for quiz_name
        user_scores = [score[0].total_scored for score in scores]  # Use score[0] for Score object

        # Create a bar graph
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(quiz_names)), user_scores, color='#0d6efd')
        plt.xlabel("Quiz Name")
        plt.ylabel("Your Score")
        plt.title("Your Quiz Performance")
        plt.xticks(range(len(quiz_names)), quiz_names, rotation=45, ha='right')
        plt.tight_layout()

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close()

        # Calculate statistics
        total_quizzes = len(scores)
        avg_score = sum(user_scores) / total_quizzes if total_quizzes > 0 else 0
        highest_score = max(user_scores) if user_scores else 0
        
        stats = {
            'total_quizzes': total_quizzes,
            'average_score': round(avg_score, 2),
            'highest_score': highest_score,
            'scores': list(zip(quiz_names, user_scores))
        }

        return render_template("user/user_summary.html", 
                            plot_url=plot_url, 
                            id=user_id, 
                            name=user.full_name,
                            stats=stats)
    except Exception as e:
        print(f"Error generating user summary: {str(e)}")
        return render_template("user/user_summary.html", 
                            id=user_id, 
                            name=user.full_name if user else "",
                            error="Failed to generate summary. Please try again.")