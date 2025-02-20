from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from functools import wraps
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:200804@localhost:3306/peliculas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'key secret'

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
db = SQLAlchemy(app)
ma = Marshmallow(app)

# MODELOS
class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    fechaCreacion = db.Column(db.DateTime, nullable=False)

    def __init__(self, nombre):
        self.nombre = nombre
        self.fechaCreacion = datetime.now()

class Pelicula(db.Model):
    __tablename__ = 'pelicula'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    duracion = db.Column(db.Integer, nullable=False)
    rutaImagen = db.Column(db.String(200), nullable=True)
    fechaCreacion = db.Column(db.DateTime, nullable=False)
    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey('categoria.id', ondelete='SET NULL'),
        nullable=True
    )
    categoria = db.relationship(
        'Categoria',
        backref=db.backref('peliculas', lazy=True, passive_deletes=True)
    )

    def __init__(self, nombre, categoria_id, descripcion, duracion, rutaImagen=None):
        self.nombre = nombre
        self.categoria_id = categoria_id
        self.descripcion = descripcion
        self.duracion = duracion
        self.rutaImagen = rutaImagen
        self.fechaCreacion = datetime.now()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombreUsuario = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(50), nullable=False)

    def __init__(self, nombreUsuario, password, rol):
        self.nombreUsuario = nombreUsuario
        self.password = password
        self.rol = rol

# ESQUEMAS
class CategoriaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Categoria
        load_instance = True

class PeliculaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pelicula
        load_instance = True

class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True
        exclude = ('password',)  

# DECORADORES PARA VERIFICAR EL TOKEN Y EL ROL DEL USUARIO
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token_header = request.headers['Authorization']
            if token_header.startswith('Bearer '):
                token = token_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token faltante'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.filter_by(nombreUsuario=data['nombreUsuario']).first()
            if current_user is None:
                return jsonify({'error': 'Usuario no encontrado'}), 401
        except Exception as e:
            return jsonify({'error': 'Token inválido'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.rol.lower() != 'administrador':
            return jsonify({'error': 'Acceso denegado: se requiere rol de administrador'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ENDPOINT PARA EL LOGIN
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nombreUsuario = data.get('nombreUsuario', '').strip().lower()
    password = data.get('password', '')
    rol = data.get('rol', '').strip().lower()

    usuario = Usuario.query.filter_by(nombreUsuario=nombreUsuario).first()

    if not usuario:
        return jsonify({'error': 'Usuario no encontrado.'}), 401

    if not check_password_hash(usuario.password, password):
        return jsonify({'error': 'Contraseña incorrecta.'}), 401

    if usuario.rol.lower() != rol:
        return jsonify({'error': 'Rol incorrecto.'}), 401

    token = jwt.encode({
        'nombreUsuario': usuario.nombreUsuario,
        'rol': usuario.rol,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'token': token,
        'nombreUsuario': usuario.nombreUsuario,
        'rol': usuario.rol.lower()
    }), 200

# CREAR USUARIO
@app.route('/usuario', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    nombreUsuario = data.get('nombreUsuario', '').strip().lower()
    password = data.get('password', '')
    rol = data.get('rol', '').strip().lower()

    if not nombreUsuario or not password or not rol:
        return jsonify({'error': 'Datos incompletos.'}), 400

    # VERIFICAR SI EL NOMBRE DE USUARIO YA EXISTE
    if Usuario.query.filter_by(nombreUsuario=nombreUsuario).first():
        return jsonify({'error': 'El nombre de usuario ya existe.'}), 409

    # ENCRIPTAR LA CONTRASEÑA
    hashed_password = generate_password_hash(password)

    # CREAR EL NUEVO USUARIO
    nuevo_usuario = Usuario(
        nombreUsuario=nombreUsuario,
        password=hashed_password,
        rol=rol.lower()
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'mensaje': 'Usuario creado exitosamente'}), 201

# OBTENER TODOS LOS USUARIOS
@app.route('/usuarios', methods=['GET'])
@token_required
@admin_required
def obtener_usuarios(current_user):
    usuarios = Usuario.query.all()
    usuario_schema = UsuarioSchema(many=True)
    return usuario_schema.jsonify(usuarios), 200

# OBTENER USUARIO POR ID
@app.route('/usuario/<int:id>', methods=['GET'])
@token_required
@admin_required
def obtener_usuario(current_user, id):
    usuario = Usuario.query.get(id)
    if usuario:
        usuario_schema = UsuarioSchema()
        return usuario_schema.jsonify(usuario), 200
    return jsonify({'error': 'Usuario no encontrado'}), 404

# ACTUALIZAR USUARIO
@app.route('/usuario/<int:id>', methods=['PUT'])
@token_required
@admin_required
def actualizar_usuario(current_user, id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.get_json()
    nombreUsuario = data.get('nombreUsuario', usuario.nombreUsuario).strip().lower()
    password = data.get('password')
    rol = data.get('rol', usuario.rol).strip().lower()

    if Usuario.query.filter(
        Usuario.nombreUsuario == nombreUsuario,
        Usuario.id != id
    ).first():
        return jsonify({'error': 'El nombre de usuario ya está en uso.'}), 409

    usuario.nombreUsuario = nombreUsuario

    if password:
        usuario.password = generate_password_hash(password)

    usuario.rol = rol.lower()
    db.session.commit()

    return jsonify({'mensaje': 'Usuario actualizado exitosamente'}), 200

# ELIMINAR USUARIO POR ID
@app.route('/usuario/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def eliminar_usuario(current_user, id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({'mensaje': 'Usuario eliminado exitosamente'}), 200

# ENDPOINTS DE CATEGORÍAS
# CREAR CATEGORÍA
@app.route('/categoria/<string:nombre>', methods=['POST'])
@token_required
@admin_required
def crear_categoria(current_user, nombre):
    nombre = nombre.strip()
    if not nombre:
        return jsonify({'error': 'Nombre de categoría requerido.'}), 400

    if Categoria.query.filter_by(nombre=nombre).first():
        return jsonify({'error': 'La categoría ya existe.'}), 409

    nuevaCategoria = Categoria(nombre)
    db.session.add(nuevaCategoria)
    db.session.commit()
    return jsonify({'mensaje': 'Categoría creada exitosamente'}), 201

# EDITAR CATEGORÍA
@app.route('/editarCategoria/<int:id>', methods=['PUT'])
@token_required
@admin_required
def editar_categoria(current_user, id):
    nuevo_nombre = request.json.get('nombre', '').strip()
    if not nuevo_nombre:
        return jsonify({'error': 'Nombre de categoría requerido.'}), 400

    categoria = Categoria.query.get(id)
    if categoria is None:
        return jsonify({'error': 'Categoría no encontrada'}), 404

    if Categoria.query.filter(
        Categoria.nombre == nuevo_nombre,
        Categoria.id != id
    ).first():
        return jsonify({'error': 'El nombre de categoría ya está en uso.'}), 409

    categoria.nombre = nuevo_nombre
    db.session.commit()

    return jsonify({'mensaje': 'Categoría actualizada exitosamente'}), 200

# ELIMINAR CATEGORÍA
@app.route('/eliminarCategoria/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def eliminar_categoria(current_user, id):
    categoria = Categoria.query.get(id)
    if categoria is None:
        return jsonify({'error': 'Categoría no encontrada'}), 404

    db.session.delete(categoria)
    db.session.commit()

    return jsonify({'mensaje': 'Categoría eliminada exitosamente'}), 200

# OBTENER TODAS LAS CATEGORÍAS
@app.route('/obtenerCategorias', methods=['GET'])
def obtener_categorias():
    lista_categoria = Categoria.query.all()
    categoria_schema = CategoriaSchema(many=True)
    return categoria_schema.jsonify(lista_categoria)

# OBTENER CATEGORÍA POR ID
@app.route('/obtenerCategoria/<int:id>', methods=['GET'])
def obtener_categoria(id):
    categoria = Categoria.query.get(id)
    if categoria is None:
        return jsonify({'error': 'Categoría no encontrada'}), 404

    categoria_schema = CategoriaSchema()
    return categoria_schema.jsonify(categoria)

# ENDPOINTS DE PELÍCULAS
# SERVIR IMÁGENES ESTÁTICAS
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# OBTENER TODAS LAS PELÍCULAS
@app.route('/obtenerPeliculas', methods=['GET'])
def obtener_peliculas():
    peliculas = Pelicula.query.all()
    output = []

    for pelicula in peliculas:
        pelicula_data = {}
        pelicula_data['id'] = pelicula.id
        pelicula_data['nombre'] = pelicula.nombre
        pelicula_data['descripcion'] = pelicula.descripcion
        pelicula_data['duracion'] = pelicula.duracion
        if pelicula.rutaImagen:
            pelicula_data['rutaImagen'] = f"/uploads/{pelicula.rutaImagen}"
        else:
            pelicula_data['rutaImagen'] = ''
        pelicula_data['categoria_id'] = pelicula.categoria_id
        output.append(pelicula_data)

    return jsonify(output)

# OBTENER PELÍCULA POR ID
@app.route('/obtenerPelicula/<int:id>', methods=['GET'])
def obtener_pelicula(id):
    pelicula = Pelicula.query.get(id)
    if pelicula is None:
        return jsonify({'error': 'Película no encontrada'}), 404

    pelicula_data = {}
    pelicula_data['id'] = pelicula.id
    pelicula_data['nombre'] = pelicula.nombre
    pelicula_data['descripcion'] = pelicula.descripcion
    pelicula_data['duracion'] = pelicula.duracion
    if pelicula.rutaImagen:
        pelicula_data['rutaImagen'] = f"/uploads/{pelicula.rutaImagen}"
    else:
        pelicula_data['rutaImagen'] = ''
    pelicula_data['categoria_id'] = pelicula.categoria_id

    return jsonify(pelicula_data)

# OBTENER PELÍCULAS POR CATEGORÍA
@app.route('/obtenerPeliculasEnCategoria/<int:categoria_id>', methods=['GET'])
def obtener_peliculas_en_categoria(categoria_id):
    if categoria_id == 'null':
        peliculas = Pelicula.query.filter_by(categoria_id=None).all()
    else:
        peliculas = Pelicula.query.filter_by(categoria_id=categoria_id).all()
    output = []

    for pelicula in peliculas:
        pelicula_data = {}
        pelicula_data['id'] = pelicula.id
        pelicula_data['nombre'] = pelicula.nombre
        pelicula_data['descripcion'] = pelicula.descripcion
        pelicula_data['duracion'] = pelicula.duracion
        if pelicula.rutaImagen:
            pelicula_data['rutaImagen'] = f"/uploads/{pelicula.rutaImagen}"
        else:
            pelicula_data['rutaImagen'] = ''
        pelicula_data['categoria_id'] = pelicula.categoria_id
        output.append(pelicula_data)

    return jsonify(output)

# BUSCAR PELÍCULA POR NOMBRE
@app.route('/buscarPelicula/<string:nombre>', methods=['GET'])
def buscar_pelicula(nombre):
    peliculas = Pelicula.query.filter(
        Pelicula.nombre.ilike(f'%{nombre}%')
    ).all()
    output = []

    for pelicula in peliculas:
        pelicula_data = {}
        pelicula_data['id'] = pelicula.id
        pelicula_data['nombre'] = pelicula.nombre
        pelicula_data['descripcion'] = pelicula.descripcion
        pelicula_data['duracion'] = pelicula.duracion
        if pelicula.rutaImagen:
            pelicula_data['rutaImagen'] = f"/uploads/{pelicula.rutaImagen}"
        else:
            pelicula_data['rutaImagen'] = ''
        pelicula_data['categoria_id'] = pelicula.categoria_id
        output.append(pelicula_data)

    return jsonify(output)

# CREAR PELÍCULA CON IMAGEN
@app.route('/crearPelicula', methods=['POST'])
@token_required
@admin_required
def crear_pelicula(current_user):
    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    duracion = request.form.get('duracion')
    categoria_id = request.form.get('categoria_id')

    if 'imagen' not in request.files:
        return jsonify({'error': 'No se proporcionó ninguna imagen.'}), 400

    file = request.files['imagen']


    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ninguna imagen.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de archivo no permitido.'}), 400

    if Pelicula.query.filter_by(nombre=nombre).first():
        return jsonify({'error': 'El nombre de la película ya está en uso.'}), 409

    if categoria_id:
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada.'}), 404
    else:
        categoria_id = None

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    rutaImagen = filename 

    nueva_pelicula = Pelicula(
        nombre=nombre,
        categoria_id=categoria_id,
        descripcion=descripcion,
        duracion=duracion,
        rutaImagen=rutaImagen
    )

    db.session.add(nueva_pelicula)
    db.session.commit()

    return jsonify({'mensaje': 'Película creada exitosamente'}), 201

# ACTUALIZAR PELÍCULA
@app.route('/actualizarPelicula/<int:id>', methods=['PUT'])
@token_required
@admin_required
def actualizar_pelicula(current_user, id):
    pelicula = Pelicula.query.get(id)
    if pelicula is None:
        return jsonify({'error': 'Película no encontrada'}), 404

    nombre = request.form.get('nombre', pelicula.nombre).strip()
    descripcion = request.form.get('descripcion', pelicula.descripcion).strip()
    duracion = request.form.get('duracion', pelicula.duracion)
    categoria_id = request.form.get('categoria_id', pelicula.categoria_id)

    if Pelicula.query.filter(
        Pelicula.nombre == nombre,
        Pelicula.id != id
    ).first():
        return jsonify({'error': 'El nombre de la película ya está en uso.'}), 409

    pelicula.nombre = nombre
    pelicula.descripcion = descripcion
    pelicula.duracion = duracion

    if categoria_id:
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada.'}), 404
        pelicula.categoria_id = categoria_id
    else:
        pelicula.categoria_id = None

    if 'imagen' in request.files:
        file = request.files['imagen']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pelicula.rutaImagen = filename
        else:
            return jsonify({'error': 'Tipo de archivo no permitido.'}), 400

    db.session.commit()

    return jsonify({'mensaje': 'Película actualizada exitosamente'}), 200

# ELIMINAR PELÍCULA
@app.route('/borrarPelicula/<int:id>', methods=['DELETE'])
@token_required
@admin_required
def borrar_pelicula(current_user, id):
    pelicula = Pelicula.query.get(id)
    if pelicula is None:
        return jsonify({'error': 'Película no encontrada'}), 404
    if pelicula.rutaImagen:
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], pelicula.rutaImagen)
        if os.path.exists(imagen_path):
            os.remove(imagen_path)

    db.session.delete(pelicula)
    db.session.commit()

    return jsonify({'mensaje': 'Película eliminada exitosamente'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='localhost')
