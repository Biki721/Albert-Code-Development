from flask import Flask, request, render_template_string, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import session
 
# Set up Flask and LoginManager
app = Flask(__name__)
app.secret_key = '0be4d357bbc029961773819455bc116a'
login_manager = LoginManager()
login_manager.init_app(app)
 
# Set up User model
class User(UserMixin):
    def __init__(self, id):
        self.id = id
 
# Set up user loader
@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id else None
 
# Add a global variable to track if a user is logged in
user_logged_in = False
user_email = None  # Add a global variable to track the email of the logged in user
 
# Modify the login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_logged_in, user_email
    common_password = 'password'  # The common password for all users
    error = None
    if request.method == 'POST':
        if user_logged_in:
            error = f'Another user with email {user_email} is currently logged in. Please try again later.'
        elif request.form['password'] != common_password:
            error = 'Invalid credentials. Please try again.'
        else:
            user = User(request.form['email'])  # Create a User with the provided email
            login_user(user)
            user_logged_in = True  # Set the global variable to True when a user logs in
            user_email = request.form['email']  # Store the email of the logged in user
            return redirect('/dashboard/dashboard')  # Change this line
    return render_template_string('''
    <head>
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='styles.css') }}">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
    </head>
    <body>
        <section>
            <form method="post">
                <h1>Login</h1>
                <div class="inputbox">
                    <ion-icon name="mail-outline"></ion-icon>
                    <input type="text" name=email required>
                    <label for="">Email</label>    
                </div>
                <div class="inputbox">
                    <ion-icon name="lock-closed-outline"></ion-icon>
                    <input type="password" name=password required>
                    <label for="">Password</label>    
                </div>
                <button type="submit">Login</button>
                <br>
                {% if error %}
                <br>
                <p class="error"><i class="fas fa-exclamation-triangle" style="color: #FF8300;"></i> <strong>{{ error }}</strong></p>
                {% endif %}
            </form>
        </section>
    </body>
''', error=error)
 
# Set up logout route
@app.route('/logout')
@login_required
def logout():
    global user_logged_in, user_email
    logout_user()
    user_logged_in = False  # Set the global variable to False when a user logs out
    user_email = None  # Clear the email of the logged out user
    return redirect(url_for('login'))
 
@app.before_request
def protect_dash_routes():
    if request.path.startswith('/dashboard') and not current_user.is_authenticated:
        return redirect(url_for('login'))