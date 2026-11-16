
from flask import Flask, request, jsonify
from models import db, Todo

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()


# Home route
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Flask Todo REST API",
        "status": "Running successfully"
    })


# GET - Retrieve all todos
@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos])


# POST - Create a new todo
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json(silent=True) or {}

    if not isinstance(data, dict) or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400

    todo = Todo(
        title=data['title'],
        description=data.get('description', '')
    )

    db.session.add(todo)
    db.session.commit()

    return jsonify(todo.to_dict()), 201


# GET - Retrieve a specific todo
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = db.session.get(Todo, todo_id)

    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    return jsonify(todo.to_dict())


# PUT - Update an existing todo
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = db.session.get(Todo, todo_id)

    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON object is required"}), 400

    if 'title' in data:
        if not isinstance(data['title'], str) or not data['title'].strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        todo.title = data['title']

    if 'description' in data:
        todo.description = data['description']

    if 'completed' in data:
        if not isinstance(data['completed'], bool):
            return jsonify({"error": "Completed must be true or false"}), 400
        todo.completed = data['completed']

    db.session.commit()

    return jsonify(todo.to_dict())


# DELETE - Remove a todo
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = db.session.get(Todo, todo_id)

    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    db.session.delete(todo)
    db.session.commit()

    return jsonify({"message": "Todo deleted successfully"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
