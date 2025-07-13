import os, psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.environ["DATABASE_URL"]          

def get_conn():
    """
    Devuelve una conexión nueva a la BD de PostgreSQL.
    Usa el string de conexión completo (usuario, pass, host, puerto, base).
    """
    return psycopg2.connect(DATABASE_URL)


DDL = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente   TEXT PRIMARY KEY,
    nombre       TEXT NOT NULL,
    telefono     TEXT,
    direccion    TEXT,
    mail         TEXT
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto  TEXT PRIMARY KEY,
    descripcion  TEXT NOT NULL,
    unidad_base  TEXT NOT NULL,
    precio       NUMERIC(10,0) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido     TEXT PRIMARY KEY,
    id_cliente    TEXT NOT NULL REFERENCES clientes(id_cliente),
    fecha_pedido  TIMESTAMP DEFAULT NOW(),
    fecha_entrega TIMESTAMP,
    estado        TEXT DEFAULT 'pendiente'
);

CREATE TABLE IF NOT EXISTS detalle_pedido (
    id_detalle      SERIAL PRIMARY KEY,
    id_pedido       TEXT REFERENCES pedidos(id_pedido),
    id_producto     TEXT REFERENCES productos(id_producto),
    cantidad        NUMERIC(10,3) NOT NULL CHECK (cantidad > 0),
    precio          NUMERIC(10,0) NOT NULL,
    unidad          TEXT NOT NULL,
    cantidad_real   NUMERIC(10,3) CHECK (cantidad_real > 0)
);

CREATE TABLE IF NOT EXISTS pagos (
    id_pago       SERIAL PRIMARY KEY,
    id_cliente    TEXT REFERENCES clientes(id_cliente),
    fecha_pago    TIMESTAMP DEFAULT NOW(),
    monto_pagado  NUMERIC(12,0),
    medio_pago    TEXT,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS movimientos_cuenta_corriente (
    id_movimiento TEXT PRIMARY KEY,
    id_cliente    TEXT REFERENCES clientes(id_cliente),
    fecha         DATE NOT NULL,
    tipo_mov      TEXT NOT NULL,
    importe       NUMERIC(12,0) NOT NULL,
    forma_pago    TEXT,
    id_remito     INTEGER UNIQUE
);

CREATE TABLE IF NOT EXISTS clientes_cuenta_corriente (
    id_cliente TEXT PRIMARY KEY,
    saldo      NUMERIC(12,0) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS remitos (
    id_remito SERIAL PRIMARY KEY,
    id_pedido TEXT REFERENCES pedidos(id_pedido),
    fecha TIMESTAMP DEFAULT NOW(),
    total NUMERIC(12,0) NOT NULL,
    saldo_anterior NUMERIC(12,0) NOT NULL,
    CONSTRAINT un_remito_por_pedido UNIQUE (id_pedido)
);

CREATE TABLE IF NOT EXISTS detalle_remito (
    id_detalle SERIAL PRIMARY KEY,
    id_remito INTEGER REFERENCES remitos(id_remito),
    id_producto TEXT REFERENCES productos(id_producto),
    cantidad NUMERIC(10,3) NOT NULL,
    precio NUMERIC(12,0) NOT NULL
);


"""


def init_db():
    """
    Ejecuta el DDL una sola vez para crear las tablas si no existen.
    """
    with get_conn() as conn:
        conn.autocommit = True                        
        with conn.cursor() as cur:
            cur.execute(DDL)
