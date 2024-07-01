import unittest
import json
import uuid
import base64  # Import base64 module for encoding
from app import app, db, Users, Books
from werkzeug.security import generate_password_hash

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Create tables and a test user
        with app.app_context():
            db.create_all()
            self.create_test_user()

    def tearDown(self):
        # Clean up after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_user(self):
        test_user = Users(public_id=str(uuid.uuid4()), name='test_user', password=generate_password_hash('test_password', method='sha256'), admin=False)
        db.session.add(test_user)
        db.session.commit()

    def get_token(self):
        # Log in and get a token
        response = self.app.post('/login', headers={
            'Authorization': 'Basic ' + base64.b64encode(b'test_user:test_password').decode('utf-8')
        })
        data = json.loads(response.data)
        return data['token']

    def test_create_book(self):
        token = self.get_token()
        response = self.app.post('/book', json={
            'name': 'Test Book',
            'Author': 'Test Author',
            'Publisher': 'Test Publisher',
            'book_prize': 100
        }, headers={'x-access-tokens': token})

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'new book created')

    def test_get_all_books(self):
        token = self.get_token()
        self.app.post('/book', json={
            'name': 'Test Book',
            'Author': 'Test Author',
            'Publisher': 'Test Publisher',
            'book_prize': 100
        }, headers={'x-access-tokens': token})

        response = self.app.get('/books', headers={'x-access-tokens': token})
        
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue('list_of_books' in data)
        self.assertEqual(len(data['list_of_books']), 1)
        self.assertEqual(data['list_of_books'][0]['name'], 'Test Book')

    def test_get_book_by_name(self):
        token = self.get_token()
        self.app.post('/book', json={
            'name': 'Test Book',
            'Author': 'Test Author',
            'Publisher': 'Test Publisher',
            'book_prize': 100
        }, headers={'x-access-tokens': token})

        response = self.app.get('/books/Test Book', headers={'x-access-tokens': token})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], 'Test Book')

    def test_delete_book(self):
        token = self.get_token()
        self.app.post('/book', json={
            'name': 'Test Book',
            'Author': 'Test Author',
            'Publisher': 'Test Publisher',
            'book_prize': 100
        }, headers={'x-access-tokens': token})

        response = self.app.get('/books', headers={'x-access-tokens': token})
        data = json.loads(response.data)
        book_id = data['list_of_books'][0]['id']

        response = self.app.delete(f'/books/{book_id}', headers={'x-access-tokens': token})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Book deleted')

        # Verify book is deleted
        response = self.app.get('/books', headers={'x-access-tokens': token})
        data = json.loads(response.data)
        self.assertEqual(len(data['list_of_books']), 0)

if __name__ == '__main__':
    unittest.main()
