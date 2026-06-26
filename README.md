# 🏭 Sistema de Control de Estibas

<p align="left">
  <img src="https://img.shields.io/github/stars/Headstaa/app_pallets?style=for-the-badge&logo=github&color=1e3a8a" alt="GitHub Stars">
  <img src="https://img.shields.io/github/forks/Headstaa/app_pallets?style=for-the-badge&logo=github&color=0284c7" alt="GitHub Forks">
  <img src="https://img.shields.io/github/license/Headstaa/app_pallets?style=for-the-badge&color=f59e0b" alt="License">
</p>

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux">
</p>

¡Bienvenido al **Sistema de Control de Estibas**! Esta es una aplicación web robusta e interactiva desarrollada en **Python** utilizando el framework **Streamlit**. Está diseñada para simular el entorno de empaque automático de una planta industrial, permitiendo el control de calidad en tiempo real, la gestión de lotes y la validación segura de pallets (estibas).

---

## 🚀 Características Principales

* **Configuración Dinámica de Orden de Producción:** Panel de control superior (Header) para fijar Línea, Producto (vía menú desplegable estandarizado), Código SAP y Lote Activo.
* **Simulación de Brazo Robótico:** Automatización en caliente que cuenta las cajas de forma continua y simula el cierre automático del pallet al alcanzar el tope técnico.
* **Simulación de Conexión SAP (Arquitectura Modular):** Integración local con un módulo simulador (`sscc_generador.py`) que genera códigos alfanuméricos aleatorios de 8 caracteres, estructurado con lógica preparada para consumir APIs estándar de SAP (REST/OData) mediante protocolos HTTP seguros.
* **Tolerancia a Cambios de Lote (Planificación Continua):** Capacidad de arrastrar el cumplimiento general de una meta programada (ej. programa de 1,300 cajas) independientemente de los cambios físicos de lote en la línea de producción o transiciones entre los 3 turnos de planta.
* **Control y Verificación de Turnos:** Desglose inteligente de cajas reales producidas por cada franja horaria (Turno 1, Turno 2, Turno 3) con control de errores numéricos para evitar caídas del sistema en caso de datos corruptos.
* **Persistencia de Datos Local:** Base de datos relacional integrada en **SQLite** con reseteo inteligente del identificador de pallet por lote, asegurando que cada nueva corrida de producción empiece desde el **Pallet N° 1**.

---
## Video demostración en horizontal.


https://github.com/user-attachments/assets/179d74ad-648a-4987-8a7d-8f8192e39571


## Video desmotración en vertical.


https://github.com/user-attachments/assets/f685fdaf-3e8f-4dfa-a110-6c81cde36b2b


---
# 📋 Sistema de Control de Planillas y Paletizado Industrial

Este proyecto es una aplicación web interactiva desarrollada en **Python** con el framework **Streamlit**, diseñada para entornos de empaque industrial. Su objetivo principal es registrar, validar y controlar el flujo de paletizado en finales de línea (líneas de producción como Volpak), integrando la generación de códigos **SSCC de 18 dígitos**, control de firmas de operadores y almacenamiento de datos en una base local **SQLite**.

---

## 🚀 Instalación y Ejecución Local

Sigue estos pasos para clonar el proyecto, configurar el entorno virtual en Linux y ejecutar la aplicación correctamente:

### Clonar el Repositorio
Abre tu terminal y clona el proyecto desde GitHub:
```bash
git clone [https://github.com/Headstaa/app_pallets.git](https://github.com/Headstaa/app_pallets.git)
cd app_pallets
```
### Crear el entorno virtual
```bash
python -m venv .venv
```

### Activar el entorno virtual
```
source .venv/bin/activate
```

### Instalar las librerías requeridas
```
pip install -r requirements.txt
```
### Ejecutar la Aplicación
```
streamlit run app.py
```
---

## 🛠️ Estructura del Proyecto

El repositorio está organizado bajo una arquitectura de software limpia y modular:

```text
├── app.py              # Aplicación principal de Streamlit (Interfaz de usuario y flujos)
├── sscc_generador.py   # Módulo local de simulación para códigos SSCC de SAP
├── database.py         # La base de datos con sus funciones (Inicializacion, peticiones)
├── produccion.db       # Base de datos SQLite (se genera automáticamente en la primera ejecución)
├── estilos.py          # Mejoras adaptativas de los estilos + mobile 
└── requirements.txt    # Dependencias del proyecto para producción
```
---
✒️ **Developed by:** [Juan Cabezas Tamayo] (https://www.linkedin.com/in/juan-jose-cabezas-tamayo-87b402417/) — *Automation & Electronics Tech Student | Python Developer*

