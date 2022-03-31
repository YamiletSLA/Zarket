from datetime import timedelta
from urllib import request

from flask import Flask,render_template,request,redirect,url_for,flash,session,abort
from flask_bootstrap import Bootstrap
from modelo.Dao import db, Categoria, Producto, Usuario, Tarjetas, Paqueterias, Carrito, Pedidos, DetallePedidos
from modelo.Dao import db, Almacen, Usuario, Ofertas, Ventas
from flask_login import login_required,login_user,logout_user,current_user,LoginManager
import json


app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:holamundo@localhost/MiConexion'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key='Cl4v3'
#Implementación de la gestion de usuarios con flask-login
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='mostrar_login'
login_manager.login_message='¡ Tu sesión expiró !'
login_manager.login_message_category="info"

# Urls defininas para el control de usuario
@app.before_request
def before_request():
    session.permanent=True
    app.permanent_session_lifetime=timedelta(minutes=10)

@app.route("/")
def inicio():
    return render_template('principal.html')

#@app.route('/Usuarios/iniciarSesion')
#def mostrar_login():
#    if current_user.is_authenticated:
#        return render_template('principal2.html')
#    else:
#        return render_template('usuarios/login.html')

@login_manager.user_loader
def cargar_usuario(id):
    return Usuario.query.get(int(id))

@app.route('/Usuarios/nuevo')
def nuevoUsuario():
    if current_user.is_authenticated and not current_user.is_admin():
        return render_template('principal2.html')
    else:
        return render_template('usuarios/registrarCuenta.html')

@app.route('/Usuarios/agregar',methods=['post'])
def agregarUsuario():
    try:
        usuario=Usuario()
        usuario.nombre=request.form['nombre']
        usuario.password=request.form['password']
        usuario.Posisicion=request.values.get("posicion","Vendedor")
        usuario.agregar()
        flash('¡ Usuario registrado con exito')
    except:
        flash('¡ Error al agregar al usuario !')
    return render_template('usuarios/registrarCuenta.html')


@app.route("/Usuarios/validarSesion",methods=['POST'])
def login():
    correo=request.form['email']
    password=request.form['password']
    usuario=Usuario()
    user=usuario.validar(nombre,password)
    if user!=None:
        login_user(user)
        return render_template('principal2.html')
    else:
        flash('Nombre de usuario o contraseña incorrectos')
        return render_template('usuarios/login.html')

@app.route('/Usuarios/cerrarSesion')
@login_required
def cerrarSesion():
    logout_user()
    return redirect(url_for('mostrar_login'))

@app.route('/Usuarios/verPerfil')
@login_required
def consultarUsuario():
    return render_template('usuarios/editar.html')

@app.route('/Usuarios/Clientes')
@login_required
def consultarClientes():
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/clientes.html',user=user.consultaUsuarios())
    else:
        return render_template('usuarios/login.html')
@app.route('/Usuarios/Vendedores')
@login_required
def consultarVendedores():
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/vendedores.html',user=user.consultaUsuarios())
    else:
        return render_template('usuarios/login.html')
@app.route('/Usuarios/Admin')
@login_required
def consultarAdmin():
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/admins.html',user=user.consultaUsuarios())
    else:
        return render_template('usuarios/login.html')
#fin del manejo de usuarios

@app.route('/Usuarios/<int:id>')
@login_required
def consultarUnUsuario(id):
    if current_user.is_authenticated and current_user.is_admin():
        user=Usuario()
        return render_template('usuarios/editarUsu.html',user=user.consultaIndividual(id))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Usuarios/modificar',methods=['POST'])
@login_required
def modificarUsuario():
    if current_user.is_authenticated:
        try:
            user=Usuario()
            user.idUsuario=request.form['ID']
            user.nombre=request.form['nombre']
            user.Posicion=request.form['posicion']
            user.editarUsua()
            flash('¡ Usuario editado con exito !')
        except:
            flash('¡ Error al editar el usuario !')
        if user.tipo == 'Comprador':
            return redirect(url_for('consultarClientes'))
        else:
            if user.tipo == 'Vendedor':
                return redirect(url_for('consultarVendedores'))
            else :
                return redirect(url_for('consultarAdmin'))

    else:
        return redirect(url_for('mostrar_login'))
#PRODUCTOS

@app.route("/Almacen")
def consultarAlmacen():
    producto=Producto()
    return render_template("Almacen/consultaGeneral.html",productos=producto.consultaGeneral())

@app.route('/Almacen/foto/<int:id>')
def consultarFotoPorducto(id):
    prod=Producto()
    return prod.consultarFoto(id)


@app.route('/Almacen/nuevo')
@login_required
def nuevoProducto():
    if current_user.is_authenticated and current_user.is_admin():
            return render_template('productos/agregarP.html')
    else:
        abort(404)

@app.route('/Productos/agregar',methods=['post'])
@login_required
def agregarProducto():
    try:
        if current_user.is_authenticated:
            if current_user.is_admin():
                try:
                    prod=Producto()
                    prod.idCategoria=1
                    prod.producto=request.form['']
                    prod.descripcion=request.form['desc']
                    prod.precioVenta=request.form['precio']
                    prod.foto=request.files['imagen'].stream.read()
                    prod.agregar()
                    flash('¡ Producto agregada con exito !')
                except:
                    flash('¡ Error al agregar el producto !')
                return redirect(url_for('consultarProductos'))
            else:
                abort(404)

        else:
            return redirect(url_for('mostrar_login'))
    except:
        abort(500)

@app.route('/Productos/editar',methods=['POST'])
@login_required
def editarProducto():
    if current_user.is_authenticated and current_user.is_admin():
        try:
            prod=Producto()
            prod.idCategoria=request.form['idCategoria']
            prod.producto=request.form['']
            prod.descripcion=request.form['desc']
            prod.precioVenta=request.form['precio']
            prod.foto=request.files['imagen'].stream.read()
            imagen=request.files['imagen'].stream.read()
            if imagen:
                prod.imagen=imagen
            prod.editar()
            flash('¡ Producto editado con exito !')
        except:
            flash('¡ Error al editar el producto !')

        return redirect(url_for('consultarProductos'))
    else:
        return redirect(url_for('mostrar_login'))

@app.route('/Productos/eliminar/<int:id>')
@login_required
def eliminarProducto(id):
    if current_user.is_authenticated and current_user.is_admin():
        try:
            prod=Producto()
            prod.eliminar(id)
            flash('Producto eliminado con exito')
        except:
            flash('Error al eliminar el producto')
        return redirect(url_for('consultarProductos'))
    else:
        return redirect(url_for('mostrar_login'))

#manejo de errores
@app.errorhandler(404)
def error_404(e):
    return render_template('comunes/error_404.html'),404

@app.errorhandler(500)
def error_500(e):
    return render_template('comunes/error_500.html'),500

if __name__=='__main__':
    db.init_app(app)#Inicializar la BD - pasar la configuración de la url de la BD
    app.run(debug=True)



