from flask import Flask, jsonify, make_response, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import uuid
import jwt
import datetime
import os
from flasgger import Swagger

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(12)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://////Users/aniruddh/bookstore-project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Swagger for documentation
Swagger(app)

# Model 1
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)

# Model 2
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    Author = db.Column(db.String(50), unique=True, nullable=False)
    Publisher = db.Column(db.String(50), nullable=False)
    book_prize = db.Column(db.Integer)

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

# Decorator for token authentication
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator

@app.route('/register', methods=['POST'])
def signup_user():
    """Endpoint to register a new user.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: User
          required:
            - name
            - password
          properties:
            name:
              type: string
              description: User's name
            password:
              type: string
              description: User's password
    responses:
      200:
        description: User registered successfully
    """
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'registered successfully'})

@app.route('/login', methods=['POST'])
def login_user():
    """Endpoint to log in an existing user.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Login
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: User's name
            password:
              type: string
              description: User's password
    responses:
      200:
        description: Token generated successfully
      401:
        description: Could not verify user
    """
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'Authentication': 'login required"'})

    user = Users.query.filter_by(name=auth.username).first()
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")

        return jsonify({'token': token})

    return make_response('could not verify', 401, {'Authentication': '"login required"'})

@app.route('/users', methods=['GET'])
def get_all_users():
    """Endpoint to get all registered users.
    ---
    responses:
      200:
        description: List of all users
    """
    users = Users.query.all()
    result = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin

        result.append(user_data)
    return jsonify({'users': result})

@app.route('/book', methods=['POST'])
@token_required
def create_book(current_user):
    """Endpoint to create a new book.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Book
          required:
            - name
            - Author
            - Publisher
            - book_prize
          properties:
            name:
              type: string
              description: Book name
            Author:
              type: string
              description: Book author
            Publisher:
              type: string
              description: Book publisher
            book_prize:
              type: integer
              description: Book price
    responses:
      200:
        description: New book created successfully
      401:
        description: Token is missing or invalid
    """
    data = request.get_json()

    # Check if the book already exists in the database
    existing_book = Books.query.filter_by(name=data['name'], Author=data['Author'], Publisher=data['Publisher'], book_prize=data['book_prize']).first()
    if existing_book:
        return jsonify({'message': 'Book already exists'}), 409
    curr_book = Books.query.filter_by(name=data['name'], Author=data['Author'], Publisher=data['Publisher']).first()
    if curr_book:
        db.session.delete(curr_book)
        db.session.commit()
    new_books = Books(name=data['name'], Author=data['Author'], Publisher=data['Publisher'], book_prize=data['book_prize'], user_id=current_user.id)
    db.session.add(new_books)
    db.session.commit()
    return jsonify({'message': 'new book created'})

@app.route('/books', methods=['GET'])
@token_required
def get_books(current_user):
    """Endpoint to retrieve all books.
    ---
    responses:
      200:
        description: List of all books
    """
    books = Books.query.filter_by(user_id=current_user.id).all()
    output = []
    for book in books:
        book_data = {}
        book_data['id'] = book.id
        book_data['name'] = book.name
        book_data['Author'] = book.Author
        book_data['Publisher'] = book.Publisher
        book_data['book_prize'] = book.book_prize
        output.append(book_data)

    return jsonify({'list_of_books': output})

@app.route('/books/<name>', methods=['GET'])
@token_required
def get_book_by_name(current_user, name):
    """Endpoint to retrieve a book by its name.
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Book name
    responses:
      200:
        description: Book details retrieved successfully
      404:
        description: Book not found
    """
    book = Books.query.filter_by(user_id=current_user.id, name=name).first()

    if not book:
        return jsonify({'message': 'Book not found'}), 404

    book_data = {
        'id': book.id,
        'name': book.name,
        'Author': book.Author,
        'Publisher': book.Publisher,
        'book_prize': book.book_prize
    }

    return jsonify(book_data)

@app.route('/books/<book_id>', methods=['DELETE'])
@token_required
def delete_book(current_user, book_id):
    """Endpoint to delete a book by its ID.
    ---
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: Book ID
    responses:
      200:
        description: Book deleted successfully
      401:
        description: Token is missing or invalid
      404:
        description: Book not found
    """
    book = Books.query.filter_by(id=book_id, user_id=current_user.id).first()
    if not book:
        return jsonify({'message': 'book does not exist'})

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})

if __name__ == '__main__':
    app.run(debug=True)
