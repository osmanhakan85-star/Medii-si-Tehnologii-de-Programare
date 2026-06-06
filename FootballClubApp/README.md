# Sistem de Gestiune a Suporterilor Abonati ai unui Club de Fotbal

Proiect universitar pentru materia Medii si Tehnologii de Programare.

## Descriere

Aplicatie simpla in `Flask` care permite administratorului sa gestioneze suporterii abonati ai unui club: autentificare, vizualizare, adaugare, editare, cautare si stergere.

## Tehnologii

- Backend: Python 3, Flask
- Baza de date: SQLite
- Autentificare: fisier XML (`users.xml`)
- Frontend: HTML5, CSS3, Jinja2 (fara JavaScript frameworks)

## Structura proiect

- `app.py` - aplicatia Flask
- `init_db.py` - script pentru initializarea bazei de date si inserarea datelor de test
- `database.db` - fisier baza de date SQLite (creat de `init_db.py`)
- `users.xml` - fisier XML cu credentiale admin
- `templates/` - sabloane Jinja2
- `static/` - stiluri si logo

## Baza de date

Tabela `suporteri` contine campurile:

- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `nr_legitimatie` TEXT NOT NULL UNIQUE
- `nume` TEXT NOT NULL
- `prenume` TEXT NOT NULL
- `email` TEXT NOT NULL
- `telefon` TEXT NOT NULL
- `tip_abonament` TEXT NOT NULL (Standard, Premium, VIP)
- `data_inceput` TEXT NOT NULL (YYYY-MM-DD)
- `data_expirare` TEXT NOT NULL (YYYY-MM-DD)
- `status` TEXT NOT NULL (Activ, Expirat, Suspendat)

`init_db.py` creeaza tabela si insereaza 5 inregistrari de test la prima rulare.

## Functionalitati

- Autentificare administrator (citita din `users.xml`)
- Vizualizare toti suporterii pe dashboard
- Cautare dupa `nume`, `prenume` sau `nr_legitimatie`
- Adaugare suporter cu validari complete
- Editare suporter cu validari si pre-populare
- Stergere suporter cu pagina de confirmare
- Deconectare (logout)

## Instalare si rulare

1. Instalati dependintele:

```bash
pip install -r requirements.txt
```

2. Initializati baza de date (va crea `database.db` si va popula datele de test):

```bash
python init_db.py
```

3. Porniti aplicatia:

```bash
python app.py
```

Accesati `http://127.0.0.1:5000` si autentificati-va cu user: `admin`, parola: `admin123`.

## Autentificarea prin XML

Credentialele administratorului sunt stocate in fisierul `users.xml` in format XML. Aplicatia citeste fisierul cu `xml.etree.ElementTree` si verifica daca username si parola trimise coincid cu una din intrari. Dupa autentificare se creeaza o sesiune Flask (`session['user']`) pentru a proteja rutele.

## Utilizarea SQLite

Aplicatia foloseste modulul `sqlite3` din Python. Conexiunea este deschisa cu `sqlite3.connect(database.db)` si se foloseste `row_factory` pentru a accesa coloanele dupa nume. Scriptul `init_db.py` creeaza tabela si insereaza date sample.

## Capturi de ecran

*(Placeholder - adaugati capturi dupa ce rulati aplicatia)*

## Cum sunt satisfacute cerintele universitare

- Formularul de autentificare foloseste `users.xml` (cerinta 1).
- Dashboard-ul afiseaza datele din SQLite (cerinta 2).
- Cautarea este disponibila pe dashboard (cerinta 3).
- Stergerea include pagina de confirmare si sterge din baza de date (cerinta 4).
- Validarea completa a campurilor este implementata in `app.py` (cerinta 5).

## Observatii

Proiectul este conceput pentru a fi clar si usor de inteles, cu comentarii in cod pentru fiecare ruta si operatie pe baza de date. Pentru productie ar fi necesare imbunatatiri de securitate (stocare parole, secret key, CSRF etc.), dar acestea sunt in afara scopului proiectului universitar.
