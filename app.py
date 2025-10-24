from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
from datetime import datetime

# Initialize app
app = Flask(__name__)
app.config.from_object('config.Config')

# Ensure instance folder exists
os.makedirs('instance', exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# ---------------- Models ---------------- #
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Pending / Approved / Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Student {self.id} - {self.name}>'

# ---------------- Routes ---------------- #
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        course = request.form['course']

        student = Student(name=name, email=email, phone=phone, course=course)
        db.session.add(student)
        db.session.commit()

        flash('Registration submitted successfully!', 'success')
        return redirect(url_for('success'))

    return render_template('register.html')

@app.route('/success')
def success():
    return render_template('success.html')

# ---------------- Admin Panel ---------------- #
@app.route('/admin')
def admin():
    students = Student.query.order_by(Student.applied_at.desc()).all()
    return render_template('admin.html', students=students)

@app.route('/approve/<int:id>')
def approve(id):
    student = Student.query.get_or_404(id)
    student.status = "Approved"
    db.session.commit()

    # Send email notification
    try:
        msg = Message(
            subject='Admission Status',
            sender=app.config['MAIL_USERNAME'],
            recipients=[student.email],
            body=f"Dear {student.name}, your admission has been approved for the course: {student.course}."
        )
        mail.send(msg)
    except Exception as e:
        print("Email failed:", e)

    flash(f"{student.name} approved successfully!", 'success')
    return redirect(url_for('admin'))

@app.route('/reject/<int:id>')
def reject(id):
    student = Student.query.get_or_404(id)
    student.status = "Rejected"
    db.session.commit()

    # Send email notification
    try:
        msg = Message(
            subject='Admission Status',
            sender=app.config['MAIL_USERNAME'],
            recipients=[student.email],
            body=f"Dear {student.name}, your admission for {student.course} has been rejected."
        )
        mail.send(msg)
    except Exception as e:
        print("Email failed:", e)

    flash(f"{student.name} rejected.", 'info')
    return redirect(url_for('admin'))

# ---------------- Run ---------------- #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
