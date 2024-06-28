from flask import Flask, render_template, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_socketio import SocketIO, send

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///creds.db'
app.config['SECRET_KEY'] = '\x06L\xde\xb9\xc3\x97\xe2\x1c\xbd\xdbT|\xf1\xd5_\xc1\x8c#\xebW#[\xf6\x0b'
db = SQLAlchemy(app)
socket = SocketIO(app, cors_allowed_origins='*')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    passwd = db.Column(db.String(80), nullable=False)

class register_form(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    passwd = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        check_user = User.query.filter_by(username=username.data).first()
        if check_user:
            raise ValidationError('Username taken! Pick another one.')

class login_form(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    passwd = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

@app.route('/', methods=['GET', 'POST'])
def login():
    form = login_form()
    if form.validate_on_submit():
        session['username'] = form.username.data
        user_check = User.query.filter_by(username=form.username.data).first()
        if user_check:
            if bcrypt.check_password_hash(user_check.passwd, form.passwd.data):
                login_user(user_check)
                return redirect(url_for('chat_room'))
    return render_template('home.html', login_box = form)

@app.route('/sign-out', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = register_form()
    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.passwd.data)
        new_user = User(username=form.username.data, passwd=password_hash)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', register_box = form)

@app.route('/chat_room', methods=['GET', 'POST'])
@login_required
def chat_room():
    return render_template('chat.html')

@socket.on('message')
def message_handler(message):
    global connected
    print('>> ' + message)
    print(session)
    if message[:7] == '(-@+@-)':
        pass
    elif message.strip()[-1] == "]":
        pass
    else:
        send(message, broadcast=True)

if __name__ == '__main__':
    # app.run(debug=True)
    socket.run(app , host="127.0.0.1", debug=True)
