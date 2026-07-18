from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# CLAVE SECRETA: En un proyecto real, esto debe ser complejo y oculto
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura_123' 

# Configuración de uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profile_pics')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB máximo

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verificar si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

print("1. App configurado")

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Si no está logueado, lo manda aquí

print("2. Login manager configurado")

DB_PATH = 'usuarios.db'

print("3. DB_PATH definido")

# 1. Inicializar Base de Datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE NOT NULL, 
                  password TEXT NOT NULL,
                  fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  ultimo_login TIMESTAMP)''')
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE NOT NULL, 
                  password TEXT NOT NULL,
                  foto_perfil TEXT,
                  fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  ultimo_login TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()


# Clase de Usuario para Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(id=user_data[0], username=user_data[1], password=user_data[2])
    return None

# 3. Rutas del Sistema

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = c.fetchone()
        conn.close()
        
        # Verificar si existe y si la contraseña (encriptada) coincide
        if user_data and check_password_hash(user_data[2], password):
            user_obj = User(id=user_data[0], username=user_data[1], password=user_data[2])
            login_user(user_obj)

            # Actualizar último login
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE users SET ultimo_login = datetime('now') WHERE id = ?", (user_obj.id,))
            conn.commit()
            conn.close()

            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # ENCRYPTAR la contraseña antes de guardarla (NUNCA guardar en texto plano)
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, fecha_registro) VALUES (?, ?, datetime('now'))", (username, hashed_password))
            conn.commit()
            conn.close()
            flash('¡Registro exitoso! Ahora inicia sesión.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Ese nombre de usuario ya existe.', 'error')
            
    return render_template('register.html')

@app.route('/dashboard')
@login_required # ESTA MAGIA PROTEGE LA RUTA
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))

# Rutas nuevas para mejorar el sistema

@app.route('/perfil')
@login_required
def perfil():
    """Mostrar información del usuario con fechas"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT fecha_registro, ultimo_login, foto_perfil FROM users WHERE id = ?", (current_user.id,))
    datos = c.fetchone()
    conn.close()
    
    return render_template('perfil.html', 
                          username=current_user.username,
                          fecha_registro=datos[0],
                          ultimo_login=datos[1],
                          foto_perfil=datos[2])

@app.route('/admin')
@login_required
def admin():
    """Panel de administración - Ver todos los usuarios"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, fecha_registro, ultimo_login FROM users ORDER BY id")
    usuarios = c.fetchall()
    conn.close()
    return render_template('admin.html', usuarios=usuarios)

@app.route('/subir_foto', methods=['GET', 'POST'])
@login_required
def subir_foto():
    """Permitir al usuario subir una foto de perfil"""
    if request.method == 'POST':
        # Verificar si hay archivo
        if 'foto' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('subir_foto'))
        
        file = request.files['foto']
        
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('subir_foto'))
        
        if file and allowed_file(file.filename):
            # Generar nombre único para el archivo
            filename = secure_filename(file.filename)
            filename = f"user_{current_user.id}_{filename}"
            
            # Eliminar foto anterior si existe
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT foto_perfil FROM users WHERE id = ?", (current_user.id,))
            foto_anterior = c.fetchone()[0]
            conn.close()
            
            if foto_anterior:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, foto_anterior))
                except:
                    pass
            
            # Guardar nueva foto
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            
            # Actualizar en base de datos
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE users SET foto_perfil = ? WHERE id = ?", (filename, current_user.id))
            conn.commit()
            conn.close()
            
            flash('¡Foto de perfil actualizada!', 'success')
            return redirect(url_for('perfil'))
        else:
            flash('Archivo no válido. Usa PNG, JPG o GIF', 'error')
    
    return render_template('subir_foto.html')

@app.route('/cambiar_password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """Permitir al usuario cambiar su contraseña"""
    if request.method == 'POST':
        password_actual = request.form['password_actual']
        password_nueva = request.form['password_nueva']
        password_confirm = request.form['password_confirm']
        
        # Verificar contraseña actual
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE id = ?", (current_user.id,))
        password_db = c.fetchone()[0]
        conn.close()
        
        if not check_password_hash(password_db, password_actual):
            flash('La contraseña actual es incorrecta', 'error')
            return redirect(url_for('cambiar_password'))
        
        if password_nueva != password_confirm:
            flash('Las nuevas contraseñas no coinciden', 'error')
            return redirect(url_for('cambiar_password'))
        
        if len(password_nueva) < 4:
            flash('La contraseña debe tener al menos 4 caracteres', 'error')
            return redirect(url_for('cambiar_password'))
        
        # Actualizar contraseña
        hashed_password = generate_password_hash(password_nueva)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, current_user.id))
        conn.commit()
        conn.close()
        
        flash('¡Contraseña cambiada correctamente!', 'success')
        return redirect(url_for('perfil'))
    
    return render_template('cambiar_password.html')

@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Permitir al usuario cambiar su nombre de usuario"""
    if request.method == 'POST':
        nuevo_username = request.form['username']
        
        # Verificar que no exista otro usuario con ese nombre
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ? AND id != ?", (nuevo_username, current_user.id))
        existe = c.fetchone()
        
        if existe:
            conn.close()
            flash('Ese nombre de usuario ya está en uso', 'error')
            return redirect(url_for('editar_perfil'))
        
        # Actualizar username
        c.execute("UPDATE users SET username = ? WHERE id = ?", (nuevo_username, current_user.id))
        conn.commit()
        conn.close()
        
        # Actualizar el objeto de usuario actual
        current_user.username = nuevo_username
        
        flash('¡Perfil actualizado correctamente!', 'success')
        return redirect(url_for('perfil'))
    
    return render_template('editar_perfil.html', username=current_user.username)

print("4. Todo cargado, iniciando servidor...")
print("Iniciando servidor en http://127.0.0.1:5000")
app.run(debug=True, use_reloader=False)