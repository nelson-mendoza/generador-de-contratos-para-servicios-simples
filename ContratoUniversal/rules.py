"""
Reglas de validación para contratos
Valida datos del formulario antes de generar contrato
"""

import sqlite3
from datetime import datetime
import os

DATABASE = 'contracts.db'

def get_db_connection():
    """Crear conexión a SQLite y crear tablas si no existen"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    # Crear tabla de usuarios para autenticación
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla de contratos
    conn.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            provider_name TEXT NOT NULL,
            provider_phone TEXT NOT NULL,
            provider_rfc TEXT,
            provider_address TEXT,
            client_name TEXT NOT NULL,
            client_phone TEXT NOT NULL,
            client_rfc TEXT,
            client_address TEXT,
            client_email TEXT,
            service_type TEXT NOT NULL,
            service_title TEXT NOT NULL,
            service_description TEXT NOT NULL,
            has_materials BOOLEAN,
            materials_details TEXT,
            pending_quote BOOLEAN,
            payment_structure TEXT NOT NULL,
            payment_timing TEXT NOT NULL,
            total_amount REAL NOT NULL,
            advance_amount REAL,
            remaining_amount REAL,
            payment_method TEXT NOT NULL,
            bank_name TEXT,
            bank_clabe TEXT,
            payment_deadline TEXT NOT NULL,
            penalty_rate TEXT,
            witness_name TEXT,
            include_confidentiality BOOLEAN,
            include_signatures BOOLEAN,
            provider_signature TEXT,
            client_signature TEXT,
            witness_signature TEXT,
            guarantee_days TEXT,
            guarantee_type TEXT,
            guarantee_exclusions TEXT,
            logo TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    return conn

def init_db():
    """Inicializar la base de datos con todas las tablas"""
    conn = get_db_connection()
    conn.close()

def validate_contract(data):
    """
    Validar todos los campos del contrato
    Returns: lista de errores o lista vacía si todo está bien
    """
    errors = []
    
    # Validaciones obligatorias básicas
    if not data.get('provider_name') or len(data['provider_name']) < 3:
        errors.append('Nombre del prestador debe tener al menos 3 caracteres')
    
    if not data.get('client_name') or len(data['client_name']) < 3:
        errors.append('Nombre del cliente debe tener al menos 3 caracteres')
    
    # Validar teléfono (mínimo 10 dígitos)
    client_phone = data.get('client_phone', '').replace(' ', '').replace('-', '')
    if not client_phone.isdigit() or len(client_phone) < 10:
        errors.append('Teléfono del cliente debe tener al menos 10 dígitos')
    
    # Validar descripción del servicio
    if not data.get('service_description') or len(data['service_description']) < 10:
        errors.append('Descripción del servicio debe tener al menos 10 caracteres')
    
    # Validar monto total
    try:
        total_amount = float(data.get('total_amount', 0))
        if total_amount <= 0:
            errors.append('El monto total debe ser mayor a 0')
    except (ValueError, TypeError):
        errors.append('Monto total inválido')
    
    # Validar fecha límite (debe ser futura)
    try:
        deadline = datetime.strptime(data.get('payment_deadline', ''), '%Y-%m-%d')
        if deadline.date() <= datetime.now().date():
            errors.append('La fecha límite debe ser futura')
    except ValueError:
        errors.append('Fecha límite inválida')
    
    # Validaciones condicionales
    
    # Si incluye materiales, se requieren detalles
    if data.get('has_materials') and not data.get('materials_details'):
        errors.append('Debe especificar los materiales incluidos')
    
    # Si es transferencia, se requieren datos bancarios
    if data.get('payment_method') == 'transfer' and not data.get('bank_clabe'):
        errors.append('Debe proporcionar CLABE para transferencia')
    
    # Validar estructura de pagos
    structure = data.get('payment_structure')
    if structure == 'advance':
        try:
            advance = float(data.get('advance_amount', 0))
            remaining = float(data.get('remaining_amount', 0))
            total = float(data.get('total_amount', 0))
            
            if abs((advance + remaining) - total) > 0.01:
                errors.append('Anticipo + Resto debe ser igual al total')
        except (ValueError, TypeError):
            errors.append('Montos de pago inválidos')
    
    # Si incluye firmas, se requieren nombres
    if data.get('include_signatures'):
        if not data.get('provider_signature'):
            errors.append('Nombre requerido para firma del prestador')
        if not data.get('client_signature'):
            errors.append('Nombre requerido para firma del cliente')
    
    # Validar logo (si se subió)
    # Esta validación se hace en el backend con allowed_file()
    
    return errors

def sanitize_input(text):
    """Limpiar input de posibles inyecciones"""
    if not text:
        return ''
    # Eliminar tags HTML básicos
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    return text.strip()
