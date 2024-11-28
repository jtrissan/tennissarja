from datetime import datetime, date
from . import db
from .models import Pelaaja, Kausi, Sarjakierros, LohkojenPelaajat, Ottelu

def hae_aktiiviset_pelaajat():
    return Pelaaja.query.filter_by(aktiivinen=True).order_by(Pelaaja.taso).all()

def tallenna_lohkojako_sarjakierrokseksi(lohkot):
    kausi = Kausi.query.filter_by(nimi='2024').first()
    if not kausi:
        kausi = Kausi(nimi='2024', alkupaiva=date(2024, 1, 1), loppupaiva=date(2024, 12, 31))
        db.session.add(kausi)
        db.session.commit()

    sarjakierros = Sarjakierros(kierros_numero=1, kausi_id=kausi.id)
    db.session.add(sarjakierros)
    db.session.commit()

    for lohko_numero, lohko in enumerate(lohkot, start=1):
        for pelaaja in lohko:
            lohkojen_pelaaja = LohkojenPelaajat(sarjakierros_id=sarjakierros.id, lohko_numero=lohko_numero, pelaaja_id=pelaaja.id)
            db.session.add(lohkojen_pelaaja)
    db.session.commit()

def pisteyta_ottelu(era1_p1, era1_p2, era2_p1, era2_p2, era3_p1, era3_p2):
    p1_pisteet = 1  # Osallistumisesta
    p2_pisteet = 1  # Osallistumisesta

    # Ensimmäinen erä
    if era1_p1 > era1_p2:
        if era1_p1 >= 6 and (era1_p1 - era1_p2) >= 2:
            p1_pisteet += 2
        elif era1_p1 == 7 and era1_p2 == 6:
            p1_pisteet += 2
        else:
            p1_pisteet += 1
    elif era1_p2 > era1_p1:
        if era1_p2 >= 6 and (era1_p2 - era1_p1) >= 2:
            p2_pisteet += 2
        elif era1_p2 == 7 and era1_p1 == 6:
            p2_pisteet += 2
        else:
            p2_pisteet += 1
    else:
        p1_pisteet += 0.5
        p2_pisteet += 0.5

    # Toinen erä
    if era2_p1 > era2_p2:
        if era2_p1 >= 6 and (era2_p1 - era2_p2) >= 2:
            p1_pisteet += 2
        elif era2_p1 == 7 and era2_p2 == 6:
            p1_pisteet += 2
        else:
            p1_pisteet += 1
    elif era2_p2 > era2_p1:
        if era2_p2 >= 6 and (era2_p2 - era2_p1) >= 2:
            p2_pisteet += 2
        elif era2_p2 == 7 and era2_p1 == 6:
            p2_pisteet += 2
        else:
            p2_pisteet += 1
    else:
        p1_pisteet += 0.5
        p2_pisteet += 0.5

    # Kolmas erä (super tiebreak)
    if era3_p1 is not None and era3_p2 is not None:
        if era3_p1 > era3_p2:
            if era3_p1 >= 10 and (era3_p1 - era3_p2) >= 2:
                p1_pisteet += 2
            else:
                p1_pisteet += 1
        elif era3_p2 > era3_p1:
            if era3_p2 >= 10 and (era3_p2 - era3_p1) >= 2:
                p2_pisteet += 2
            else:
                p2_pisteet += 1
        else:
            p1_pisteet += 0.5
            p2_pisteet += 0.5

    return p1_pisteet, p2_pisteet

def tallenna_ottelu(pelaaja1_id, pelaaja2_id, era1_p1, era1_p2, era2_p1, era2_p2, era3_p1, era3_p2, sarjakierros_id, lohko_numero):
    p1_pisteet, p2_pisteet = pisteyta_ottelu(era1_p1, era1_p2, era2_p1, era2_p2, era3_p1, era3_p2)
    ottelu = Ottelu(
        pelaaja1_id=pelaaja1_id,
        pelaaja2_id=pelaaja2_id,
        era1_p1=era1_p1,
        era1_p2=era1_p2,
        era2_p1=era2_p1,
        era2_p2=era2_p2,
        era3_p1=era3_p1,
        era3_p2=era3_p2,
        p1_pisteet=p1_pisteet,
        p2_pisteet=p2_pisteet,
        sarjakierros_id=sarjakierros_id,
        lohko_numero=lohko_numero,
        ottelun_aika=datetime.now()
    )
    db.session.add(ottelu)

    # Päivitä pelaajien pisteet lohkojen_pelaajat-taulussa
    pelaaja1_lohko = LohkojenPelaajat.query.filter_by(pelaaja_id=pelaaja1_id, sarjakierros_id=sarjakierros_id).first()
    pelaaja2_lohko = LohkojenPelaajat.query.filter_by(pelaaja_id=pelaaja2_id, sarjakierros_id=sarjakierros_id).first()

    pelaaja1_lohko.pisteet += p1_pisteet
    pelaaja2_lohko.pisteet += p2_pisteet

    db.session.commit()

def jaa_pelaajat_uudelle_kierrokselle():
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

    # Vaihda peräkkäisissä lohkoissa kaksi huonointa ja kaksi parasta
    lohko_numerot = sorted(lohkot_jarjestetty.keys())
    for i in range(0, len(lohko_numerot) - 1, 2):
        lohko1 = lohkot_jarjestetty[lohko_numerot[i]]
        lohko2 = lohkot_jarjestetty[lohko_numerot[i + 1]]
        lohko1[-2:], lohko2[:2] = lohko2[:2], lohko1[-2:]

    # Luo uusi sarjakierros
    uusi_sarjakierros = Sarjakierros(kierros_numero=uusin_sarjakierros.kierros_numero + 1, kausi_id=uusin_sarjakierros.kausi_id)
    db.session.add(uusi_sarjakierros)
    db.session.commit()

    # Luo uusi lohkojako pelaajien menestyksen perusteella
    kaikki_pelaajat = []
    for lohko_numero in lohko_numerot:
        kaikki_pelaajat.extend(lohkot_jarjestetty[lohko_numero])

    # Lisää aktiiviset pelaajat, jotka eivät olleet mukana edellisellä sarjakierroksella
    aktiiviset_pelaajat = Pelaaja.query.filter_by(aktiivinen=True).all()
    mukana_olevat_pelaajat = {pelaaja.pelaaja_id for pelaaja in kaikki_pelaajat}
    uudet_pelaajat = [pelaaja for pelaaja in aktiiviset_pelaajat if pelaaja.id not in mukana_olevat_pelaajat]

    for uusi_pelaaja in uudet_pelaajat:
        viimeisin_lohko = LohkojenPelaajat.query.filter_by(pelaaja_id=uusi_pelaaja.id).order_by(LohkojenPelaajat.sarjakierros_id.desc()).first()
        if viimeisin_lohko:
            viimeisin_lohko_numero = viimeisin_lohko.lohko_numero
        else:
            viimeisin_lohko_numero = max(lohko_numerot) + 1
        kaikki_pelaajat.append(LohkojenPelaajat(pelaaja_id=uusi_pelaaja.id, lohko_numero=viimeisin_lohko_numero, sarjakierros_id=uusi_sarjakierros.id))

    # Järjestä pelaajat uudelleen lohkojärjestyksessä
    kaikki_pelaajat.sort(key=lambda x: (x.lohko_numero, x.pisteet), reverse=True)

    # Jaa pelaajat uusiksi lohkoiksi
    uudet_lohkot = []
    for i in range(0, len(kaikki_pelaajat), 5):
        uudet_lohkot.append(kaikki_pelaajat[i:i + 5])

    # Tarkista viimeisen lohkon pelaajamäärä
    if len(uudet_lohkot) > 1:
        viimeinen_lohko = uudet_lohkot[-1]
        toiseksi_viimeinen_lohko = uudet_lohkot[-2]
        if len(viimeinen_lohko) in [1, 2]:
            toiseksi_viimeinen_lohko.extend(viimeinen_lohko)
            uudet_lohkot.pop()

    # Tallenna uusi lohkojako
    for lohko_numero, lohko in enumerate(uudet_lohkot, start=1):
        for pelaaja in lohko:
            lohkojen_pelaaja = LohkojenPelaajat(sarjakierros_id=uusi_sarjakierros.id, lohko_numero=lohko_numero, pelaaja_id=pelaaja.pelaaja_id)
            db.session.add(lohkojen_pelaaja)
    db.session.commit()