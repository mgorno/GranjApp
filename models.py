import sqlite3, datetime
from pathlib import Path

DB_PATH = Path("database.db")

def get_conn():
    return sqlite3.connect(DB_PATH, isolation_level=None)

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente TEXT PRIMARY KEY,
            nombre     TEXT NOT NULL,
            telefono   TEXT,
            direccion  TEXT,
            mail       TEXT
        );

        CREATE TABLE IF NOT EXISTS productos (
            id_producto TEXT PRIMARY KEY,
            descripcion TEXT NOT NULL,
            unidad_base TEXT,
            precio      REAL
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id_pedido     TEXT PRIMARY KEY,
            id_cliente    TEXT NOT NULL,
            fecha_pedido  TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),
            fecha_entrega TEXT,
            estado        TEXT DEFAULT 'pendiente',
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        );

        CREATE TABLE IF NOT EXISTS detalle_pedido (
            id_detalle  INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pedido   TEXT,
            id_producto TEXT,
            cantidad    INTEGER,
            precio      REAL,
            FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        );

        CREATE TABLE IF NOT EXISTS pagos (
            id_pago      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente   TEXT,
            fecha_pago   TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),
            monto_pagado REAL,
            medio_pago   TEXT,
            observaciones TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        );
        """)
