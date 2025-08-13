from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return '¡Hola, mundo! Esta es mi primera aplicación con Flask.'

if __name__ == '__main__':
    app.run(debug=True)