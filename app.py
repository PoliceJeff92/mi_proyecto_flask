from flask import Flask, render_template, request, jsonify
import os
import json
import csv
from flask_sqlalchemy import SQLAlchemy

# Configuración inicial de la app
app = Flask(__name__)

# --- Persistencia con SQLite (Flask-SQLAlchemy) ---
# Se configura la base de datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database', 'usuarios.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db = SQLAlchemy(app)

# Se define el modelo de datos para la tabla de usuarios
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

# Se crea la base de datos y las tablas si no existen
with app.app_context():
    os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)
    db.create_all()

# --- Rutas de la aplicación ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        
        # Opcional: Puedes guardar los datos en un formato específico
        # como txt, json, csv o en la base de datos aquí mismo.
        # Por simplicidad, las rutas de guardado están separadas.

        return render_template('resultado.html', nombre=nombre, email=email)
    return render_template('formulario.html')


# --- Rutas para Persistencia con Archivos ---
# Directorio para los archivos de datos
datos_dir = 'datos'
if not os.path.exists(datos_dir):
    os.makedirs(datos_dir)

# --- TXT ---
@app.route('/guardar_txt', methods=['POST'])
def guardar_txt():
    nombre = request.form['nombre']
    email = request.form['email']
    
    with open(os.path.join(datos_dir, 'datos.txt'), 'a') as f:
        f.write(f"Nombre: {nombre}, Email: {email}\n")
    return jsonify({'mensaje': 'Datos guardados en datos.txt'})

@app.route('/leer_txt')
def leer_txt():
    datos = []
    try:
        with open(os.path.join(datos_dir, 'datos.txt'), 'r') as f:
            for line in f:
                datos.append(line.strip())
    except FileNotFoundError:
        return jsonify({'error': 'El archivo datos.txt no existe.'}), 404
    return jsonify(datos)

# --- JSON ---
@app.route('/guardar_json', methods=['POST'])
def guardar_json():
    nombre = request.form['nombre']
    email = request.form['email']
    
    # Cargar datos existentes si el archivo existe, si no, crear lista vacía
    datos = []
    if os.path.exists(os.path.join(datos_dir, 'datos.json')):
        with open(os.path.join(datos_dir, 'datos.json'), 'r') as f:
            datos = json.load(f)
            
    nuevo_dato = {'nombre': nombre, 'email': email}
    datos.append(nuevo_dato)
    
    with open(os.path.join(datos_dir, 'datos.json'), 'w') as f:
        json.dump(datos, f, indent=4)
        
    return jsonify({'mensaje': 'Datos guardados en datos.json'})

@app.route('/leer_json')
def leer_json():
    try:
        with open(os.path.join(datos_dir, 'datos.json'), 'r') as f:
            datos = json.load(f)
    except FileNotFoundError:
        return jsonify({'error': 'El archivo datos.json no existe.'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'El archivo datos.json no es un JSON válido.'}), 500
    return jsonify(datos)

# --- CSV ---
@app.route('/guardar_csv', methods=['POST'])
def guardar_csv():
    nombre = request.form['nombre']
    email = request.form['email']
    
    nuevo_dato = {'nombre': nombre, 'email': email}
    
    file_exists = os.path.exists(os.path.join(datos_dir, 'datos.csv'))
    
    with open(os.path.join(datos_dir, 'datos.csv'), 'a', newline='') as f:
        fieldnames = ['nombre', 'email']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Escribe la cabecera si el archivo no existía
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(nuevo_dato)
        
    return jsonify({'mensaje': 'Datos guardados en datos.csv'})

@app.route('/leer_csv')
def leer_csv():
    datos = []
    try:
        with open(os.path.join(datos_dir, 'datos.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                datos.append(row)
    except FileNotFoundError:
        return jsonify({'error': 'El archivo datos.csv no existe.'}), 404
    return jsonify(datos)


# --- Rutas para Persistencia con SQLite ---
@app.route('/guardar_db', methods=['POST'])
def guardar_db():
    nombre = request.form['nombre']
    email = request.form['email']
    
    nuevo_usuario = Usuario(nombre=nombre, email=email)
    
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({'mensaje': 'Datos guardados en la base de datos SQLite'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ocurrió un error: {e}'}), 500

@app.route('/leer_db')
def leer_db():
    usuarios = Usuario.query.all()
    # Convierte los objetos de la base de datos a un formato JSON
    resultado = [{'id': user.id, 'nombre': user.nombre, 'email': user.email} for user in usuarios]
    return jsonify(resultado)

if __name__ == '__main__':
    # Cambia esto para que no se ejecute en el servidor de Render
    # app.run(debug=True)
    # El servidor Gunicorn se encargará de ejecutar la app
    pass