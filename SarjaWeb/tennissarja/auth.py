from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import Pelaaja

auth = Blueprint('auth', __name__)

# Kirjautumissivu
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        emailf = request.form.get('email')
        password = request.form.get('password')
        print(emailf)
        pelaaja = Pelaaja.query.filter_by(email=emailf).first()
        print(pelaaja)
        if pelaaja:
            if check_password_hash(pelaaja.password, password):
                flash('Logged in successfully!', category='success')
                login_user(pelaaja, remember=True)
                return redirect(url_for('player.sarjataulukko'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html')

# Rekisteröintisivu
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nimi = request.form.get('nimi')
        email = request.form.get('email')
        taso = request.form.get('taso')
        puhelin = request.form.get('puhelin')
        aktiivinen = True
        admin = False
        password1 = request.form.get('password')
        password2 = request.form.get('password2')

        pelaaja = Pelaaja.query.filter_by(email=email).first()
        print(pelaaja)
        if pelaaja:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(nimi) < 4:
            flash('Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            uusi_pelaaja = Pelaaja(
                nimi=nimi,
                email=email,
                puhelin=puhelin,
                taso=taso,
                aktiivinen=aktiivinen,
                admin=admin,
                password=generate_password_hash(password1, method='pbkdf2:sha256', salt_length=8)
            )
            db.session.add(uusi_pelaaja)
            db.session.commit()
            # login_user(uusi_pelaaja, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Päivityssivu
@auth.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    if request.method == 'POST':
        nimi = request.form.get('nimi')
        email = request.form.get('email')
        puhelin = request.form.get('puhelin')
        aktiivinen = request.form.get('aktiivisuus') == 'True'
        taso = request.form.get('taso')
        password = request.form.get('password')

        pelaaja = current_user
        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(nimi) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password and len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            pelaaja.nimi = nimi
            pelaaja.email = email
            pelaaja.puhelin = puhelin
            pelaaja.aktiivinen = aktiivinen
            if taso:
                pelaaja.taso = taso
            if password:
                pelaaja.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

            db.session.commit()
            flash('Your account has been updated!', category='success')
            return redirect(url_for('auth.update'))

    return render_template('update.html', user=current_user)

# Salasanan palautus
@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('forgot_password.html')