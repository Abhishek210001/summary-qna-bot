from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello! Your server is working!</h1><p>If you see this, Flask is running correctly.</p>'

if __name__ == '__main__':
    print("Starting simple test server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='localhost', port=5000)
