from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Pelaaja, Ottelu, Sarjakierros, LohkojenPelaajat
from .services import pisteyta_ottelu, tallenna_ottelu

player = Blueprint('player', __name__)

# Esittelysivu
@player.route('/esittely')
def esittely():
    return render_template('esittely.html')

# Sarjataulukko
@player.route('/sarjataulukko')
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

    # Järjestä pelaajat pisteiden mukaan ja lisää ottelujen määrä
    for lohko_numero in lohkot_jarjestetty:
        for pelaaja in lohkot_jarjestetty[lohko_numero]:
            pelaaja.ottelut_maara = Ottelu.query.filter(
                ((Ottelu.pelaaja1_id == pelaaja.pelaaja_id) | (Ottelu.pelaaja2_id == pelaaja.pelaaja_id)),
                Ottelu.sarjakierros_id == sarjakierros_id,
                Ottelu.lohko_numero == lohko_numero
            ).count()
        lohkot_jarjestetty[lohko_numero].sort(key=lambda x: x.pisteet, reverse=True)

    return render_template('sarjataulukko.html', lohkot=lohkot_jarjestetty)

# Ottelutuloksen syöttäminen
@player.route('/input', methods=['GET', 'POST'])
@login_required
def input():
    if request.method == 'POST':
        try:
            pelaaja1_id = current_user.id
            pelaaja2_id = request.form.get('pelaaja2_id')
            era1_p1 = int(request.form.get('era1_p1'))
            era1_p2 = int(request.form.get('era1_p2'))
            era2_p1 = request.form.get('era2_p1')
            era2_p2 = request.form.get('era2_p2')
            era3_p1 = request.form.get('era3_p1')
            era3_p2 = request.form.get('era3_p2')

            if era2_p1:
                era2_p1 = int(era2_p1)
            if era2_p2:
                era2_p2 = int(era2_p2)
            if era3_p1:
                era3_p1 = int(era3_p1)
            if era3_p2:
                era3_p2 = int(era3_p2)

            # Hae uusin sarjakierros
            uusin_sarjakierros = Sarjakierros.query.order_by(Sarjakierros.kierros_numero.desc()).first()
            sarjakierros_id = uusin_sarjakierros.id

            # Hae pelaajan lohko meneillään olevalla kierroksella
            lohko = LohkojenPelaajat.query.filter_by(pelaaja_id=pelaaja1_id, sarjakierros_id=sarjakierros_id).first()
            lohko_id = lohko.lohko_numero

            tallenna_ottelu(pelaaja1_id, pelaaja2_id, era1_p1, era1_p2, era2_p1, era2_p2, era3_p1, era3_p2, sarjakierros_id, lohko_id)
            flash('Ottelutulos tallennettu!', category='success')
            return redirect(url_for('player.input'))
        except (TypeError, ValueError) as e:
            flash('Virheellinen syöte. Varmista, että kaikki kentät on täytetty oikein.', category='error')

    # Hae uusin sarjakierros
    uusin_sarjakierros = Sarjakierros.query.order_by(Sarjakierros.kierros_numero.desc()).first()
    sarjakierros_id = uusin_sarjakierros.id

    # Hae pelaajan lohko meneillään olevalla kierroksella
    lohko = LohkojenPelaajat.query.filter_by(pelaaja_id=current_user.id, sarjakierros_id=sarjakierros_id).first()
    lohko_id = lohko.lohko_numero

    # Hae saman lohkon pelaajat, joita vastaan pelaaja ei ole vielä pelannut
    pelatut_ottelut = Ottelu.query.filter(
        (Ottelu.pelaaja1_id == current_user.id) | (Ottelu.pelaaja2_id == current_user.id),
        Ottelu.sarjakierros_id == sarjakierros_id,
        Ottelu.lohko_numero == lohko_id
    ).all()
    pelatut_pelaajat = {ottelu.pelaaja1_id for ottelu in pelatut_ottelut} | {ottelu.pelaaja2_id for ottelu in pelatut_ottelut}
    pelatut_pelaajat.discard(current_user.id)

    saman_lohkon_pelaajat = LohkojenPelaajat.query.filter(
        LohkojenPelaajat.sarjakierros_id == sarjakierros_id,
        LohkojenPelaajat.lohko_numero == lohko_id,
        LohkojenPelaajat.pelaaja_id != current_user.id,
        ~LohkojenPelaajat.pelaaja_id.in_(pelatut_pelaajat)
    ).all()

    return render_template('input.html', saman_lohkon_pelaajat=saman_lohkon_pelaajat)

# Index page
@player.route('/')
def index():
    return render_template('index.html')