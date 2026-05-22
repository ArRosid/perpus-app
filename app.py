import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Memuat environment variables dari .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key-12345")

# Ambil Konfigurasi dari Environment Variable
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Validasi environment variables
if not all([DB_USER, DB_PASS, DB_HOST, DB_NAME]):
    raise RuntimeError("ERROR: Harap pastikan file .env telah diisi dengan lengkap!")

# Konfigurasi Database
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model Database (Tabel books)
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)

# Route: Tampilkan Semua Buku
@app.route("/")
def index():
    books = Book.query.all()
    return render_template("index.html", books=books)

# Route: Tambah Buku Baru
@app.route("/add", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")
    isbn = request.form.get("isbn")

    if not title or not author or not isbn:
        flash("Semua kolom input wajib diisi!", "danger")
        return redirect(url_for("index"))

    # Cek duplikat ISBN
    existing_book = Book.query.filter_by(isbn=isbn).first()
    if existing_book:
        flash(f"Gagal! Buku dengan ISBN {isbn} sudah terdaftar.", "danger")
        return redirect(url_for("index"))

    try:
        new_book = Book(title=title, author=author, isbn=isbn)
        db.session.add(new_book)
        db.session.commit()
        flash("Buku berhasil ditambahkan ke perpustakaan!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Terjadi kesalahan database: {str(e)}", "danger")

    return redirect(url_for("index"))

# Route: Hapus Buku
@app.route("/delete/<int:id>")
def delete_book(id):
    book = Book.query.get(id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
            flash("Buku berhasil dihapus!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal menghapus buku: {str(e)}", "danger")
    else:
        flash("Buku tidak ditemukan!", "danger")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)