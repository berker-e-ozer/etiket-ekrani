"""Yalnizca yerel gelistirme sunucusu. Ana sisteme tasinmaz."""
from pathlib import Path

from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader

from routes_etiket_ekrani import bp
from services.etiket_ekrani_service import init_schema

KOK = Path(__file__).resolve().parent

app = Flask(__name__)
# templates/ modulun sablonlari; dev/ yalnizca gelistirme icin base.html
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(str(KOK / "templates")),
    FileSystemLoader(str(KOK / "dev")),
])
app.register_blueprint(bp)
init_schema()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
