from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from . import db
from .models import Pelaaja, Sarjakierros, LohkojenPelaajat
from .services import hae_aktiiviset_pelaajat, tallenna_lohkojako_sarjakierrokseksi, jaa_pelaajat_uudelle_kierrokselle
import os

admin = Blueprint('admin', __name__)

# Pääsivu
@admin.route('/')
@login_required
def admin_dashboard():
    return render_template('admin.html')

# Sarjataulukko
@admin.route('/sarjataulukko')
@login_required
def sarjataulukko():
    # Hae uusin sarjakierros
    uusin_sarjakierros = Sarjakierros.query.order_by(Sarjakierros.kierros_numero.desc()).first()
    sarjakierros_id = uusin_sarjakierros.id

    # Hae lohkojen pelaajat ja pisteet
    lohkot = LohkojenPelaajat.query.filter_by(sarjakierros_id=sarjakierros_id).all()

    # Järjestä lohkot lohkon numeron mukaan
    lohkot_jarjestetty = {}
    for lohko in lohkot:
        if lohko.lohko_numero not in lohkot_jarjestetty:
            lohkot_jarjestetty[lohko.lohko_numero] = []
        lohkot_jarjestetty[lohko.lohko_numero].append(lohko)

    # Järjestä pelaajat pisteiden mukaan
    for lohko_numero in lohkot_jarjestetty:
        lohkot_jarjestetty[lohko_numero].sort(key=lambda x: x.pisteet, reverse=True)

    return render_template('sarjataulukko.html', lohkot=lohkot_jarjestetty)

# Pelaajien hallinta
@admin.route('/players', methods=['GET', 'POST'])
@login_required
def players():
    pelaajat = Pelaaja.query.all()
    return render_template('playerlist.html', pelaajat=pelaajat)

@admin.route('/jaa-lohkot-uudelle-kierrokselle', methods=['POST'])
@login_required
def jaa_lohkot_uudelle_kierrokselle():
    jaa_pelaajat_uudelle_kierrokselle()
    flash("Lohkojako tallennettu uudelle kierrokselle.", "success")
    return redirect(url_for('admin.sarjataulukko'))

@admin.route('/lohkojako')
@login_required
def lohkojako():
    # Hae uusin sarjakierros
    uusin_sarjakierros = Sarjakierros.query.order_by(Sarjakierros.kierros_numero.desc()).first()
    sarjakierros_id = uusin_sarjakierros.id

    # Hae lohkojen pelaajat ja pisteet
    lohkot = LohkojenPelaajat.query.filter_by(sarjakierros_id=sarjakierros_id).all()

    # Järjestä lohkot lohkon numeron mukaan
    lohkot_jarjestetty = {}
    for lohko in lohkot:
        if lohko.lohko_numero not in lohkot_jarjestetty:
            lohkot_jarjestetty[lohko.lohko_numero] = []
        lohkot_jarjestetty[lohko.lohko_numero].append(lohko)

    # Järjestä pelaajat pisteiden mukaan
    for lohko_numero in lohkot_jarjestetty:
        lohkot_jarjestetty[lohko_numero].sort(key=lambda x: x.pisteet, reverse=True)

    # Hae aktiiviset pelaajat, jotka eivät ole mukana viimeisimmässä sarjakierroksessa
    aktiiviset_pelaajat = Pelaaja.query.filter_by(aktiivinen=True).all()
    mukana_olevat_pelaajat = {lohko.pelaaja_id for lohko in lohkot}
    uudet_pelaajat = [pelaaja for pelaaja in aktiiviset_pelaajat if pelaaja.id not in mukana_olevat_pelaajat]

    return render_template('lohkojako.html', lohkot=lohkot_jarjestetty, uudet_pelaajat=uudet_pelaajat, enumerate=enumerate)