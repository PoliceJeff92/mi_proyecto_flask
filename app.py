from flask import Flask, render_template

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Definir la ruta para la página de inicio
@app.route('/')
def home():
    # Renderizar la plantilla 'index.html'
    return render_template('index.html')

# Definir la ruta para la página "Acerca de"
@app.route('/about')
def about():
    # Renderizar la plantilla 'about.html'
    return render_template('about.html')

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)