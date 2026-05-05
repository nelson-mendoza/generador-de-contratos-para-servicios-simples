"""
ContratoUniversal - Generador de Contratos Legales en PDF
Aplicación Flask para crear contratos profesionales de servicios
Incluye autenticación segura con hash de contraseñas
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session, flash
import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

# Importar validaciones
from rules import validate_contract, get_db_connection, init_db

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max
app.secret_key = os.urandom(24)  # Clave secreta para sesiones seguras
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Crear carpeta de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar DB al arrancar (incluye tabla de usuarios)
init_db()

def allowed_file(filename):
    """Verificar si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorador para proteger rutas que requieren login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    """Página principal con el formulario"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos usuarios"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validaciones básicas
        if not username or len(username) < 3:
            flash('El usuario debe tener al menos 3 caracteres.', 'danger')
            return redirect(url_for('register'))
        
        if not password or len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('register'))
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verificar si el usuario ya existe
            existing = cursor.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing:
                flash('El usuario ya existe. Elige otro nombre.', 'danger')
                conn.close()
                return redirect(url_for('register'))
            
            # Hash de contraseña y guardar usuario
            hashed_pw = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                          (username, hashed_pw))
            conn.commit()
            conn.close()
            
            flash('Usuario registrado exitosamente. Ahora inicia sesión.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Error registrando usuario: {str(e)}', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión de usuarios"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Usuario y contraseña requeridos.', 'danger')
            return redirect(url_for('login'))
        
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                # Iniciar sesión
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'¡Bienvenido, {user["username"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Usuario o contraseña incorrectos.', 'danger')
                return redirect(url_for('login'))
                
        except Exception as e:
            flash(f'Error iniciando sesión: {str(e)}', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada exitosamente.', 'info')
    return redirect(url_for('login'))

@app.route('/generate', methods=['POST'])
@login_required
def generate_contract():
    """Generar contrato y guardar en base de datos"""
    
    # Obtener datos del formulario
    data = {
        'provider_name': request.form.get('provider_name', '').strip(),
        'provider_phone': request.form.get('provider_phone', '').strip(),
        'provider_rfc': request.form.get('provider_rfc', '').strip(),
        'provider_address': request.form.get('provider_address', '').strip(),
        'client_name': request.form.get('client_name', '').strip(),
        'client_phone': request.form.get('client_phone', '').strip(),
        'client_rfc': request.form.get('client_rfc', '').strip(),
        'client_address': request.form.get('client_address', '').strip(),
        'client_email': request.form.get('client_email', '').strip(),
        'service_type': request.form.get('service_type', '').strip(),
        'service_title': request.form.get('service_title', '').strip(),
        'service_description': request.form.get('service_description', '').strip(),
        'has_materials': request.form.get('has_materials') == 'on',
        'materials_details': request.form.get('materials_details', '').strip(),
        'pending_quote': request.form.get('pending_quote') == 'on',
        'payment_structure': request.form.get('payment_structure', '').strip(),
        'payment_timing': request.form.get('payment_timing', '').strip(),
        'total_amount': request.form.get('total_amount', '').strip(),
        'advance_amount': request.form.get('advance_amount', '').strip(),
        'remaining_amount': request.form.get('remaining_amount', '').strip(),
        'payment_method': request.form.get('payment_method', '').strip(),
        'bank_name': request.form.get('bank_name', '').strip(),
        'bank_clabe': request.form.get('bank_clabe', '').strip(),
        'payment_deadline': request.form.get('payment_deadline', '').strip(),
        'penalty_rate': request.form.get('penalty_rate', '').strip(),
        'witness_name': request.form.get('witness_name', '').strip(),
        'include_confidentiality': request.form.get('include_confidentiality') == 'on',
        'include_signatures': request.form.get('include_signatures') == 'on',
        'provider_signature': request.form.get('provider_signature', '').strip(),
        'client_signature': request.form.get('client_signature', '').strip(),
        'witness_signature': request.form.get('witness_signature', '').strip(),
        'guarantee_days': request.form.get('guarantee_days', '30').strip(),
        'guarantee_type': request.form.get('guarantee_type', 'defectos de fabricación').strip(),
        'guarantee_exclusions': request.form.get('guarantee_exclusions', 'daños por mal uso').strip(),
    }
    
    # Validar datos
    errors = validate_contract(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400
    
    # Manejar logo subido
    logo_filename = None
    if 'logo' in request.files:
        file = request.files['logo']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Añadir timestamp para evitar duplicados
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            logo_filename = timestamp + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_filename))
    
    data['logo'] = logo_filename
    
    # Guardar en base de datos
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener user_id de la sesión
        user_id = session.get('user_id')
        
        cursor.execute('''
            INSERT INTO contracts (
                user_id,
                provider_name, provider_phone, provider_rfc, provider_address,
                client_name, client_phone, client_rfc, client_address, client_email,
                service_type, service_title, service_description,
                has_materials, materials_details, pending_quote,
                payment_structure, payment_timing, total_amount, advance_amount, remaining_amount,
                payment_method, bank_name, bank_clabe, payment_deadline, penalty_rate,
                witness_name, include_confidentiality, include_signatures,
                provider_signature, client_signature, witness_signature,
                guarantee_days, guarantee_type, guarantee_exclusions,
                logo, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['provider_name'], data['provider_phone'], data['provider_rfc'], data['provider_address'],
            data['client_name'], data['client_phone'], data['client_rfc'], data['client_address'], data['client_email'],
            data['service_type'], data['service_title'], data['service_description'],
            data['has_materials'], data['materials_details'], data['pending_quote'],
            data['payment_structure'], data['payment_timing'], data['total_amount'], data['advance_amount'], data['remaining_amount'],
            data['payment_method'], data['bank_name'], data['bank_clabe'], data['payment_deadline'], data['penalty_rate'],
            data['witness_name'], data['include_confidentiality'], data['include_signatures'],
            data['provider_signature'], data['client_signature'], data['witness_signature'],
            data['guarantee_days'], data['guarantee_type'], data['guarantee_exclusions'],
            data['logo'], datetime.now().isoformat()
        ))
        
        contract_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'contract_id': contract_id,
            'message': 'Contrato generado exitosamente'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'errors': [f'Error guardando contrato: {str(e)}']}), 500

@app.route('/history')
@login_required
def history():
    """Mostrar historial de contratos del usuario"""
    conn = get_db_connection()
    user_id = session.get('user_id')
    contracts = conn.execute(
        'SELECT id, provider_name, client_name, service_title, created_at FROM contracts WHERE user_id = ? ORDER BY created_at DESC', 
        (user_id,)
    ).fetchall()
    conn.close()
    return render_template('history.html', contracts=contracts)

@app.route('/view/<int:contract_id>')
@login_required
def view_contract(contract_id):
    """Ver contrato individual del usuario"""
    conn = get_db_connection()
    user_id = session.get('user_id')
    # Solo permitir ver contratos del usuario actual
    contract = conn.execute(
        'SELECT * FROM contracts WHERE id = ? AND user_id = ?', 
        (contract_id, user_id)
    ).fetchone()
    conn.close()
    
    if not contract:
        flash('Contrato no encontrado o no tienes permiso para verlo.', 'warning')
        return redirect(url_for('history'))
    
    # Convertir a diccionario
    contract_dict = dict(contract)
    
    # Formatear fecha para mostrar
    contract_dict['current_date'] = datetime.now().strftime('%d de %B de %Y')
    contract_dict['current_city'] = 'Ciudad de México'  # Podría ser dinámico
    
    return render_template('pdf_template.html', contract=contract_dict)

@app.route('/delete/<int:contract_id>', methods=['POST'])
@login_required
def delete_contract(contract_id):
    """Eliminar contrato del usuario"""
    try:
        conn = get_db_connection()
        user_id = session.get('user_id')
        
        # Obtener logo para borrarlo y verificar propiedad
        contract = conn.execute(
            'SELECT logo FROM contracts WHERE id = ? AND user_id = ?', 
            (contract_id, user_id)
        ).fetchone()
        
        if not contract:
            conn.close()
            return jsonify({'success': False, 'error': 'Contrato no encontrado o no tienes permiso'}), 404
        
        if contract['logo']:
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], contract['logo'])
            if os.path.exists(logo_path):
                os.remove(logo_path)
        
        conn.execute('DELETE FROM contracts WHERE id = ? AND user_id = ?', (contract_id, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Contrato eliminado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir archivos subidos"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Inicializar base de datos
    get_db_connection().close()
    app.run(debug=True, host='0.0.0.0', port=5000)
