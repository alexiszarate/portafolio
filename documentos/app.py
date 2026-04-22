from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import MySQLdb
from datetime import datetime, timedelta
from plyer import notification

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'alitas145'
app.config['MYSQL_DB'] = 'documentos_app'

# Conexión a la base de datos
mysql = MySQLdb.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    passwd=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

# Ruta principal
@app.route('/')
def index():
    # Obtener todos los documentos de la base de datos
    cursor = mysql.cursor()
    cursor.execute("SELECT tipo_documento, fecha_emision, fecha_caducidad, nombre FROM documentos")
    documentos = cursor.fetchall()
    cursor.close()
    return render_template('index.html', documentos=documentos)


# Ruta para subir documentos
@app.route('/upload', methods=['POST'])
def upload():
    # Verificar que se haya seleccionado un archivo
    if 'documento' not in request.files:
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for('index'))

    file = request.files['documento']
    if file.filename == '':
        flash("El archivo no tiene nombre.", "error")
        return redirect(url_for('index'))

    # Guardar el archivo
    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)

    # Insertar en base de datos los datos del formulario
    nombre = request.form.get('nombre')
    tipo_documento = request.form.get('tipo_documento')
    fecha_emision = request.form.get('fecha_emision')
    fecha_caducidad = request.form.get('fecha_caducidad')

    cursor = mysql.cursor()
    query = """
    INSERT INTO documentos (nombre, tipo_documento, documento, fecha_emision, fecha_caducidad)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nombre, tipo_documento, filename, fecha_emision, fecha_caducidad))
    mysql.commit()
    cursor.close()

    flash("Documento subido correctamente.", "success")
    return redirect(url_for('index'))


# Función para verificar documentos próximos a caducar
def verificar_documentos():
    cursor = mysql.cursor()
    hoy = datetime.now()
    limite = hoy + timedelta(days=7)  # Documentos que vencen en los próximos 7 días

    query = """
    SELECT nombre, tipo_documento, fecha_caducidad 
    FROM documentos 
    WHERE fecha_caducidad BETWEEN %s AND %s
    """
    cursor.execute(query, (hoy, limite))
    resultados = cursor.fetchall()
    cursor.close()

    for doc in resultados:
        mostrar_notificacion(doc)


# Función para mostrar notificaciones en el ordenador
def mostrar_notificacion(documento):
    nombre, tipo_documento, fecha_caducidad = documento
    mensaje = (
        f"El documento tipo '{tipo_documento}' de '{nombre}' está próximo a caducar.\n"
        f"Fecha de caducidad: {fecha_caducidad.strftime('%d/%m/%Y')}"
    )
    notification.notify(
        title="Alerta de Caducidad de Documento",
        message=mensaje,
        app_name="Gestión de Documentos",
        timeout=10  # Duración de la notificación en segundos
    )


# Iniciar la verificación al inicio del servidor
if __name__ == '__main__':
    verificar_documentos()  # Llamada directa para verificar documentos al iniciar
    app.run(debug=True)
