import sqlite3
from datetime import datetime

DB_NAME = "produccion.db"

def conectar_db():
    """Establece conexión con el archivo de la base de datos."""
    return sqlite3.connect(DB_NAME)

def inicializar_base_de_datos():
    """Crea la tabla de estibas si no existe en el archivo .db"""
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estibas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pallet_id INTEGER,
            fecha TEXT,
            hora_cierre TEXT,
            turno INTEGER,
            linea TEXT,
            producto TEXT,
            sap TEXT,
            fecha_llenaje TEXT,
            fecha_vencimiento TEXT,
            lote TEXT,
            cajas_sistema INTEGER,
            cajas_reales INTEGER,
            tiempo_segundos INTEGER,
            estado TEXT,
            operador TEXT,
            sscc TEXT
        )
    """)
    conexion.commit()
    conexion.close()

def guardar_estiba(datos):
    """Inserta un nuevo registro de estiba en la base de datos."""
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO estibas (
            pallet_id, fecha, hora_cierre, turno, linea, producto, sap, 
            fecha_llenaje, fecha_vencimiento, lote, cajas_sistema, 
            cajas_reales, tiempo_segundos, estado, operador, sscc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datos["id"], datos["fecha"], datos["hora_cierre"], datos["turno"],
        datos["linea"], datos["producto"], datos["sap"], datos["fecha_llenaje"],
        datos["fecha_vencimiento"], datos["lote"], datos["cajas_sistema"],
        datos["cajas_reales"], datos["tiempo_segundos"], datos["estado"],
        datos["operador"], datos["sscc"]
    ))
    conexion.commit()
    conexion.close()

def actualizar_estiba_validacion(pallet_id, hora_cierre, cajas_reales, operador, turno):
    """Actualiza la estiba cuando el operador la valida y le da el Check."""
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE estibas 
        SET hora_cierre = ?, cajas_reales = ?, operador = ?, turno = ?, estado = 'Validada'
        WHERE pallet_id = ? AND estado = 'Pendiente de Validación'
    """, (hora_cierre, cajas_reales, operador, turno, pallet_id))
    conexion.commit()
    conexion.close()

def obtener_estibas_por_estado(estado):
    """Trae las estibas filtradas por estado (Pendiente de Validación o Validada)"""
    conexion = conectar_db()
    conexion.row_factory = sqlite3.Row  # Permite leer las filas como diccionarios
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM estibas WHERE estado = ?", (estado,))
    filas = cursor.fetchall()
    conexion.close()
    # Convertimos los resultados a una lista de diccionarios estándar de Python
    return [dict(fila) for fila in filas]

def obtener_estibas_filtradas(fecha_busqueda, linea_busqueda, producto_busqueda):
    """
    Busca estibas validadas filtrando obligatoriamente por fecha,
    y opcionalmente por Línea y Producto si el usuario los selecciona.
    """
    conexion = conectar_db()
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    # La fecha siempre es obligatoria para acotar la búsqueda
    query = "SELECT * FROM estibas WHERE estado = 'Validada' AND fecha_llenaje = ?"
    parametros = [f"{fecha_busqueda}"]
    
    # Si el usuario selecciona una línea específica (y no "Todas")
    if linea_busqueda and linea_busqueda != "Todas":
        query += " AND linea = ?"
        parametros.append(linea_busqueda)
        
    # Si el usuario selecciona un producto específico (y no "Todos")
    if producto_busqueda and producto_busqueda != "Todos":
        query += " AND producto = ?"
        parametros.append(producto_busqueda)
        
    cursor.execute(query, tuple(parametros))
    filas = cursor.fetchall()
    conexion.close()
    return [dict(fila) for fila in filas]

def obtener_valores_unicos_por_fecha(fecha_busqueda):
    """
    Trae las líneas y productos únicos que realmente tuvieron 
    producción en una fecha específica para llenar los selectores.
    """
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Obtener líneas únicas de ese día
    cursor.execute("SELECT DISTINCT linea FROM estibas WHERE estado = 'Validada' AND fecha_llenaje = ?", (f"{fecha_busqueda}",))
    lineas = [fila[0] for fila in cursor.fetchall() if fila[0]]
    
    # Obtener productos únicos de ese día
    cursor.execute("SELECT DISTINCT producto FROM estibas WHERE estado = 'Validada' AND fecha_llenaje = ?", (f"{fecha_busqueda}",))
    productos = [fila[0] for fila in cursor.fetchall() if fila[0]]
    
    conexion.close()
    return lineas, productos

def obtener_siguiente_pallet_id(linea, producto, lote):
    """Calcula el correlativo del siguiente pallet basado en los existentes."""
    conexion = sqlite3.connect("produccion.db")
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM estibas 
        WHERE linea = ? AND producto = ? AND lote = ?
    """, (linea, producto, lote))
    cantidad_existente = cursor.fetchone()[0]
    conexion.close()
    return cantidad_existente + 1

def ejecutar_query_directa(query, params=()):
    """Ejecuta operaciones de escritura o borrado directo (UPDATE/DELETE)."""
    conexion = sqlite3.connect("produccion.db")
    cursor = conexion.cursor()
    cursor.execute(query, params)
    conexion.commit()
    conexion.close()

def obtener_metricas_programa(linea, producto, lote):
    """Devuelve los datos procesados para el dashboard."""
    conexion = sqlite3.connect("produccion.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute("SELECT * FROM estibas WHERE estado = 'Validada' AND linea = ? AND producto = ?", (linea, producto))
    todas_del_programa = [dict(fila) for fila in cursor.fetchall()]

    cursor.execute("SELECT * FROM estibas WHERE estado = 'Validada' AND linea = ? AND producto = ? AND lote = ?", (linea, producto, lote))
    validadas_lote_activo = [dict(fila) for fila in cursor.fetchall()]
    conexion.close()
    
    return todas_del_programa, validadas_lote_activo
