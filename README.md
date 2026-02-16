# Fintech Challenge - Sistema de Gestión de Solicitudes de Crédito

## 🚀 Inicio Rápido

### Ejecutar la Aplicación

**Backend:**
```bash
cd fintech-api
make up
```

**Frontend:**
```bash
cd fintech-frontend
npm install
npm run dev
```

El backend estará disponible en `http://localhost:8000` y el frontend en `http://localhost:8001`.

### Acceso al Sistema

**Opción 1: Usar cuenta de administrador por defecto**
- Email: `admin@admin.com`
- Contraseña: `admin`

**Opción 2: Registrarse como nuevo usuario**
- Desde la página de login, haz clic en "Registrarse"
- Completa el formulario con tu email, nombre completo y contraseña
- Una vez registrado, podrás iniciar sesión

> **Nota**: Al ejecutar `make up`, el sistema crea automáticamente el usuario administrador si no existe.

---

## 📋 Módulos del Sistema

### 🔐 Autenticación y Usuarios

Sistema completo de autenticación con JWT:
- **Registro de usuarios**: Los usuarios pueden registrarse con email, nombre completo y contraseña
- **Login con JWT**: Autenticación mediante tokens JWT con expiración de 6 horas
- **Protección de endpoints**: Todos los endpoints protegidos requieren token de autenticación
- **Gestión de sesión**: Manejo automático de sesión expirada con mensajes traducidos

### 💰 Solicitudes de Crédito

Gestión completa del ciclo de vida de solicitudes de crédito:
- **Creación de solicitudes**: Formulario con validación de datos y reglas por país
- **Búsqueda avanzada**: Filtros por país, documento de identidad, estado y paginación (5, 10 o 50 items por página)
- **Visualización de detalles**: Modal con información completa de la solicitud
- **Gestión de estados**: Aprobar, rechazar o poner en revisión solicitudes
- **Validación automática**: Las solicitudes se validan contra reglas específicas del país antes de crearse
- **Notificaciones por email**: Envío automático de emails al cambiar el estado (in_review, approved, rejected)

### 🌍 Reglas de Validación por País

Sistema de reglas configurables por país:
- **Reglas por defecto**: Se inicializan automáticamente para España, Portugal, Italia, México, Colombia y Brasil
- **Validación de documentos**: Verificación de formato y dígitos verificadores (DNI, NIF, CPF, CURP, Codice Fiscale, Cédula)
- **Validación de porcentajes**: Control de relación monto solicitado vs. ingreso mensual (porcentajes configurables)
- **Gestión desde frontend**: Interfaz para editar reglas existentes, habilitar/deshabilitar y ajustar porcentajes
- **Bloqueo de creación**: Si una solicitud no cumple las reglas, se bloquea su creación con mensaje detallado

### 🏦 Integración con Proveedores Bancarios

Sistema preparado para integración con APIs externas:
- **Endpoint de consulta**: `/bank-provider/information` para consultar situación bancaria
- **Preparado para expansión**: Estructura lista para conectar con proveedores por país
- **Mensajes informativos**: Cuando no hay API conectada, muestra mensaje claro al usuario

### 📊 Auditorías y Exportación de Datos

Sistema de exportación de datos con filtros:
- **Filtros avanzados**: Por fecha de solicitud (desde/hasta), estado y países
- **Selección de campos**: Elige qué campos exportar del modelo de solicitud
- **Exportación a Excel**: Genera archivos Excel con los datos filtrados y seleccionados
- **Validación**: Si no hay datos, muestra mensaje en lugar de generar archivo vacío

### 📝 Sistema de Logs

Registro completo de actividad del sistema:
- **Filtros de búsqueda**: Por método HTTP, módulo, endpoint y rango de fechas
- **Visualización paginada**: Lista de logs con paginación (10 items por página)
- **Nombres amigables**: Los endpoints se muestran como módulos traducidos (ej: "Solicitud de Crédito")
- **Exportación a Excel**: Exporta los logs filtrados a Excel
- **Módulos disponibles**: Solo muestra módulos que realmente registran datos

### 🧪 Modo de Prueba

Herramientas para facilitar el desarrollo y testing:
- **Generar datos de prueba**: Crea 50 solicitudes de crédito aleatorias con datos variados
- **Limpiar datos**: Elimina todas las solicitudes de crédito de la base de datos
- **Confirmaciones**: Modales de confirmación antes de ejecutar acciones destructivas

### 🌐 Sistema Multiidioma

Soporte completo para 4 idiomas:
- **Idiomas disponibles**: Español, Inglés, Portugués, Italiano
- **Persistencia**: El idioma seleccionado se guarda en localStorage
- **Traducción completa**: Todos los textos de la interfaz están traducidos
- **Emails multiidioma**: Los emails se envían en el idioma correspondiente al país de la solicitud

### 📧 Notificaciones por Email

Sistema de notificaciones automáticas:
- **Envío asíncrono**: Los emails se envían sin bloquear la respuesta
- **Idioma según país**: El email se envía en el idioma del país de la solicitud
- **Estados notificados**: Se envía email cuando una solicitud se pone en revisión, se aprueba o se rechaza
- **Configuración SMTP**: Requiere configuración de SMTP en variables de entorno

### 🧪 Tests Unitarios

Cobertura completa de tests:
- **Organización por módulo**: Tests separados en carpetas (controllers, services, repositories, utils)
- **Uso de mocks**: Todos los tests usan mocks para aislar las pruebas
- **Cobertura**: Tests para validación de documentos, reglas de país, servicios y controladores

---

## 🛠️ Stack Tecnológico

### Backend

- **Python 3.9+**: Lenguaje de programación
- **FastAPI**: Framework web moderno y rápido para construir APIs
  - Documentación automática con Swagger/OpenAPI
  - Validación automática de datos con Pydantic
  - Soporte nativo para async/await
- **MongoDB**: Base de datos NoSQL orientada a documentos
  - Motor async para operaciones asíncronas
  - Flexibilidad en el esquema de datos
  - Colecciones: `users`, `credit_requests`, `country_rules`, `log_data`
- **JWT (python-jose)**: Autenticación basada en tokens
- **bcrypt**: Hash seguro de contraseñas
- **Pydantic**: Validación y serialización de datos
- **aiosmtplib**: Envío asíncrono de emails

### Frontend

- **React**: Biblioteca para construir interfaces de usuario
- **Vite**: Herramienta de build rápida y moderna
- **Tailwind CSS**: Framework de CSS utility-first
- **Context API**: Gestión de estado (autenticación, idioma)
- **Fetch API**: Cliente HTTP para comunicación con el backend

### Base de Datos

- **MongoDB**: Base de datos principal
  - Almacenamiento de usuarios, solicitudes, reglas y logs
  - Índices en campos clave para optimización
  - Operaciones asíncronas con Motor

---

## 📁 Estructura del Proyecto

```
fintech-challenge/
├── fintech-api/              # Backend (FastAPI)
│   ├── app/
│   │   ├── controllers/      # Endpoints de la API
│   │   ├── models/           # Modelos Pydantic
│   │   ├── services/         # Lógica de negocio
│   │   ├── repositories/     # Acceso a datos
│   │   ├── core/             # Configuración e inicialización
│   │   └── utils/            # Utilidades (validadores, etc.)
│   └── tests/                # Tests unitarios
│
└── fintech-frontend/         # Frontend (React)
    ├── src/
    │   ├── api/              # Cliente API
    │   ├── components/       # Componentes React
    │   ├── pages/            # Páginas
    │   ├── i18n/             # Traducciones
    │   └── utils/            # Utilidades
    └── package.json
```

---

## 🔧 Configuración

### Variables de Entorno (Backend)

**El proyecto incluye un archivo `.env` de prueba** en `fintech-api/` que puedes usar directamente. Este archivo contiene la configuración necesaria para ejecutar el proyecto en modo desarrollo.

Si necesitas personalizar la configuración, puedes editar el archivo `.env` existente o crear uno nuevo. Las variables disponibles son:

```bash
# MongoDB (opcional, default: mongodb://localhost:27017)
MONGODB_URL=mongodb://localhost:27017

# JWT (opcional, tiene valores por defecto)
FINTECH_JWT_SECRET_KEY=tu-clave-secreta-aqui
FINTECH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=360  # 6 horas (default)

# SMTP para emails (opcional, solo si quieres enviar emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
SMTP_FROM_EMAIL=noreply@fintech.com
SMTP_USE_TLS=true
```

**Nota**: El archivo `.env` incluido en el proyecto es para fines de prueba y desarrollo. Para producción, asegúrate de usar valores seguros y no exponer credenciales sensibles.

### Requisitos Previos

- Python 3.9 o superior
- Node.js 16 o superior
- MongoDB (local o remoto)
- npm o yarn

---

## 📚 Documentación Adicional

Para más detalles técnicos, consulta el archivo [`context.md`](context.md) que contiene:
- Arquitectura detallada
- Flujos de validación
- Estructura de datos
- Guías de desarrollo
- Buenas prácticas

---

## 🎯 Características Principales

✅ Sistema completo de autenticación con JWT  
✅ Gestión de solicitudes de crédito con validación automática  
✅ Reglas configurables por país  
✅ Sistema multiidioma (4 idiomas)  
✅ Exportación de datos a Excel  
✅ Sistema de logs y auditoría  
✅ Notificaciones por email  
✅ Tests unitarios completos  
✅ Documentación automática de API (Swagger)  

---

**Desarrollado para el Fintech Challenge**
