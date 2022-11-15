from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import SignInForm, RegisterForm, TaskForm
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config["SECRET_KEY"] = "TopSecretKey"
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///to_do.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    tasks = db.relationship("Task", backref="user")


class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(250), nullable=False)
    task_date = db.Column(db.Date)
    task_done = db.Column(db.Boolean, unique=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html", current_user=current_user)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/signin", methods=["GET", "POST"])
def sign_in():
    form = SignInForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for("sign_in"))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.")
            return redirect(url_for("sign_in"))
        else:
            login_user(user)
            return redirect(url_for("task"))

    return render_template("sign_in.html", form=form, current_user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("sign_in"))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )

        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("task"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route("/task", methods=["GET", "POST"])
def task():
    form = TaskForm()
    all_tasks = Task.query.filter_by(user_id=current_user.id).all()
    if form.validate_on_submit():
        new_task = Task(
            task=form.task_name.data,
            task_date=form.task_date.data,
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("task"))
    return render_template("task.html", form=form, current_user=current_user, task=all_tasks)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>")
def delete(task_id):
    task_to_delete = Task.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for("task"))


@app.route("/finish_task/<int:task_id>")
def finish_task(task_id):
    task_to_finish = Task.query.get(task_id)
    finish = True
    task_to_finish.task_done = finish
    db.session.commit()
    return redirect(url_for("task"))


if __name__ == "__main__":
    app.run(debug=True)
