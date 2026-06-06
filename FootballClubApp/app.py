"""
Aplicatie Flask pentru gestionarea suporterilor abonati.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import xml.etree.ElementTree as ET
from functools import wraps
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'database.db')
USERS_XML = os.path.join(BASE_DIR, 'users.xml')

app = Flask(__name__)
# Cheie simpla pentru sesiune - pentru un proiect universitar este suficienta
app.secret_key = 'schimba_acesta_cu_una_secreta_in_proiect_real'


def get_db_connection():
    # Deschidem conexiunea la baza de date si setam row_factory pentru acces prin nume de coloana
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def citeste_credentile_xml(username, password):
    # Citim fisierul XML si verificam daca exista un utilizator cu username/parola date
    try:
        tree = ET.parse(USERS_XML)
        root = tree.getroot()
        for u in root.findall('utilizator'):
            user = u.find('username').text
            pwd = u.find('password').text
            if user == username and pwd == password:
                return True
    except Exception:
        # Daca fisierul nu poate fi citit, consideram autentificarea esuata
        return False
    return False


def login_required(f):
    # Decorator pentru protejarea rutelor: verifica daca exista sesiune activa
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Trebuie sa va autentificati pentru a accesa aceasta pagina.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def validare_suporter(form, is_edit=False, current_id=None):
    # Functie de validare a campurilor formularului pentru adaugare/actualizare
    # Returneaza dict de erori; daca e gol, validarea a trecut
    erori = {}

    nr = form.get('nr_legitimatie', '').strip()
    nume = form.get('nume', '').strip()
    prenume = form.get('prenume', '').strip()
    email = form.get('email', '').strip()
    telefon = form.get('telefon', '').strip()
    tip = form.get('tip_abonament', '').strip()
    data_inceput = form.get('data_inceput', '').strip()
    data_expirare = form.get('data_expirare', '').strip()
    status = form.get('status', '').strip()

    # Validam nr_legitimatie: nu poate fi gol
    if not nr:
        erori['nr_legitimatie'] = 'Numarul legitimatiei nu poate fi gol.'
    else:
        # Verificam unicitatea in baza de date
        conn = get_db_connection()
        cur = conn.cursor()
        if is_edit:
            cur.execute('SELECT id FROM suporteri WHERE nr_legitimatie = ? AND id != ?', (nr, current_id))
        else:
            cur.execute('SELECT id FROM suporteri WHERE nr_legitimatie = ?', (nr,))
        exista = cur.fetchone()
        conn.close()
        if exista:
            erori['nr_legitimatie'] = 'Acest numar de legitimatie exista deja in baza de date.'

    # Nume si prenume obligatorii
    if not nume:
        erori['nume'] = 'Numele nu poate fi gol.'
    if not prenume:
        erori['prenume'] = 'Prenumele nu poate fi gol.'

    # Validare email simpla
    if not email:
        erori['email'] = 'Email-ul nu poate fi gol.'
    elif '@' not in email or '.' not in email:
        erori['email'] = 'Email-ul pare invalid.'

    # Telefon: doar cifre, min 10
    if not telefon:
        erori['telefon'] = 'Telefonul nu poate fi gol.'
    elif not telefon.isdigit():
        erori['telefon'] = 'Telefonul trebuie sa contina doar cifre.'
    elif len(telefon) < 10:
        erori['telefon'] = 'Telefonul trebuie sa aiba minim 10 cifre.'

    # Abonament si status trebuie sa fie selectate
    if tip not in ('Standard', 'Premium', 'VIP'):
        erori['tip_abonament'] = 'Selectati un tip de abonament valid.'
    if status not in ('Activ', 'Expirat', 'Suspendat'):
        erori['status'] = 'Selectati un status valid.'

    # Validare date: format YYYY-MM-DD si expirare > inceput
    try:
        di = datetime.strptime(data_inceput, '%Y-%m-%d')
    except Exception:
        erori['data_inceput'] = 'Data inceput trebuie in format YYYY-MM-DD.'
        di = None
    try:
        de = datetime.strptime(data_expirare, '%Y-%m-%d')
    except Exception:
        erori['data_expirare'] = 'Data expirare trebuie in format YYYY-MM-DD.'
        de = None

    if di and de:
        if de <= di:
            erori['data_expirare'] = 'Data expirare trebuie sa fie dupa data de inceput.'

    return erori


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Ruta pentru autentificare; citeste datele din users.xml
    # Verificam daca exista un logo JPEG in folderul static pentru a-l afisa
    custom_logo = None
    for fname in ('logo.jpg', 'logo.jpeg', 'custom_logo.jpg', 'custom_logo.jpeg'):
        potential = os.path.join(BASE_DIR, 'static', fname)
        if os.path.exists(potential):
            # vom trimite calea relativa catre template
            custom_logo = f'/static/{fname}'
            break

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if citeste_credentile_xml(username, password):
            # Setam sesiunea Flask si redirectionam catre dashboard
            session['user'] = username
            flash('Autentificare reusita.', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Afișam mesaj prietenos de eroare la date incorecte
            flash('Username sau parola incorecte. Incercati din nou.', 'error')
            return render_template('login.html', custom_logo=custom_logo)
    else:
        return render_template('login.html', custom_logo=custom_logo)


@app.route('/logout')
def logout():
    # Ruta de logout: distruge sesiunea si redirectioneaza la login
    session.pop('user', None)
    flash('V-ati deconectat.', 'success')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    # Pagina principala redirect catre dashboard
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Afisam toti suporterii sau filtram dupa termenul de cautare
    q = request.args.get('q', '').strip()
    conn = get_db_connection()
    cur = conn.cursor()
    if q:
        # Cautam dupa nume, prenume sau nr_legitimatie
        like = f'%{q}%'
        cur.execute('''
            SELECT * FROM suporteri
            WHERE nume LIKE ? OR prenume LIKE ? OR nr_legitimatie LIKE ?
            ORDER BY id
        ''', (like, like, like))
    else:
        cur.execute('SELECT * FROM suporteri ORDER BY id')
    suporteri = cur.fetchall()
    conn.close()
    return render_template('dashboard.html', suporteri=suporteri, q=q)


@app.route('/adauga', methods=['GET', 'POST'])
@login_required
def adauga_suporter():
    # Ruta pentru adaugarea unui suporter nou
    if request.method == 'POST':
        # Validam datele
        erori = validare_suporter(request.form)
        if erori:
            # Daca exista erori, reafisam formularul cu mesajele
            return render_template('adauga_suporter.html', erori=erori, form=request.form)

        # Daca validarea trece, inseram in baza de date
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO suporteri (nr_legitimatie, nume, prenume, email, telefon, tip_abonament, data_inceput, data_expirare, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['nr_legitimatie'].strip(),
            request.form['nume'].strip(),
            request.form['prenume'].strip(),
            request.form['email'].strip(),
            request.form['telefon'].strip(),
            request.form['tip_abonament'].strip(),
            request.form['data_inceput'].strip(),
            request.form['data_expirare'].strip(),
            request.form['status'].strip()
        ))
        conn.commit()
        conn.close()
        flash('Suporter adaugat cu succes.', 'success')
        return redirect(url_for('dashboard'))
    else:
        # Afisam formularul gol
        return render_template('adauga_suporter.html', erori={}, form={})


@app.route('/editeaza/<int:id>', methods=['GET', 'POST'])
@login_required
def editeaza_suporter(id):
    # Ruta pentru editarea unui suporter existent
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM suporteri WHERE id = ?', (id,))
    suporter = cur.fetchone()
    if not suporter:
        conn.close()
        flash('Suporterul nu a fost gasit.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        erori = validare_suporter(request.form, is_edit=True, current_id=id)
        if erori:
            # Daca exista erori, reafisam formularul cu datele trimise
            conn.close()
            return render_template('editeaza_suporter.html', erori=erori, form=request.form, suporter=suporter)

        # Actualizam inregistrarea
        cur.execute('''
            UPDATE suporteri SET nr_legitimatie = ?, nume = ?, prenume = ?, email = ?, telefon = ?, tip_abonament = ?, data_inceput = ?, data_expirare = ?, status = ?
            WHERE id = ?
        ''', (
            request.form['nr_legitimatie'].strip(),
            request.form['nume'].strip(),
            request.form['prenume'].strip(),
            request.form['email'].strip(),
            request.form['telefon'].strip(),
            request.form['tip_abonament'].strip(),
            request.form['data_inceput'].strip(),
            request.form['data_expirare'].strip(),
            request.form['status'].strip(),
            id
        ))
        conn.commit()
        conn.close()
        flash('Suporter actualizat cu succes.', 'success')
        return redirect(url_for('dashboard'))
    else:
        # Pre-populam formularul cu datele existente
        form = {
            'nr_legitimatie': suporter['nr_legitimatie'],
            'nume': suporter['nume'],
            'prenume': suporter['prenume'],
            'email': suporter['email'],
            'telefon': suporter['telefon'],
            'tip_abonament': suporter['tip_abonament'],
            'data_inceput': suporter['data_inceput'],
            'data_expirare': suporter['data_expirare'],
            'status': suporter['status']
        }
        conn.close()
        return render_template('editeaza_suporter.html', erori={}, form=form, suporter=suporter)


@app.route('/sterge/<int:id>', methods=['GET', 'POST'])
@login_required
def sterge_suporter(id):
    # Ruta pentru stergerea unui suporter: GET - afiseaza confirmarea, POST - sterge
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM suporteri WHERE id = ?', (id,))
    suporter = cur.fetchone()
    if not suporter:
        conn.close()
        flash('Suporterul nu a fost gasit.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Confirmare stergere primita: stergem din baza de date
        cur.execute('DELETE FROM suporteri WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash('Suporter sters cu succes.', 'success')
        return redirect(url_for('dashboard'))
    else:
        # Afisam pagina de confirmare cu detaliile suporterului
        conn.close()
        return render_template('sterge_confirmare.html', suporter=suporter)


if __name__ == '__main__':
    # Pornim aplicatia in mod debug pentru dezvoltare
    app.run(host='0.0.0.0', port=5000, debug=True)
