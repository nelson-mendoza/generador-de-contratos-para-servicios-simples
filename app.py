from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
from flask_wtf.csrf import CSRFProtect
from rules import get_db, validate_contract, register_user, login_user
from werkzeug.utils import secure_filename
import os
import time # Para nombres únicos de archivos

app = Flask(__name__)
# Clave secreta generada automáticamente para mayor seguridad
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex()) 

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear carpeta uploads al iniciar (fuera del main para funcionar con flask run)
# Inicializar protección CSRF
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
csrf = CSRFProtect(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Rutas de Autenticación ---

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        
        if not username or len(username) < 3:
            flash("Usuario muy corto.", "error")
            return redirect(url_for('register'))
        if not password or len(password) < 6:
            flash("Contraseña débil (min 6).", "error")
            return redirect(url_for('register'))
        if password != confirm:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for('register'))
            
        success, msg = register_user(username, password)
        if success:
            flash("Cuenta creada. Inicie sesión.", "success")
            return redirect(url_for('login'))
        else:
            flash(msg, "error")
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_id = login_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash("Credenciales inválidas.", "error")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    """Borra cuenta y contratos (Cascada manual por seguridad)."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contracts WHERE user_id = ?", (session['user_id'],))
    cursor.execute("DELETE FROM users WHERE id = ?", (session['user_id'],))
    conn.commit()
    conn.close()
    session.clear()
    flash("Cuenta eliminada.", "warning")
    return redirect(url_for('register'))

# --- Rutas de la App ---

@app.route('/new_contract', methods=['GET', 'POST'])
def new_contract():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        errors = validate_contract(request.form)
        
        # Validaciones críticas: Prestador y Cliente no pueden ser iguales
        nombre_prestador = request.form.get('provider_name', '').strip()
        nombre_cliente = request.form.get('client_name', '').strip()
        telefono_prestador = request.form.get('provider_phone', '').strip()
        telefono_cliente = request.form.get('client_phone', '').strip()
        
        if nombre_prestador and nombre_cliente and nombre_prestador.lower() == nombre_cliente.lower():
            errors.append("El nombre del Prestador y del Cliente no pueden ser iguales.")
        
        if telefono_prestador and telefono_cliente and telefono_prestador == telefono_cliente:
            errors.append("El número de teléfono del Prestador y del Cliente no pueden ser iguales.")
        
        # Manejo de Logo con nombre único (timestamp) para evitar sobrescribir
        logo_filename = None
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Nombre único: user_id_timestamp_nombre.ext
                unique_name = f"{session['user_id']}_{int(time.time())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
                logo_filename = unique_name
            elif file:
                errors.append("Imagen no válida (solo JPG/PNG).")

        if errors:
            # CORRECCIÓN: En vez de redirect (que borra datos), renderizamos con errores
            # Pasamos los datos del formulario (request.form) para rellenar los inputs
            for err in errors:
                flash(err, "error")
            return render_template('form.html', form_data=request.form)

        # Guardar en DB
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO contracts (
                    user_id, city_location, provider_name, provider_phone, provider_logo,
                    client_name, client_phone, service_type, service_title, service_desc,
                    has_materials, materials_details, is_quote_pending,
                    payment_structure, payment_timing, total_amount, advance_amount, remaining_amount,
                    payment_method, bank_details, crypto_wallet, other_method, deadline, penalty_rate,
                    rfc_provider, rfc_client, address_provider, address_client, email_client,
                    witness_name, include_confidentiality, include_signatures,
                    sig_provider_name, sig_client_name, sig_witness_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                request.form.get('city_location'), # Nueva ciudad
                request.form.get('provider_name'), request.form.get('provider_phone'), logo_filename,
                request.form.get('client_name'), request.form.get('client_phone'),
                request.form.get('service_type'), request.form.get('service_title'), request.form.get('service_desc'),
                1 if request.form.get('has_materials') else 0, request.form.get('materials_details'),
                1 if request.form.get('is_quote_pending') else 0,
                request.form.get('payment_structure'), request.form.get('payment_timing'),
                float(request.form.get('total_amount')),
                float(request.form.get('advance_amount') or 0),
                float(request.form.get('remaining_amount') or 0),
                request.form.get('payment_method'), request.form.get('bank_details'),
                request.form.get('crypto_wallet'), request.form.get('other_method'),
                request.form.get('deadline'), float(request.form.get('penalty_rate') or 0),
                request.form.get('rfc_provider'), request.form.get('rfc_client'),
                request.form.get('address_provider'), request.form.get('address_client'),
                request.form.get('email_client'), request.form.get('witness_name'),
                1 if request.form.get('include_confidentiality') else 0,
                1 if request.form.get('include_signatures') else 0,
                request.form.get('sig_provider_name'), request.form.get('sig_client_name'),
                request.form.get('sig_witness_name')
            ))
            contract_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            flash("Contrato generado con éxito.", "success")
            return redirect(url_for('view_contract', contract_id=contract_id))
            
        except Exception as e:
            conn.close()
            flash(f"Error al guardar: {str(e)}", "error")
            return render_template('form.html', form_data=request.form)

    return render_template('form.html', form_data=None)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    contracts = conn.execute(
        "SELECT * FROM contracts WHERE user_id = ? ORDER BY created_at DESC", 
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('history.html', contracts=contracts)

@app.route('/view/<int:contract_id>')
def view_contract(contract_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    # Asegurar que el contrato pertenece al usuario logueado
    contract = conn.execute(
        "SELECT * FROM contracts WHERE id = ? AND user_id = ?", 
        (contract_id, session['user_id'])
    ).fetchone()
    conn.close()
    
    if not contract:
        flash("Contrato no encontrado.", "error")
        return redirect(url_for('history'))
        
    return render_template('pdf_view.html', contract=contract)

@app.route('/delete/<int:contract_id>', methods=['POST'])
def delete_contract(contract_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Verificar CSRF token manualmente si es necesario
    from flask_wtf.csrf import validate_csrf
    try:
        validate_csrf(request.form.get('csrf_token'))
    except Exception:
        flash("Error de seguridad CSRF.", "error")
        return redirect(url_for('history'))
    
    conn = get_db()
    contract = conn.execute("SELECT provider_logo FROM contracts WHERE id = ? AND user_id = ?", 
                            (contract_id, session['user_id'])).fetchone()
    if contract:
        if contract['provider_logo']:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], contract['provider_logo']))
            except FileNotFoundError:
                pass
        conn.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
        conn.commit()
        flash("Contrato eliminado.", "warning")
    conn.close()
    return redirect(url_for('history'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
