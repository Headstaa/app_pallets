# 🏭 Sistema de Auditoría de Producción y Control de Estibas

¡Bienvenido al **Sistema de Auditoría de Producción y Control de Estibas**! Esta es una aplicación web robusta e interactiva desarrollada en **Python** utilizando el framework **Streamlit**. Está diseñada para simular el entorno de empaque automático de una planta industrial, permitiendo el control de calidad en tiempo real, la gestión de lotes y la validación segura de pallets (estibas).

---

## 🚀 Características Principales

* **Configuración Dinámica de Orden de Producción:** Panel de control superior (Header) para fijar Línea, Producto (vía menú desplegable estandarizado), Código SAP y Lote Activo.
* **Simulación de Brazo Robótico:** Automatización en caliente que cuenta las cajas de forma continua y simula el cierre automático del pallet al alcanzar el tope técnico.
* **Simulación de Conexión SAP (Arquitectura Modular):** Integración local con un módulo simulador (`sscc_generador.py`) que genera códigos alfanuméricos aleatorios de 8 caracteres, estructurado con lógica preparada para consumir APIs estándar de SAP (REST/OData) mediante protocolos HTTP seguros.
* **Tolerancia a Cambios de Lote (Planificación Continua):** Capacidad de arrastrar el cumplimiento general de una meta programada (ej. programa de 1,300 cajas) independientemente de los cambios físicos de lote en la línea de producción o transiciones entre los 3 turnos de planta.
* **Control y Verificación de Turnos (Piso de Planta):** Desglose inteligente de cajas reales producidas por cada franja horaria (Turno 1, Turno 2, Turno 3) con control de errores numéricos para evitar caídas del sistema en caso de datos corruptos.
* **Persistencia de Datos Local:** Base de datos relacional integrada en **SQLite** con reseteo inteligente del identificador de pallet por lote, asegurando que cada nueva corrida de producción empiece desde el **Pallet N° 1**.

---

## 🛠️ Estructura del Proyecto

El repositorio está organizado bajo una arquitectura de software limpia y modular:

```text
├── app_pallets.py      # Aplicación principal de Streamlit (Interfaz de usuario y flujos)
├── sscc_generador.py   # Módulo local de simulación para códigos SSCC de SAP
├── database.py         # La base de datos con sus funciones (Inicializacion, peticiones)
├── produccion.db       # Base de datos SQLite (se genera automáticamente en la primera ejecución)
└── requirements.txt    # Dependencias del proyecto para producción

---
✒️ **Developed by:** [Juan Cabezas Tamayo] https://www.linkedin.com/in/juan-jose-cabezas-tamayo-87b402417/ — *Automation & Electronics Tech Student | Python Developer*

