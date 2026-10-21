# Sistema de Gestión Empresarial

Aplicación de escritorio desarrollada en Python para centralizar y optimizar la gestión de empleados, equipos, materiales, finanzas, proyectos y actividades operativas.

## Descripción del proyecto

El **Sistema de Gestión Empresarial** es una aplicación de escritorio diseñada para facilitar la organización y el seguimiento de los recursos y procesos de una empresa desde una única plataforma.

La aplicación integra diferentes módulos de gestión que permiten administrar información operativa, organizar los recursos asociados a los proyectos, consultar registros financieros y visualizar actividades pendientes mediante un calendario.

Además, incorpora funcionalidades de notificación y seguimiento de novedades para facilitar el acceso a información relevante y mejorar la planificación de las actividades diarias.

## Funcionalidades principales

### Gestión de empleados
- Registro y administración de la información de los empleados.
- Consulta de perfiles y detalles de cada empleado.
- Asignación de empleados a proyectos.

### Gestión de equipos
- Administración de los equipos disponibles.
- Consulta de información y detalles de los equipos.
- Asignación de equipos a proyectos.

### Gestión de materiales
- Registro y administración de materiales.
- Asociación de materiales con proyectos.
- Seguimiento de asignaciones y devoluciones de materiales.

### Gestión financiera
- Administración de ingresos y gastos.
- Organización de información financiera relacionada con los proyectos.
- Consulta de registros mediante interfaces dedicadas a la gestión financiera.

### Gestión de proyectos
- Organización y consulta de proyectos.
- Asociación de empleados, equipos y materiales.
- Acceso a información detallada para facilitar el seguimiento operativo.

### Calendario y planificación
- Visualización de actividades programadas y tareas pendientes.
- Organización de actividades relacionadas con los proyectos.
- Consulta de fechas relevantes para facilitar la planificación del trabajo.

### Notificaciones y novedades
- Registro y consulta de novedades operativas.
- Visualización de información relevante para el seguimiento de actividades.
- Facilidades para identificar asuntos que requieren atención.

### Autenticación y seguridad
- Interfaz de inicio de sesión.
- Separación de la lógica de autenticación respecto a las vistas de la aplicación.
- Utilidades de seguridad para apoyar la protección de las operaciones del sistema.

## Tecnologías utilizadas

- **Python:** desarrollo de la lógica de negocio y funcionalidades de la aplicación.
- **Git y GitHub:** control de versiones y gestión del código fuente.

> Las tecnologías específicas de interfaz gráfica y almacenamiento deben documentarse de acuerdo con las dependencias y la configuración real del proyecto.

## Estructura del proyecto

```text
desktop-management-system/
├── app/
│   ├── database/    # Acceso y configuración de la base de datos
│   ├── models/      # Modelos y entidades del sistema
│   ├── services/    # Servicios y lógica de negocio
│   ├── utils/       # Funciones auxiliares y utilidades
│   └── views/       # Ventanas, vistas y diálogos
├── assets/          # Imágenes, iconos y recursos visuales
├── ui/              # Estilos de la interfaz
├── crear_admin.py   # Configuración del usuario administrador
├── crear_db.py      # Inicialización de la base de datos
├── main.py          # Punto de entrada de la aplicación
├── requirements.txt # Dependencias del proyecto
├── SISMAEP.spec     # Configuración de compilación con PyInstaller
└── .gitignore       # Archivos excluidos del control de versiones
```

## Instalación y ejecución

### Requisitos previos

- Python instalado y compatible con las dependencias del proyecto.
- Git.
- Sistema operativo compatible con las dependencias de la aplicación.

### 1. Clonar el repositorio

```bash
git clone https://github.com/Velalejandro23/desktop-management-system.git
cd desktop-management-system
```

### 2. Crear un entorno virtual

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

En Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 5. Inicializar la base de datos

Si la aplicación requiere crear una base de datos nueva, ejecuta:

```bash
python crear_db.py
```

### 6. Ejecutar la aplicación

```bash
python main.py
```

**Nota:** revisa la configuración de la aplicación y los scripts de inicialización antes de ejecutarlos. La creación de la base de datos y la configuración del administrador pueden variar según el entorno.

## Objetivos del proyecto

- Centralizar la información operativa en una aplicación de escritorio.
- Facilitar la administración de empleados y recursos empresariales.
- Mejorar la organización de proyectos y la asignación de recursos.
- Simplificar el seguimiento de ingresos y gastos.
- Facilitar la planificación de actividades y tareas pendientes.
- Mantener una estructura de código modular que favorezca el mantenimiento y la evolución del sistema.

## Posibles mejoras futuras

- Ampliar la cobertura de pruebas automatizadas.
- Incorporar informes operativos y financieros adicionales.
- Mejorar los flujos de notificaciones y planificación.
- Fortalecer los mecanismos de respaldo y recuperación de datos.
- Optimizar el proceso de empaquetado y distribución de la aplicación.

## Estado del proyecto

Proyecto en desarrollo. Sus funcionalidades y componentes pueden evolucionar a medida que se incorporen mejoras y nuevas capacidades.

## Autor

**Alejandro Velasquez**

GitHub: [@Velalejandro23](https://github.com/Velalejandro23)

---

*Proyecto de desarrollo de software enfocado en aplicaciones de escritorio, gestión empresarial y organización de recursos.*