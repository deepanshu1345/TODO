from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_pymongo import PyMongo
import jwt
import datetime
from bson.objectid import ObjectId
from functools import wraps
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'my_secret_key'
# app.config['MONGO_URI'] = "mongodb://localhost:27017/tasks"
app.config['MONGO_URI'] = "mongodb+srv://deepanshulakde26:71MTKApcuwva5o6M@deepanshucluster.zrgfxrc.mongodb.net/db?retryWrites=true&w=majority&appName=DeepanshuCluster"
mongo = PyMongo(app)
collection = mongo.db.tasksuser
users_collection = mongo.db.users
app.config['SECRET_KEY'] = 'your_secret_key'

# Session configuration
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Function to require token on protected routes
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('jwt_token')  # Fetch token from session
        print(token)
        print(f)

        if not token:
            error_message = 'Token is missing!'
            return render_template('error.html', error_message=error_message)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS512"])
            current_user = users_collection.find_one({'username': data['username']})
        except jwt.ExpiredSignatureError:
            error_message = 'Token has expired!'
            return render_template('error.html', error_message=error_message)
        except jwt.InvalidTokenError:
            error_message = 'Invalid Token!'
            return render_template('error.html', error_message=error_message)

        return f(current_user, *args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    return redirect(url_for('login'))  # Ensure login is the first step


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Getting form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))

        # Check if username already exists
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            flash('Username already taken!', 'error')
            return redirect(url_for('signup'))

        # Insert the new user into MongoDB without hashing the password
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': password  # Storing plain password (not recommended)
        })

        flash('Account created successfully!', 'success')
        return redirect(url_for('index'))


    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username)

        # Check if user exists
        user = users_collection.find_one({'username': username})
        if user and user['password'] == password:  # Checking plain password
            # Generate JWT token
            token = jwt.encode({'username': username, 'exp': datetime.datetime.now() + datetime.timedelta(hours=1)},
                                app.config['SECRET_KEY'], algorithm='HS512')

            # Store token in session
            session['jwt_token'] = token

            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to /todo after login
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')


@app.route('/todo')
@token_required
def home(current_user):
    print(current_user)
    tasks = collection.find({
        'user': current_user["username"]
    })
    user = current_user["username"]
    return render_template("todolist.html", tasks=tasks, user = user)


@app.route("/add", methods=["POST", "GET"])
@token_required
def add(current_user):
    if request.method == "POST":
        task = {
            'task': request.form['task'],
            'user': current_user["username"]
        }
        collection.insert_one(task)
        flash('Task added successfully!', 'success')
        return redirect("/todo")  # Redirect to /todo after adding a task


@app.route("/del/<task_id>")
@token_required
def delete(current_user, task_id):
    collection.delete_one({'_id': ObjectId(task_id)})
    flash('Task deleted successfully!', 'success')
    return redirect("/todo")  # Redirect to /todo after deleting a task


@app.route('/edit/<task_id>', methods=['POST', 'GET'])
@token_required
def edit_task(current_user, task_id):
    tasks = collection.find()
    if request.method == "POST":
        task_title = request.form.get('task')

        collection.update_one(
            {'_id': ObjectId(task_id)},
            {'$set': {
                'task': task_title,
            }}
        )
        flash('Task updated successfully!', 'success')
        return redirect("/todo")  # Redirect to /todo after updating a task

    existing_task = collection.find_one({'_id': ObjectId(task_id)})
    if not existing_task:
        flash('Task not found!', 'error')
        return redirect(url_for('home'))

    # return render_template("update.html", task=tasks, task_id=task_id, existing_task=existing_task)


@app.route('/logout')
@token_required
def logout(current_user):
    print(current_user)
    session.pop('jwt_token', None)  # Remove JWT from session
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))  # Redirect to login page after logout


if __name__ == "__main__":
    app.run(debug=True, port=2323)
