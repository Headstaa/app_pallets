# app.py
import streamlit as st
import time
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Importaciones modulares locales
from estilos import cargar_css_industrial
from sscc_generador import generar_sscc_local
from database import (
    inicializar_base_de_datos, 
    guardar_estiba, 
    obtener_estibas_por_estado, 
    obtener_estibas_filtradas, 
    obtener_valores_unicos_por_fecha,
    obtener_siguiente_pallet_id,
    ejecutar_query_directa,
    obtener_metricas_programa
)

# Configuración Inicial de la Página
st.set_page_config(page_title="0467.MANAG.REC.022 V 1.0 Control de Estibas", page_icon="📋", layout="wide")

# 🔥 Cargar estilos responsivos desde el nuevo archivo
cargar_css_industrial()

# Inicializar Base de Datos Central
inicializar_base_de_datos()

# ============================================================
#  LÓGICA DE BACKEND - CONTROL DE ESTADOS DE LA ORDEN
# ============================================================
if "orden_configurada" in st.session_state and st.session_state.orden_configurada:
    st.session_state.contador_estiba_id = obtener_siguiente_pallet_id(
        st.session_state.orden_activa["linea_produccion"],
        st.session_state.orden_activa["producto"],
        st.session_state.orden_activa["lote"]
    )
else:
    st.session_state.contador_estiba_id = 1

if "robot_cajas_actual" not in st.session_state:
    st.session_state.robot_cajas_actual = 0
if "robot_tiempo_inicio" not in st.session_state:
    st.session_state.robot_tiempo_inicio = time.time()

MAX_CAJAS_POR_ESTIBA = 10  
st_autorefresh(interval=5000, key="refresh_industrial")

if "orden_activa" not in st.session_state:
    st.session_state.orden_activa = {
        "linea_produccion": "", "producto": "", "sap": "",
        "fecha_llenaje": datetime.now().strftime("%Y-%m-%d"),
        "fecha_vencimiento": "", "lote": ""
    }
if "orden_configurada" not in st.session_state:
    st.session_state.orden_configurada = False

# ============================================================
#  CONTROL DE CABECERA Y DATOS DE LA ORDEN
# ============================================================
st.title("🏭 0467.MANAG.REC.022 V 1.0 Control de Estibas")
st.caption("Panel de Validación y Control Integrado con Robot Paletizador")
st.write("")

with st.expander("📝 Configurar Datos de la Línea y Producto", expanded=not st.session_state.orden_configurada):
    OPCIONES_LINEAS = ["Selecciona una linea...", "Volpak", "Laudenberg", "Enflex", "Nalbach"]
    OPCIONES_PRODUCTOS = [
    "Selecciona un producto...",
    # --- MILO ACTIV-GO  ---
    "MILO Activ-Go Doypack x 100g",
    "MILO Activ-Go Doypack x 150g",
    "MILO Activ-Go Doypack x 220g",
    "MILO Activ-Go Doypack x 320g",
    "MILO Activ-Go Doypack x 375g",
    "MILO Activ-Go Doypack x 440g",
    "MILO Activ-Go Doypack x 590g",
    "MILO Activ-Go Doypack x 800g",
    "MILO Activ-Go Doypack x 1500g",
    
    # --- MILO NUTRI-FIT / FREE ---
    "MILO Nutri-Fit Doypack x 200g",
    "MILO Nutri-Fit Doypack x 500g",
    "MILO Nutri-Fit Doypack x 700g",
    "MILO Nutri-Fit Doypack x 1100g",
    
    # --- NESQUIK CHOCOLATE ---
    "NESQUIK Chocolate Doypack x 200g",
    "NESQUIK Chocolate Doypack x 400g",
    "NESQUIK Chocolate Doypack x 900g",
    
]
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        linea_actual = st.session_state.orden_activa["linea_produccion"]
        idx_defecto = OPCIONES_LINEAS.index(linea_actual) if linea_actual in OPCIONES_LINEAS else 0
        v_linea = st.selectbox("Línea de Producción:", options=OPCIONES_LINEAS, index=idx_defecto)
    with col_h2:
        prod_actual = st.session_state.orden_activa["producto"]
        idx_defecto = OPCIONES_PRODUCTOS.index(prod_actual) if prod_actual in OPCIONES_PRODUCTOS else 0
        producto = st.selectbox("Producto:", options=OPCIONES_PRODUCTOS, index=idx_defecto)
        
    col_h3, col_h4 = st.columns(2)
    with col_h3:
        sap = st.text_input("Código SAP:", value=st.session_state.orden_activa["sap"])
    with col_h4:
        lote = st.text_input("Número de Lote:", value=st.session_state.orden_activa["lote"])
        
    col_h5, col_h6 = st.columns(2)
    with col_h5:
        try:
            fecha_default = datetime.strptime(st.session_state.orden_activa["fecha_llenaje"], "%Y-%m-%d")
        except (ValueError, TypeError):
            fecha_default = datetime.now()
        f_llenaje = st.date_input("Fecha Llenaje:", value=fecha_default)
    with col_h6:
        f_vencimiento = st.text_input("Vencimiento (Texto):", value=st.session_state.orden_activa["fecha_vencimiento"])

    if st.button("Fijar Información de Lote", type="primary", use_container_width=True):
        if not v_linea or not lote or producto == "Selecciona un producto...":
            st.error("⚠️ Error crítico: Todos los campos operativos de la cabecera son obligatorios.")
        else:
            st.session_state.orden_activa = {
                "linea_produccion": v_linea, "producto": producto, "sap": sap,
                "fecha_llenaje": f_llenaje.strftime("%Y-%m-%d"), "fecha_vencimiento": f_vencimiento, "lote": lote
            }
            st.session_state.orden_configurada = True
            if "contador_estiba_id" in st.session_state:
                del st.session_state.contador_estiba_id
            st.success("¡Header de producción fijado correctamente!")
            st.rerun()

if st.session_state.orden_configurada:
    with st.container(border=True):
        st.subheader("📋 Datos de Producción")
        st.write("")
        col_f1, col_f2 = st.columns(2)
        with col_f1: st.markdown(f"**🏭 Línea:** {st.session_state.orden_activa['linea_produccion']}")
        with col_f2: st.markdown(f"**📦 SKU:** {st.session_state.orden_activa['producto']}")
            
        col_f3, col_f4 = st.columns(2)
        with col_f3: st.markdown(f"**🔢 Código SAP:** {st.session_state.orden_activa['sap']}")
        with col_f4: st.markdown(f"**🏷️ Lote:** {st.session_state.orden_activa['lote']}")
            
        col_f5 = st.columns(1)[0]
        with col_f5: st.markdown(f"**📅 Llenaje:** {st.session_state.orden_activa['fecha_llenaje']}")
            
        col_f6 = st.columns(1)[0]
        with col_f6: st.markdown(f"**⏳ Vencimiento:** {st.session_state.orden_activa['fecha_vencimiento']}")
else:
    st.warning("⚠️ Alerta Operativa: Orden no configurada. Los registros entrantes carecerán de metadatos de cabecera.")

# ============================================================
#  COLA DE VERIFICACIÓN EN TIEMPO REAL
# ============================================================
st.write("")
st.header("📥 Validación Obligatoria de Operador")

pendientes = obtener_estibas_por_estado("Pendiente de Validación")

if not pendientes:
    st.success("✅ Cola Vacía: No existen pallets pendientes de revisión en este momento.")
else:
    estiba_a_revisar = pendientes[0]
    with st.container(border=True):
        st.markdown(f"🔬 **Validando Pallet N° {estiba_a_revisar['pallet_id']}**")
        st.markdown("---")
        
        col_rev1, col_rev2 = st.columns(2)
        with col_rev1: v_pallet_id = st.number_input("N° Pallet Corregido:", value=int(estiba_a_revisar["pallet_id"]), key=f"edit_p_{estiba_a_revisar['id']}")
        with col_rev2: v_lote_final = st.text_input("Confirmar Lote:", value=str(estiba_a_revisar["lote"]), key=f"edit_l_{estiba_a_revisar['id']}")
            
        col_rev3, col_rev4 = st.columns(2)
        with col_rev3: v_hora_final = st.text_input("Hora Cierre:", value=estiba_a_revisar.get("hora_cierre", datetime.now().strftime("%H:%M")), key=f"edit_h_{estiba_a_revisar['id']}")
        with col_rev4: v_cajas_reales = st.number_input("Cajas Reales:", value=int(estiba_a_revisar["cajas_sistema"]), key=f"edit_c_{estiba_a_revisar['id']}")
            
        col_rev5, col_rev6 = st.columns(2)
        with col_rev5: v_sscc_final = st.text_input("Código SSCC:", value=str(estiba_a_revisar["sscc"]), key=f"edit_s_{estiba_a_revisar['id']}")
        with col_rev6: v_operador_final = st.text_input("Firma Operador:", value=str(estiba_a_revisar["operador"]), key=f"edit_o_{estiba_a_revisar['id']}")

        st.write("")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("💾 Validar y Guardar", type="primary", key=f"btn_save_{estiba_a_revisar['id']}", use_container_width=True):
                if not v_operador_final.strip():
                    st.session_state[f"error_operador_{estiba_a_revisar['id']}"] = True
                else:
                    if f"error_operador_{estiba_a_revisar['id']}" in st.session_state:
                        del st.session_state[f"error_operador_{estiba_a_revisar['id']}"]
                    
                    try: hora_editada = int(v_hora_final.split(":")[0])
                    except: hora_editada = int(datetime.now().strftime("%H"))
                    
                    turno_calculado = 1 if hora_editada >= 22 or hora_editada < 6 else (2 if hora_editada < 14 else 3)
                    
                    # 🔥 Llamada limpia al backend modular
                    query_update = """
                        UPDATE estibas 
                        SET pallet_id = ?, hora_cierre = ?, turno = ?, lote = ?, 
                            cajas_reales = ?, sscc = ?, operador = ?, estado = 'Validada'
                        WHERE id = ?
                    """
                    ejecutar_query_directa(query_update, (int(v_pallet_id), str(v_hora_final), int(turno_calculado), str(v_lote_final), 
                                                          int(v_cajas_reales), str(v_sscc_final), str(v_operador_final), estiba_a_revisar['id']))
                    st.success("Estiba guardada con éxito.")
                    st.rerun()

            if st.session_state.get(f"error_operador_{estiba_a_revisar['id']}", False):
                st.error("❌ Firma Requerida: Digita tu nombre para poder validar el registro.")

        with col_btn2:
            if st.button("🗑️ Descartar Registro Erróneo", type="secondary", key=f"btn_del_{estiba_a_revisar['id']}", use_container_width=True):
                ejecutar_query_directa("DELETE FROM estibas WHERE id = ?", (estiba_a_revisar['id'],))
                st.toast("Registro descartado correctamente.", icon="🗑️")
                st.rerun()

# ============================================================
#  CONTROL DE PRODUCCIÓN GENERAL (DASHBOARD)
# ============================================================
st.write("")
st.header("📊 Métricas de Control del Lote y Programa")

if not st.session_state.orden_configurada:
    st.info("💡 Proporcione un encabezado válido en la sección superior para desplegar las estadísticas de producción.")
else:
    linea_activa = st.session_state.orden_activa["linea_produccion"]
    producto_activo = st.session_state.orden_activa["producto"]
    lote_activo = st.session_state.orden_activa["lote"]
    
    ####ESTE DATO SE RECIBE DE LA PROGRAMACION EN KPI
    CANTIDAD_PROGRAMADA = 1300 

    # 🔥 Llamada limpia al módulo database
    todas_del_programa, validadas_lote_activo = obtener_metricas_programa(linea_activa, producto_activo, lote_activo)

    cajas_turno1 = sum(int(e["cajas_reales"] or 0) for e in validadas_lote_activo if int(e["turno"]) == 1)
    cajas_turno2 = sum(int(e["cajas_reales"] or 0) for e in validadas_lote_activo if int(e["turno"]) == 2)
    cajas_turno3 = sum(int(e["cajas_reales"] or 0) for e in validadas_lote_activo if int(e["turno"]) == 3)

    gran_total_programa = sum(int(e["cajas_reales"] or 0) for e in todas_del_programa)
    faltante_programa = max(0, CANTIDAD_PROGRAMADA - gran_total_programa)
    porcentaje_cumplimiento = (gran_total_programa / CANTIDAD_PROGRAMADA) * 100 if CANTIDAD_PROGRAMADA > 0 else 0

    with st.container(border=True):
        st.markdown(f"#### 🎯 Avance del Programa ({producto_activo})")
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Cantidad Programada", f"{CANTIDAD_PROGRAMADA:,} Cajas")
        col_p2.metric("Faltante General", f"{faltante_programa:,} Cajas")
        col_p3.metric("Porcentaje Cumplimiento", f"{porcentaje_cumplimiento:.1f}%")

    st.write("")
    st.markdown(f"##### Desglose Producción Lote Activo: **{lote_activo}**")
    t_col1, t_col2, t_col3, t_col4 = st.columns([1, 1, 1, 1.2])
    with t_col1:
        with st.container(border=True): st.metric("Total Turno 1", f"{cajas_turno1} unds")
    with t_col2:
        with st.container(border=True): st.metric("Total Turno 2", f"{cajas_turno2} unds")
    with t_col3:
        with st.container(border=True): st.metric("Total Turno 3", f"{cajas_turno3} unds")
    with t_col4:
        with st.container(border=True): st.metric("Total cajas", f"{cajas_turno1+cajas_turno2+cajas_turno3:,} unds")

    # ============================================================
    #  MONITOREO DINÁMICO DEL ROBOT PALETIZADOR
    # ============================================================
    st.write("")
    st.subheader("Estatus del Brazo Robotizado")
    
    if st.button("🔧 Simular Pulso PLC (Caja colocada por Robot +1)", use_container_width=True):
        st.session_state.robot_cajas_actual += 1

    if st.session_state.robot_cajas_actual >= MAX_CAJAS_POR_ESTIBA:
        tiempo_final = int(time.time() - st.session_state.robot_tiempo_inicio)
        nuevo_registro = {
            "id": st.session_state.contador_estiba_id, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hora_cierre": datetime.now().strftime("%H:%M"),
            "turno": 1 if int(datetime.now().strftime("%H")) >= 22 or int(datetime.now().strftime("%H")) < 6 else (2 if int(datetime.now().strftime("%H")) < 14 else 3),
            "linea": linea_activa, "producto": producto_activo, "sap": st.session_state.orden_activa["sap"], 
            "fecha_llenaje": st.session_state.orden_activa["fecha_llenaje"], "fecha_vencimiento": st.session_state.orden_activa["fecha_vencimiento"], 
            "lote": lote_activo, "cajas_sistema": st.session_state.robot_cajas_actual, "cajas_reales": st.session_state.robot_cajas_actual, 
            "tiempo_segundos": tiempo_final, "estado": "Pendiente de Validación", "operador": "", "sscc": generar_sscc_local()
        }
        guardar_estiba(nuevo_registro)
        st.session_state.contador_estiba_id += 1
        st.session_state.robot_cajas_actual = 0
        st.session_state.robot_tiempo_inicio = time.time()
        st.toast("¡Pallet lleno! Robot rotando posición.", icon="🤖")
        st.rerun()

    c_rb1, c_rb2 = st.columns(2)
    with c_rb1:
        with st.container(border=True): st.metric("ID Siguiente Pallet", f"N° {st.session_state.contador_estiba_id}")
    with c_rb2:
        with st.container(border=True): st.metric("Llenado Física Actual", f"{st.session_state.robot_cajas_actual} / {MAX_CAJAS_POR_ESTIBA} Cajas")

    if st.button("🚨 Cierre Manual de Pallet (Fin de Turno / Llenaje)", type="secondary", use_container_width=True):
        tiempo_final = int(time.time() - st.session_state.robot_tiempo_inicio)
        nuevo_registro = {
            "id": st.session_state.contador_estiba_id, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hora_cierre": datetime.now().strftime("%H:%M"), "linea": linea_activa, "producto": producto_activo, 
            "sap": st.session_state.orden_activa["sap"], "fecha_llenaje": st.session_state.orden_activa["fecha_llenaje"], 
            "fecha_vencimiento": st.session_state.orden_activa["fecha_vencimiento"], "lote": lote_activo,
            "turno": 1 if int(datetime.now().strftime("%H")) >= 22 or int(datetime.now().strftime("%H")) < 6 else (2 if int(datetime.now().strftime("%H")) < 14 else 3),
            "cajas_sistema": st.session_state.robot_cajas_actual, "cajas_reales": st.session_state.robot_cajas_actual, 
            "tiempo_segundos": tiempo_final, "estado": "Pendiente de Validación", "operador": "", "sscc": "Generando..."
        }
        guardar_estiba(nuevo_registro)
        st.session_state.contador_estiba_id += 1
        st.session_state.robot_cajas_actual = 0
        st.session_state.robot_tiempo_inicio = time.time()
        st.toast("Forzado manual enviado a cola.", icon="⚠️")
        st.rerun()

    st.write("")
    st.markdown(f"📊 **Bitácora Física de Entrega del Lote Activo**")
    if not validadas_lote_activo:
        df_vacia = pd.DataFrame(columns=["Pallet ID", "Hora Cierre", "Turno", "Código SSCC", "Cajas", "Operador"])
        st.dataframe(df_vacia, use_container_width=True, hide_index=True)
    else:
        df_validadas = pd.DataFrame(validadas_lote_activo)
        df_mostrar = df_validadas[["pallet_id", "hora_cierre", "turno", "sscc", "cajas_reales", "operador"]]
        df_mostrar.columns = ["Pallet ID", "Hora Cierre", "Turno", "Código SSCC", "Cajas", "Operador"]
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

# ============================================================
#  MÓDULO AUDITOR: REVISIÓN DE ARCHIVO HISTÓRICO
# ============================================================
st.write("")
with st.expander("🔍 Módulo de Auditoría: Consultar Historial Antiguo", expanded=False):
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        fecha_seleccionada = st.date_input("Filtrar por Fecha:", value=datetime.now(), key="audit_fecha")
        fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")
    
    lineas_disponibles, productos_disponibles = obtener_valores_unicos_por_fecha(fecha_str)
    
    with col_f2: linea_seleccionada = st.selectbox("Filtrar por Línea:", ["Todas"] + lineas_disponibles, key="audit_linea")
    with col_f3: producto_seleccionada = st.selectbox("Filtrar por SKU Producto:", ["Todos"] + productos_disponibles, key="audit_producto")

    registros_filtrados = obtener_estibas_filtradas(fecha_str, linea_seleccionada, producto_seleccionada)

    if not registros_filtrados:
        st.info("No se encontraron coincidencias operativas para los filtros provistos.")
    else:
        df_filtrados = pd.DataFrame(registros_filtrados)
        df_mostrar_audit = df_filtrados[["fecha_llenaje", "pallet_id", "producto", "hora_cierre", "turno", "sscc", "cajas_reales", "operador"]]
        df_mostrar_audit.columns = ["Fecha Llenaje", "Pallet", "Producto", "Hora", "Turno", "SSCC", "Cantidad Reales", "Auditor/Firma"]
        st.dataframe(df_mostrar_audit, use_container_width=True, hide_index=True)