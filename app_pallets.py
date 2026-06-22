import streamlit as st
import time
import pandas as pd
import sqlite3
import string
import random
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from database import inicializar_base_de_datos, guardar_estiba, actualizar_estiba_validacion, obtener_estibas_por_estado, obtener_estibas_filtradas, obtener_valores_unicos_por_fecha

from sscc_generador import generar_sscc_local

st.set_page_config(page_title="CONTROL DE ESTIBAS", layout="wide")
st.title("CONTROL DE ESTIBAS")

inicializar_base_de_datos()

# --- Calculo dinamico del siguiente pallet ---
conexion = sqlite3.connect("produccion.db")
cursor = conexion.cursor()

# Si la orden ya está configurada, contamos cuántas estibas (pendientes o validadas) existen para este lote
if "orden_configurada" in st.session_state and st.session_state.orden_configurada:
    linea_a = st.session_state.orden_activa["linea_produccion"]
    prod_a = st.session_state.orden_activa["producto"]
    lote_a = st.session_state.orden_activa["lote"]
    
    cursor.execute("""
        SELECT COUNT(*) FROM estibas 
        WHERE linea = ? AND producto = ? AND lote = ?
    """, (linea_a, prod_a, lote_a))
    
    cantidad_existente = cursor.fetchone()[0]
    # El siguiente pallet será la cantidad existente + 1
    st.session_state.contador_estiba_id = cantidad_existente + 1
else:
    # Si no hay orden fijada aún, por defecto empezamos en 1
    st.session_state.contador_estiba_id = 1

conexion.close()

# --- Estado del pallet actual que llena el brazo palletizador ---
if "robot_cajas_actual" not in st.session_state:
    st.session_state.robot_cajas_actual = 0
if "robot_tiempo_inicio" not in st.session_state:
    st.session_state.robot_tiempo_inicio = time.time()

MAX_CAJAS_POR_ESTIBA = 10  # Este dato se recibe de la configuracin del brazo paletizador de acuerdo al formato

# Refresco automático cada 1 segundo para el visor en vivo
st_autorefresh(interval=1000, key="refresh_industrial")

# --- Metadatos de la orden de produccion activa ---
if "orden_activa" not in st.session_state:
    st.session_state.orden_activa = {
        "linea_produccion": "",
        "producto": "",
        "sap": "",
        "fecha_llenaje": datetime.now().strftime("%Y-%m-%d"),
        "fecha_vencimiento": "",
        "lote": ""
    }
if "orden_configurada" not in st.session_state:
    st.session_state.orden_configurada = False

# =====================================================================
# Configuracion de la orden de produccion
# =====================================================================
st.header("📋 Información General de la Orden")

with st.expander("Configurar Datos de la Línea y Producto", expanded=not st.session_state.orden_configurada):
    # Lista de productos precargados (se modifica de acuerdo a necesidades)
    OPCIONES_LINEAS = [
        "Selecciona una linea...",
        "Linea 1",
        "Linea 2"
    ]
    OPCIONES_PRODUCTOS = [
        "Selecciona un producto...",
        "Producto 1",
        "Producto 2"
    ]
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        linea_actual = st.session_state.orden_activa["linea_produccion"]
        idx_defecto = OPCIONES_LINEAS.index(linea_actual) if linea_actual in OPCIONES_LINEAS else 0
        v_linea = st.selectbox("Linea:", options=OPCIONES_LINEAS, index=idx_defecto)
        prod_actual = st.session_state.orden_activa["producto"]
        idx_defecto = OPCIONES_PRODUCTOS.index(prod_actual) if prod_actual in OPCIONES_PRODUCTOS else 0
        producto = st.selectbox("Producto:", options=OPCIONES_PRODUCTOS, index=idx_defecto)
    with col_h2:
        sap = st.text_input("Código SAP:", value=st.session_state.orden_activa["sap"])
        lote = st.text_input("Lote:", value=st.session_state.orden_activa["lote"])
    with col_h3:
        f_llenaje = st.date_input("Fecha de Llenaje:", value=datetime.strptime(st.session_state.orden_activa["fecha_llenaje"], "%Y-%m-%d"))
        f_vencimiento = st.text_input("Fecha de Vencimiento:", value=st.session_state.orden_activa["fecha_vencimiento"])

    if st.button("Fijar Información", type="primary"):
        if not v_linea or not lote or producto == "Selecciona un producto...":
            st.error("Por favor, llena todos los campos.")
        else:
            st.session_state.orden_activa = {
                "linea_produccion": v_linea,
                "producto": producto,
                "sap": sap,
                "fecha_llenaje": f_llenaje.strftime("%Y-%m-%d"),
                "fecha_vencimiento": f_vencimiento,
                "lote": lote
            }
            st.session_state.orden_configurada = True
            if "contador_estiba_id" in st.session_state:
                del st.session_state.contador_estiba_id
            st.success("¡Header de producción fijado correctamente!")
            st.rerun()

if st.session_state.orden_configurada:
    with st.container(border=True):
        st.subheader(f"📋 Datos de Producción")
        h_col1, h_col2, h_col3 = st.columns(3)
        with h_col1:
            st.markdown(f"**🏭 Línea:** {st.session_state.orden_activa['linea_produccion']}")
            st.markdown(f"**📦 Producto:** {st.session_state.orden_activa['producto']}")
        with h_col2:
            st.markdown(f"**🔢 Código SAP:** {st.session_state.orden_activa['sap']}")
            st.markdown(f"**🏷️ Lote:** {st.session_state.orden_activa['lote']}")
        with h_col3:
            st.markdown(f"**📅 Llenaje:** {st.session_state.orden_activa['fecha_llenaje']}")
            st.markdown(f"**⏳ Vencimiento:** {st.session_state.orden_activa['fecha_vencimiento']}")

else:
    st.warning("⚠️ Atención: No se ha configurado la información de la orden. Los pallets se guardarán sin datos de cabecera.")

st.divider()

# =====================================================================
# Cola de verificacion
# =====================================================================
st.header("📋 Pallets Completadas Pendientes de Validación")

# Leemos directo de la Base de Datos las estibas pendientes
pendientes = obtener_estibas_por_estado("Pendiente de Validación")

if not pendientes:
    st.success("✅ No hay pallets pendientes de revisión. El operador está al día.")
else:
    estiba_a_revisar = pendientes[0]
    
    st.warning(f"Modificando datos del pallet **Numero: {estiba_a_revisar['pallet_id']}** | Registrada el {estiba_a_revisar['fecha']}")
    
    # Creamos las 6 columnas en el orden de almacenamiento de la tabla
    col_rev1, col_rev2, col_rev3, col_rev4, col_rev5, col_rev6 = st.columns(6)
    
    with col_rev1:
        v_pallet_id = st.number_input(
            "N° Pallet:", 
            value=int(estiba_a_revisar["pallet_id"]), 
            key=f"edit_pallet_{estiba_a_revisar['id']}"
        )
    
    with col_rev2:
        hora_robot = estiba_a_revisar.get("hora_cierre", datetime.now().strftime("%H:%M"))
        v_hora_final = st.text_input(
            "Hora Cierre:", 
            value=hora_robot, 
            key=f"edit_hora_{estiba_a_revisar['id']}"
        )
        
    with col_rev3:
        v_lote_final = st.text_input(
            "Lote:", 
            value=str(estiba_a_revisar["lote"]), 
            key=f"edit_lote_{estiba_a_revisar['id']}"
        )

    with col_rev4:
        v_cajas_reales = st.number_input(
            "Cajas Reales:", 
            value=int(estiba_a_revisar["cajas_sistema"]), 
            key=f"edit_cajas_{estiba_a_revisar['id']}"
        )

    with col_rev5:
        v_sscc_final = st.text_input(
            "Código SSCC:", 
            value=str(estiba_a_revisar["sscc"]), 
            key=f"edit_sscc_{estiba_a_revisar['id']}"
        )

    with col_rev6:
        v_operador_final = st.text_input(
            "Operador/Firma:", 
            value=str(estiba_a_revisar["operador"]),
            key=f"edit_op_{estiba_a_revisar['id']}"
        )

    # Botones Guardar y Cancelar
    st.write("")
    col_btn1, col_btn2, _ = st.columns([2, 2, 2]) # Proporciones para los botones
    
    with col_btn1:
        # BOTÓN 1: Confirmar y guardar en base de datos
        if st.button(f"Guardar ", type="primary", key=f"btn_save_{estiba_a_revisar['id']}", use_container_width=True):
            if v_operador_final.strip() == "":
                    st.session_state[f"error_operador_{estiba_a_revisar['id']}"] = True
            else:
                # Si ya escribió el nombre, nos aseguramos de apagar la alerta si existía
                if f"error_operador_{estiba_a_revisar['id']}" in st.session_state:
                    del st.session_state[f"error_operador_{estiba_a_revisar['id']}"]    
                try:
                    hora_editada = int(v_hora_final.split(":")[0])
                except:
                    hora_editada = int(datetime.now().strftime("%H"))
                
                turno_calculado = 1 if hora_editada >= 22 or hora_editada < 6 else (2 if hora_editada < 14 else 3)
                
                conexion = sqlite3.connect("produccion.db")
                cursor = conexion.cursor()
                cursor.execute("""
                    UPDATE estibas 
                    SET pallet_id = ?, hora_cierre = ?, turno = ?, lote = ?, 
                        cajas_reales = ?, sscc = ?, operador = ?, estado = 'Validada'
                    WHERE id = ?
                """, (int(v_pallet_id), str(v_hora_final), int(turno_calculado), str(v_lote_final), 
                      int(v_cajas_reales), str(v_sscc_final), str(v_operador_final), estiba_a_revisar['id']))
                conexion.commit()
                conexion.close()
                
                st.success("Estiba archivada con éxito.")
                st.rerun()

        if st.session_state.get(f"error_operador_{estiba_a_revisar['id']}", False):
            st.error("Por favor, introduce tu nombre para firmar y validar el registro.")        

    with col_btn2:
        # BOTÓN 2: Cancelar datos a guardar
        if st.button(f" Cancelar ", type="secondary", key=f"btn_delete_{estiba_a_revisar['id']}", use_container_width=True):
            conexion = sqlite3.connect("produccion.db")
            cursor = conexion.cursor()
            
            # Borramos físicamente el registro de la cola pendiente
            cursor.execute("DELETE FROM estibas WHERE id = ?", (estiba_a_revisar['id'],))
            conexion.commit()
            conexion.close()
            
            st.toast("🚫 Cierre manual cancelado. Registro eliminado de la cola.", icon="🗑️")
            st.rerun()

st.divider()

# =====================================================================
# Historial de Pallets verificados
# =====================================================================
st.header("🗄️ Pallets Verificados (Orden Activa)")

# Comprobamos si hay una orden configurada en el panel principal
if not st.session_state.orden_configurada:
    st.info("💡 Configura y fija una Orden de Producción en el Header superior para ver su historial en vivo.")
else:
    # Leemos las variables actuales del panel principal
    linea_activa = st.session_state.orden_activa["linea_produccion"]
    producto_activo = st.session_state.orden_activa["producto"]
    lote_activo = st.session_state.orden_activa["lote"]

    CANTIDAD_PROGRAMADA = 1300 # Dato recibido de la cantidad programada en KPI 

    # CONSULTA 1: consulta el total de lo producido de la programacion actual
    # Filtramos solo por Línea y Producto para arrastrar la producción total del formato
    conexion = sqlite3.connect("produccion.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT * FROM estibas 
        WHERE estado = 'Validada' 
          AND linea = ? 
          AND producto = ?
    """, (linea_activa, producto_activo))
    
    todas_del_programa = [dict(fila) for fila in cursor.fetchall()]

    # 5. CONSULTA 2: consulta datos unicamente del lote activo (Para turnos)
    cursor.execute("""
        SELECT * FROM estibas 
        WHERE estado = 'Validada' 
          AND linea = ? 
          AND producto = ? 
          AND lote = ?
    """, (linea_activa, producto_activo, lote_activo))
    
    validadas_lote_activo = [dict(fila) for fila in cursor.fetchall()]
    conexion.close()

    # Calculo de turnos (Basado estrictamente en el Lote Activo)
    cajas_turno1 = 0
    cajas_turno2 = 0
    cajas_turno3 = 0

    for estiba in validadas_lote_activo:
        try:
            cajas = int(estiba["cajas_reales"]) if estiba["cajas_reales"] is not None else 0
            t = int(estiba["turno"])
            
            if t == 1:
                cajas_turno1 += cajas
            elif t == 2:
                cajas_turno2 += cajas
            elif t == 3:
                cajas_turno3 += cajas
        except (ValueError, TypeError):
            continue  

    # Calculo del cumplimiento completo del programa (Suma de todos los lotes/turnos anteriores)
    gran_total_programa = sum(int(estiba["cajas_reales"]) for estiba in todas_del_programa if estiba["cajas_reales"] is not None)
    
    # Diferencia y porcentaje global del formato/programa entero
    faltante_programa = CANTIDAD_PROGRAMADA - gran_total_programa
    porcentaje_cumplimiento = (gran_total_programa / CANTIDAD_PROGRAMADA) * 100 if CANTIDAD_PROGRAMADA > 0 else 0

    # ─── VISOR 1: Control de planificacion global (PERSISTENTE) ───────────
    with st.container(border=True):
        st.subheader(f"🎯 Cumplimiento del Programa Activo ({producto_activo})")
        st.caption("Este panel acumula la producción total del programa.")
        col_prog1, col_prog2, col_prog3 = st.columns(3)
        with col_prog1:
            st.metric(label="📋 Cantidad Programada", value=f"{CANTIDAD_PROGRAMADA:,} cajas")
        with col_prog2:
            status_faltante = f"{max(0, faltante_programa):,} cajas"
            st.metric(label="⏳ Cantidad Faltante", value=status_faltante)
        with col_prog3:
            st.metric(label="📈 Avance Total del Programa", value=f"{porcentaje_cumplimiento:.1f}%")
            
    st.write("") 

    # ─── VISOR 2: Desglose del lote activo ─────────────────────
    st.markdown(f"### Cajas del Lote: **{lote_activo}**")
    c1, c2, c3, c4 = st.columns([2.5, 2.5, 2.5, 2.5])

    with c1:
        with st.container(border=True):
            st.metric("Turno 1", f"{cajas_turno1} und")

    with c2:
        with st.container(border=True):
            st.metric("Turno 2", f"{cajas_turno2} und")

    with c3:
        with st.container(border=True):
            st.metric("Turno 3", f"{cajas_turno3} und")

    with c4:
        # Sumatoria exclusiva de lo que lleva este lote en especifico
        total_cajas_lote = cajas_turno1 + cajas_turno2 + cajas_turno3
        with st.container(border=True):
            st.metric(f"Total cajas: **{lote_activo}**", f"{total_cajas_lote:,} und")

    st.write("")

    # =====================================================================
    # Simulacion contador brazo palletizador 
    # =====================================================================
    col_sim, _ = st.columns([1, 2])
    with col_sim:
        if st.button("Simular que Robot coloca Caja (+1)"):
            st.session_state.robot_cajas_actual += 1

    # Verificacion automatica: maxima cantidad de cajas
    if st.session_state.robot_cajas_actual >= MAX_CAJAS_POR_ESTIBA:
        tiempo_final = int(time.time() - st.session_state.robot_tiempo_inicio)
        
        nuevo_registro = {
            "id": st.session_state.contador_estiba_id,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hora_cierre": datetime.now().strftime("%H:%M"),
            "turno": 1 if int(datetime.now().strftime("%H")) >= 22 or int(datetime.now().strftime("%H")) < 6 else (2 if int(datetime.now().strftime("%H")) < 14 else 3),
            "linea": st.session_state.orden_activa["linea_produccion"],
            "producto": st.session_state.orden_activa["producto"],
            "sap": st.session_state.orden_activa["sap"],
            "fecha_llenaje": st.session_state.orden_activa["fecha_llenaje"],
            "fecha_vencimiento": st.session_state.orden_activa["fecha_vencimiento"],
            "lote": st.session_state.orden_activa["lote"],
            "cajas_sistema": st.session_state.robot_cajas_actual,
            "cajas_reales": st.session_state.robot_cajas_actual, 
            "tiempo_segundos": tiempo_final,
            "estado": "Pendiente de Validación",
            "operador": "",
            "sscc": generar_sscc_local()
        }
        
        guardar_estiba(nuevo_registro)
        
        st.session_state.contador_estiba_id += 1
        st.session_state.robot_cajas_actual = 0
        st.session_state.robot_tiempo_inicio = time.time()
        st.toast("🔄 ¡Estiba Completa! El robot cambió de lado. Nueva estiba iniciada.", icon="🤖")
        st.rerun() 
    #-------------------------------------------------------

    st.header("Contador de Pallet Actual")

    c1, c2 = st.columns([3, 3])
    with c1:
        with st.container(border=True):
            st.metric("**Pallet**", f"{st.session_state.contador_estiba_id}")
    with c2:
        with st.container(border=True):
            st.metric("**Cantidad de cajas**", f"{st.session_state.robot_cajas_actual} / {MAX_CAJAS_POR_ESTIBA}")

    if st.button("🚨 Finalizar Estiba (Cierre Manual / Fin de Producción)", type="secondary"):
        tiempo_final = int(time.time() - st.session_state.robot_tiempo_inicio)
        
        nuevo_registro = {
            "id": st.session_state.contador_estiba_id,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hora_cierre": datetime.now().strftime("%H:%M"),
            "linea": st.session_state.orden_activa["linea_produccion"],
            "producto": st.session_state.orden_activa["producto"],
            "sap": st.session_state.orden_activa["sap"],
            "fecha_llenaje": st.session_state.orden_activa["fecha_llenaje"],
            "fecha_vencimiento": st.session_state.orden_activa["fecha_vencimiento"],
            "lote": st.session_state.orden_activa["lote"],
            "turno": 1 if int(datetime.now().strftime("%H")) >= 22 or int(datetime.now().strftime("%H")) < 6 else (2 if int(datetime.now().strftime("%H")) < 14 else 3),
            "cajas_sistema": st.session_state.robot_cajas_actual, 
            "cajas_reales": st.session_state.robot_cajas_actual, 
            "tiempo_segundos": tiempo_final,
            "estado": "Pendiente de Validación",
            "operador": "",
            "sscc": "sscc"
        }
        
        guardar_estiba(nuevo_registro)
        
        st.session_state.contador_estiba_id += 1
        st.session_state.robot_cajas_actual = 0
        st.session_state.robot_tiempo_inicio = time.time()
        st.toast("⚠️ Estiba cerrada manualmente antes del límite. Lista para validación.", icon="📥")
        st.rerun()

    st.write("")

    # 8. Tabla de historial del Lote
    if not validadas_lote_activo:
        st.info(f"🏭 Cambiando configuración. Aún no hay estibas archivadas para el lote específico **{lote_activo}**.")
    else:
        ultimo_registro = validadas_lote_activo[-1]
        with st.container(border=True):
            st.subheader(f"📊 Informacion para: {f_llenaje} - {producto_activo} - {lote_activo}")
            h_col1, h_col2, h_col3 = st.columns(3)
            with h_col1:
                st.markdown(f"**🏭 Línea de Producción:** {ultimo_registro['linea']}")
                st.markdown(f"**📦 Producto:** {ultimo_registro['producto']}")
            with h_col2:
                st.markdown(f"**🔢 Código SAP:** {ultimo_registro['sap']}")
                st.markdown(f"**🏷️ Lote Fijo:** {ultimo_registro['lote']}")
            with h_col3:
                st.markdown(f"**📅 Fecha Llenaje:** {ultimo_registro['fecha_llenaje']}")
                st.markdown(f"**⏳ Fecha Vencimiento:** {ultimo_registro['fecha_vencimiento']}")

        st.write("") 
        
        df_validadas = pd.DataFrame(validadas_lote_activo)
        df_mostrar = df_validadas[["pallet_id", "hora_cierre", "turno", "sscc", "cajas_reales", "operador"]]
        df_mostrar.columns = ["Pallet", "Hora", "Turno", "SSCC", "Cantidad", "Operador"]
        
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

st.divider()


# =====================================================================
# Consulta con filtros
# =====================================================================
with st.expander("🔍 Revisar Historial", expanded=not st.session_state.orden_configurada):

    # Bloque de filtros en columnas
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        fecha_seleccionada = st.date_input("1. Selecciona Fecha:", value=datetime.now(), key="audit_fecha")
        fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")

    lineas_disponibles, productos_disponibles = obtener_valores_unicos_por_fecha(fecha_str)

    with col_f2:
        opciones_linea = ["Todas"] + lineas_disponibles
        linea_seleccionada = st.selectbox("2. Filtrar por Línea:", opciones_linea, key="audit_linea")

    with col_f3:
        opciones_producto = ["Todos"] + productos_disponibles
        producto_seleccionado = st.selectbox("3. Filtrar por Producto:", opciones_producto, key="audit_producto")

    # Ejecucion de la busqueda filtrada
    registros_filtrados = obtener_estibas_filtradas(fecha_str, linea_seleccionada, producto_seleccionado)

    if not registros_filtrados:
        st.info(f"📋 No se encontraron registros para los filtros seleccionados el día {fecha_str}.")
    else:
        texto_producto = f"Producto: {producto_seleccionado}" if producto_seleccionado != "Todos" else "Todos los Productos"
        texto_linea = f"Línea: {linea_seleccionada}" if linea_seleccionada != "Todas" else "Todas las Líneas"

        st.success(f"🗃️ Mostrando registros de **{texto_linea}** y **{texto_producto}**")

        # Tomamos el último registro de la lista filtrada para llenar el encabezado visual
        resumen_auditoria = registros_filtrados[-1]
        
        # Tabla del resumen de consulta
        with st.container(border=True):
            st.subheader(f"📊 Resumen: {texto_linea} - {texto_producto} ({fecha_str})")
            h_col1, h_col2, h_col3 = st.columns(3)
            with h_col1:
                texto_l = resumen_auditoria['linea'] if linea_seleccionada != "Todas" else "Todas"
                st.markdown(f"**🏭 Línea:** {texto_l}")
                texto_p = resumen_auditoria['producto'] if producto_seleccionado != "Todos" else "Todos"
                st.markdown(f"**📦 Producto:** {texto_p}")
            with h_col2:
                st.markdown(f"**🔢 Código SAP:** {resumen_auditoria['sap']}")
                st.markdown(f"**🏷️ Lote:** {resumen_auditoria['lote']}")
            with h_col3:
                st.markdown(f"**📅 Llenaje:** {resumen_auditoria['fecha_llenaje']}")
                st.markdown(f"**⏳ Vencimiento:** {resumen_auditoria['fecha_vencimiento']}")

        st.write("")

        # Tabla de detalles
        df_filtrados = pd.DataFrame(registros_filtrados)
        
        # Mostramos los datos de producción junto al detalle del pallet
        df_mostrar = df_filtrados[["fecha_llenaje", "pallet_id", "producto", "hora_cierre", "turno", "sscc", "cajas_reales", "operador"]]
        df_mostrar.columns = ["Fecha", "Pallet", "Producto", "Hora", "Turno", "SSCC", "Cantidad", "Validó"]
        
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)