from flask import Flask, request, render_template
from data_models import db, Author, Book
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.sqlite'
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = datetime.strptime(request.form['birth_date'],
                                       '%Y-%m-%d').date()

        if request.form['date_of_death']:
            date_of_death = datetime.strptime(request.form['date_of_death'],
                                              '%Y-%m-%d').date()
        else:
            date_of_death = None

        author = Author(name=name, birth_date=birth_date,
                        date_of_death=date_of_death)

        db.session.add(author)
        db.session.commit()

        return render_template('add_author.html',
                               message='Author added successfully')
    else:
        return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        book = Book(isbn=isbn, title=title, publication_year=publication_year,
                    author_id=author_id)

        db.session.add(book)
        db.session.commit()

        return render_template('add_book.html',
                               message='Book added successfully',
                               authors=Author.query.all())
    else:
        return render_template('add_book.html', authors=Author.query.all())


@app.route('/', methods=['GET'])
def home():
    query = request.args.get('query')
    sort_by = request.args.get('sort_by', 'title')
    # Default sorting is by title

    if query:
        books = Book.query.filter(Book.title.like(f"%{query}%"))
    else:
        books = Book.query

    if sort_by == 'title':
        books = books.order_by(Book.title)
    elif sort_by == 'author':
        books = books.join(Author).order_by(Author.name)

    books = books.all()

    return render_template('home.html', books=books, sort_by=sort_by)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author_id = book.author_id

    db.session.delete(book)
    db.session.commit()

    author_books = Book.query.filter_by(author_id=author_id).all()

    if not author_books:
        author = Author.query.get(author_id)
        db.session.delete(author)
        db.session.commit()

    message = 'Book deleted successfully!'
    books = Book.query.all()
    return render_template('home.html', books=books, message=message)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
