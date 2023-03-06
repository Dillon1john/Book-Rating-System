from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "Hello World"
# CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books-collection.db'
# Optional: But it will silence the depreciation waening in the console
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)
db.sessionmaker(autoflush=True)

##CREATE TABLE
with app.app_context():
    class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        author = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.String(250), nullable=False)

        # Optional: will allow each book object to be identified by its title when printed
        def __repr__(self):
            return f'<Book {self.title}>'


    db.create_all()


    class BookForm(FlaskForm):
        stars = ['⭐️', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐']
        title = StringField("Book Name:", validators=[DataRequired()])
        author = StringField("Book Author:", validators=[DataRequired()])
        rating = SelectField("Rating:", validators=[DataRequired()], choices=stars)
        submit = SubmitField("Add Book")


    class EditRatingForm(FlaskForm):
        stars = ['⭐️', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐']
        rating = SelectField(validators=[DataRequired()], choices=stars)
        submit = SubmitField("Change Rating")


    # all_books = []
    all_books = db.session.query(Book).all()


    @app.route('/')
    def home():
        return render_template('index.html', books=all_books)


    @app.route("/add", methods=["GET", "POST"])
    def add():
        book = {}
        form = BookForm()
        if form.validate_on_submit():
            new_book = Book(title=form.title.data,
                            author=form.author.data,
                            rating=form.rating.data)
            db.session.add(new_book)
            db.session.commit()
            print(all_books)
            return redirect(url_for('home'))
        return render_template('add.html', form=form)


    @app.route("/edit?id=<int:id>", methods=["GET", "POST"])
    def edit(id):
        form = EditRatingForm()
        book = db.session.query(Book).filter_by(id=id).first()
        if form.validate_on_submit():
            db.session.query(Book).filter_by(id=id).update({'rating': form.rating.data})
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('edit.html', form=form, book=book, id=id)

    @app.route("/delete?id=<int:id>")
    def delete(id):
        #DELETE A RECORD BY ID
        book_to_delete = db.session.query(Book).get(id)
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect(url_for('home'))

    if __name__ == "__main__":
        app.run(debug=True)
