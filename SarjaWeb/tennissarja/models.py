from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from . import db

class Pelaaja(UserMixin, db.Model):
    __tablename__ = 'pelaajat'
    
    id = db.Column(db.Integer, primary_key=True)
    nimi = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    taso = db.Column(db.String(50), nullable=False)
    aktiivinen = db.Column(db.Boolean, default=True)
    puhelin = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(150), nullable=False)
    # Suhde LohkojenPelaajat-malliin
    lohkot_suhde = db.relationship('LohkojenPelaajat', back_populates='pelaaja')
    # Suhde Ottelu-malliin
    ottelut_pelaajana1 = db.relationship('Ottelu', foreign_keys='Ottelu.pelaaja1_id', back_populates='pelaaja1')
    ottelut_pelaajana2 = db.relationship('Ottelu', foreign_keys='Ottelu.pelaaja2_id', back_populates='pelaaja2')

    def __repr__(self):
        return f"<Pelaaja id={self.id}, nimi={self.nimi}, email={self.email}, puhelin={self.puhelin}, taso={self.taso}>"

class LohkojenPelaajat(db.Model):
    __tablename__ = 'lohkojen_pelaajat'
    
    id = db.Column(db.Integer, primary_key=True)
    sarjakierros_id = db.Column(db.Integer, db.ForeignKey('sarjakierrokset.id', ondelete='CASCADE'))
    lohko_numero = db.Column(db.Integer, nullable=False)
    pelaaja_id = db.Column(db.Integer, db.ForeignKey('pelaajat.id', ondelete='CASCADE'))
    pisteet = db.Column(db.Float, default=0)
    # Suhde Pelaaja-malliin
    pelaaja = db.relationship('Pelaaja', back_populates='lohkot_suhde')
    sarjakierros = db.relationship('Sarjakierros', back_populates='lohkot')

    def __repr__(self):
        return f"<LohkojenPelaajat id={self.id}, sarjakierros_id={self.sarjakierros_id}, lohko_numero={self.lohko_numero}, pisteet={self.pisteet}>"

class Ottelu(db.Model):
    __tablename__ = 'ottelut'

    id = db.Column(db.Integer, primary_key=True)
    sarjakierros_id = db.Column(db.Integer, db.ForeignKey('sarjakierrokset.id', ondelete='CASCADE'))
    lohko_numero = db.Column(db.Integer, nullable=False)
    pelaaja1_id = db.Column(db.Integer, db.ForeignKey('pelaajat.id', ondelete='CASCADE'))
    pelaaja2_id = db.Column(db.Integer, db.ForeignKey('pelaajat.id', ondelete='CASCADE'))
    era1_p1 = db.Column(db.Integer, nullable=True)
    era1_p2 = db.Column(db.Integer, nullable=True)
    era2_p1 = db.Column(db.Integer, nullable=True)
    era2_p2 = db.Column(db.Integer, nullable=True)
    era3_p1 = db.Column(db.Integer, nullable=True)
    era3_p2 = db.Column(db.Integer, nullable=True)
    p1_pisteet = db.Column(db.Float, nullable=True)
    p2_pisteet = db.Column(db.Float, nullable=True)
    ottelun_aika = db.Column(db.DateTime, nullable=False)

    sarjakierros = relationship('Sarjakierros', back_populates='ottelut')
    pelaaja1 = relationship('Pelaaja', foreign_keys=[pelaaja1_id], back_populates='ottelut_pelaajana1')
    pelaaja2 = relationship('Pelaaja', foreign_keys=[pelaaja2_id], back_populates='ottelut_pelaajana2')

    def __repr__(self):
        return f"<Ottelu id={self.id}, pelaaja1_id={self.pelaaja1_id}, pelaaja2_id={self.pelaaja2_id}, lohko_numero={self.lohko_numero}>"

class Sarjakierros(db.Model):
    __tablename__ = 'sarjakierrokset'

    id = db.Column(db.Integer, primary_key=True)
    kausi_id = db.Column(db.Integer, db.ForeignKey('kausi.id', ondelete='CASCADE'))
    kierros_numero = db.Column(db.Integer, nullable=False)

    lohkot = relationship('LohkojenPelaajat', back_populates='sarjakierros')
    ottelut = relationship('Ottelu', back_populates='sarjakierros')

    def __repr__(self):
        return f"<Sarjakierros id={self.id}, kausi_id={self.kausi_id}, kierros_numero={self.kierros_numero}>"

class Kausi(db.Model):
    __tablename__ = 'kausi'

    id = db.Column(db.Integer, primary_key=True)
    nimi = db.Column(db.String(100), nullable=False)
    alkupaiva = db.Column(db.Date, nullable=False)
    loppupaiva = db.Column(db.Date, nullable=False)

    sarjakierrokset = relationship('Sarjakierros', backref='kausi', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Kausi id={self.id}, nimi={self.nimi}, alkupaiva={self.alkupaiva}, loppupaiva={self.loppupaiva}>"

# Tietokannan alustaminen
# with app.app_context():
#    db.create_all()  # Luo tietokannan ja taulut
#    print("Tietokanta alustettu")