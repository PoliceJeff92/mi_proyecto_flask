from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

# Inicializar la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'una-clave-super-secreta'

# --- Configuración de MySQL ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'desarrollo_web'

# Inicializar Flask-MySQLdb y Flask-Login
mysql = MySQL(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Modelo de Usuario ---
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Función para cargar el usuario
@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    if user_data:
        return User(id=user_data[0], username=user_data[1], password=user_data[2])
    return None

# --- Rutas de la Aplicación ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validación de campos
        if not username or not password:
            flash('Ambos campos, nombre de usuario y contraseña, son obligatorios.', 'error')
            return redirect(url_for('registro'))
        
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'error')
            return redirect(url_for('registro'))

        cur = mysql.connection.cursor()
        
        # Verificar si el nombre de usuario ya existe
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        
        if existing_user:
            flash('El nombre de usuario ya existe. Por favor, elige otro.', 'error')
            cur.close()
            return redirect(url_for('registro'))
        
        # Si la validación pasa, procede con el registro
        hashed_password = generate_password_hash(password, method='scrypt')
        
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            mysql.connection.commit()
            cur.close()
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error al registrar el usuario: {e}")
            cur.close()
            flash('Ocurrió un error inesperado al registrar el usuario.', 'error')
            return redirect(url_for('registro'))
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data and check_password_hash(user_data[2], password):
            user = User(id=user_data[0], username=user_data[1], password=user_data[2])
            login_user(user)
            flash('¡Has iniciado sesión con éxito!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Inicio de sesión fallido. Revisa tu nombre de usuario y contraseña.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html') # Cambia esto para renderizar una plantilla
    # En la plantilla profile.html puedes usar current_user.username
    # return f"¡Hola, {current_user.username}! Estás en tu página de perfil."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)