from flask import Flask, make_response, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!', 200

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

if __name__ == '__main__':
    app.run()