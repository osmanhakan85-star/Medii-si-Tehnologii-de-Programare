#!/usr/bin/env python3
"""
Script pentru initializarea bazei de date SQLite.
Creaza fisierul database.db, tabela 'suporteri' si insereaza date de test.
"""

import sqlite3
from datetime import date, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def init_db():
    # Conectam la baza de date (va crea fisierul daca nu exista)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cream tabela suporteri cu campurile cerute
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suporteri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nr_legitimatie TEXT NOT NULL UNIQUE,
        nume TEXT NOT NULL,
        prenume TEXT NOT NULL,
        email TEXT NOT NULL,
        telefon TEXT NOT NULL,
        tip_abonament TEXT NOT NULL,
        data_inceput TEXT NOT NULL,
        data_expirare TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')

    # Inseram date de test doar daca tabela e goala
    cursor.execute('SELECT COUNT(*) FROM suporteri')
    count = cursor.fetchone()[0]
    if count == 0:
        today = date.today()
        sample = [
            ('LEG-1001', 'Ionescu', 'Andrei', 'andrei.ionescu@example.com', '0712345678', 'Standard', str(today), str(today.replace(year=today.year+1)), 'Activ'),
            ('LEG-1002', 'Popescu', 'Maria', 'maria.popescu@example.com', '0723456789', 'Premium', str(today - timedelta(days=30)), str(today.replace(year=today.year+1)), 'Activ'),
            ('LEG-1003', 'Georgescu', 'Vlad', 'vlad.georgescu@example.com', '0734567890', 'VIP', str(today), str(today + timedelta(days=180)), 'Activ'),
            ('LEG-1004', 'Stan', 'Elena', 'elena.stan@example.com', '0745678901', 'Standard', str(today - timedelta(days=400)), str(today - timedelta(days=35)), 'Expirat'),
            ('LEG-1005', 'Niculae', 'Radu', 'radu.niculae@example.com', '0756789012', 'Premium', str(today - timedelta(days=10)), str(today + timedelta(days=355)), 'Activ')
        ]
        cursor.executemany('''
        INSERT INTO suporteri (nr_legitimatie, nume, prenume, email, telefon, tip_abonament, data_inceput, data_expirare, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample)
        print('Inserate date de test in tabela suporteri.')
    else:
        print('Tabela suporteri contine deja date. Nu se insereaza sample.')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print(f'Baza de date initializata la: {DB_PATH}')
