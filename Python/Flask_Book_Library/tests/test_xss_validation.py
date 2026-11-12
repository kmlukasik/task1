import unittest
from datetime import datetime
from project import app, db
from project.books.models import Book
from project.customers.models import Customer
from project.loans.models import Loan

class TestXSSValidation(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #testy book
    def test_valid_book(self):
        book = Book(name="Wspaniala Ksiazka", author="Wspanialy Autor", year_published=2008, book_type="5days")
        self.assertEqual(book.name, "Wspaniala Ksiazka")

    def test_invalid_book_xss(self):
        with self.assertRaises(ValueError):
            Book(name="<script>alert('XSS')</script>", author="Autor", year_published=2020, book_type="2days")

    #testy customer
    def test_valid_customer(self):
        customer = Customer(name="Mariusz Pudzianowski", city="Warszawa", age=30)
        self.assertEqual(customer.city, "Warszawa")

    def test_invalid_customer_xss(self):
        with self.assertRaises(ValueError):
            Customer(name="Jan", city="<img src=x onerror=alert(1)>", age=25)

    #testy loan
    def test_valid_loan(self):
        loan = Loan(
            customer_name="Mariusz Pudzianowski",
            book_name="Wspaniala Ksiazka",
            loan_date=datetime(2026, 11, 1),
            return_date=datetime(2026, 11, 6),
            original_author="Wspanialy Autor",
            original_year_published=2008,
            original_book_type="5days"
        )
        self.assertEqual(loan.customer_name, "Mariusz Pudzianowski")

    def test_invalid_loan_xss(self):
        with self.assertRaises(ValueError):
            Loan(
                customer_name="<svg onload=alert(1)>",
                book_name="Wspaniala Ksiazka",
                loan_date=datetime(2026, 11, 1),
                return_date=datetime(2026, 11, 6),
                original_author="Wspanialy Autor",
                original_year_published=2008,
                original_book_type="5days"
            )

if __name__ == '__main__':
    unittest.main()