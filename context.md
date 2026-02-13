# Fintech Challenge - Contexto del Proyecto

## 📋 Descripción General

Aplicación fintech con frontend en React y backend en FastAPI para gestión de solicitudes de crédito. Sistema completo de autenticación con JWT y soporte multiidioma.

## 🏗️ Arquitectura

### Backend (`fintech-api/`)
- **Framework**: FastAPI (Python 3.9+)
- **Base de datos**: MongoDB (Motor async)
- **Autenticación**: JWT con python-jose
- **Seguridad**: bcrypt para hash de contraseñas
- **Puerto**: 8000

### Frontend (`fintech-frontend/`)
- **Framework**: React + Vite
- **Estilos**: Tailwind CSS
- **i18n**: Sistema propio de traducciones
- **Puerto**: 8001 (desarrollo)

## 🔐 Autenticación

### Endpoints de Autenticación
- `POST /auth/register` - Registro de usuarios
- `POST /auth/login` - Login (retorna JWT)
- `GET /auth/me` - Información del usuario autenticado (requiere token)

### Endpoints de Credit Requests
- `POST /credit-requests` - Crear solicitud de crédito (requiere token)
- `GET /credit-requests` - Listar mis solicitudes (requiere token)
- `GET /credit-requests/{request_id}` - Obtener solicitud específica (requiere token)

### Modelo de Usuario
- `email` (EmailStr, único)
- `full_name` (string, 1-100 caracteres)
- `hashed_password` (bcrypt)
- `created_at`, `updated_at` (datetime)
- `is_active` (boolean)

### Seguridad
- Contraseñas hasheadas con bcrypt
- Tokens JWT con expiración configurable (30 min por defecto)
- Endpoints protegidos con Bearer token
- Validación de datos en frontend y backend

## 🌍 Sistema Multiidioma

### Idiomas Soportados
- **Español (es)** - Por defecto
- **Inglés (en)**
- **Portugués (pt)**
- **Italiano (it)**

### Implementación
- Archivos JSON en `fintech-frontend/src/i18n/translations/`
- Context API para gestión de idioma
- Persistencia en localStorage
- Selector de idioma en Header

## 📁 Estructura del Proyecto

### Backend
```
fintech-api/
├── app/
│   ├── controllers/     # Endpoints de la API
│   │   ├── auth_controller.py
│   │   ├── credit_request_controller.py
│   │   └── test_controller.py
│   ├── models/          # Modelos Pydantic
│   │   ├── user.py
│   │   └── credit_request.py
│   ├── repositories/    # Acceso a datos
│   │   ├── user_repository.py
│   │   └── credit_request_repository.py
│   ├── services/       # Lógica de negocio
│   │   ├── auth_service.py
│   │   └── credit_request_service.py
│   ├── core/           # Configuración
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logging.py
│   └── main.py         # Aplicación FastAPI
└── pyproject.toml
```

### Frontend
```
fintech-frontend/
├── src/
│   ├── api/            # Cliente API
│   │   └── authApi.js
│   ├── components/     # Componentes reutilizables
│   │   ├── ui/         # Componentes UI base
│   │   └── Header.jsx
│   ├── context/        # Context API
│   │   └── AuthContext.jsx
│   ├── i18n/           # Internacionalización
│   │   ├── I18nContext.jsx
│   │   └── translations/
│   ├── pages/          # Páginas
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   └── HomePage.jsx
│   └── App.jsx
└── package.json
```

## 🚀 Funcionalidades Implementadas

### ✅ Completadas
- [x] Sistema de registro de usuarios
- [x] Sistema de login con JWT
- [x] Protección de endpoints con tokens
- [x] Página de inicio post-login
- [x] Header con selector de idioma
- [x] Sistema multiidioma (4 idiomas)
- [x] Logout
- [x] Validación de formularios
- [x] Manejo de errores mejorado
- [x] Logging detallado en backend
- [x] Modelo de Credit Request
- [x] Repository para Credit Requests
- [x] Service para Credit Requests
- [x] Controller para Credit Requests (crear, listar, obtener)
- [x] Endpoints protegidos con JWT

### 🚧 Pendientes
- [ ] UI para crear solicitud de crédito
- [ ] UI para listar solicitudes de crédito
- [ ] UI para ver detalles de solicitud
- [ ] Integración con proveedor de información bancaria
- [ ] Lógica de validación de riesgo (comentada, pendiente)
- [ ] Sistema de auditoría (comentado, pendiente)
- [ ] Procesamiento en segundo plano (comentado, pendiente)
- [ ] Actualizar estado de solicitud (endpoint)
- [ ] Dashboard con estadísticas

## 🔧 Configuración

### Variables de Entorno (Backend)
- `MONGODB_URL` - URL de MongoDB (default: `mongodb://localhost:27017`)
- `FINTECH_JWT_SECRET_KEY` - Clave secreta para JWT
- `FINTECH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Expiración de tokens (default: 30)

### CORS
Orígenes permitidos:
- `http://localhost:5173`
- `http://localhost:3000`
- `http://localhost:8001`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:8001`

## 📝 Comandos Útiles

### Backend
```bash
cd fintech-api
make install      # Instalar dependencias
make run          # Ejecutar servidor (dev)
make up           # Ejecutar servidor (prod)
make mongo-up     # Iniciar MongoDB
make test         # Ejecutar tests
```

### Frontend
```bash
cd fintech-frontend
npm install       # Instalar dependencias
npm run dev       # Ejecutar en desarrollo
npm run build     # Build para producción
```

## 🗄️ Base de Datos

### Colecciones

#### users
- `_id` (ObjectId)
- `email` (string, único, indexado)
- `full_name` (string)
- `hashed_password` (string)
- `created_at` (datetime)
- `updated_at` (datetime)
- `is_active` (boolean)

#### credit_requests
- `_id` (ObjectId)
- `user_id` (ObjectId, referencia a users)
- `country` (enum: Brazil, Mexico, Portugal, Spain, Italy, Colombia)
- `full_name` (string)
- `identity_document` (string)
- `requested_amount` (float, > 0)
- `monthly_income` (float, > 0)
- `request_date` (datetime)
- `status` (enum: pending, in_review, approved, rejected, cancelled)
- `bank_information` (object opcional):
  - `bank_name` (string)
  - `account_number` (string)
  - `account_type` (string)
  - `routing_number` (string)
  - `iban` (string)
  - `swift` (string)
  - `provider_data` (object)
- `created_at` (datetime)
- `updated_at` (datetime)

## 🔄 Flujo de Autenticación

1. Usuario se registra → `POST /auth/register`
2. Usuario hace login → `POST /auth/login` → Recibe JWT
3. Frontend guarda token en localStorage
4. Requests autenticados incluyen header: `Authorization: Bearer <token>`
5. Backend valida token y obtiene usuario → `GET /auth/me`

## 📌 Notas Importantes

- El frontend corre en puerto **8001** (no 5173 estándar)
- MongoDB debe estar corriendo antes de iniciar el backend
- Los tokens JWT expiran en 30 minutos por defecto
- El idioma por defecto es español
- Las contraseñas deben tener mínimo 6 caracteres
- El email debe ser único en el sistema

## 📋 Modelo de Credit Request

### Campos Requeridos
- `country`: Enum (Brazil, Mexico, Portugal, Spain, Italy, Colombia)
- `full_name`: Nombre completo del solicitante
- `identity_document`: Documento de identidad
- `requested_amount`: Monto solicitado (float > 0)
- `monthly_income`: Ingreso mensual (float > 0)

### Campos Automáticos
- `user_id`: ID del usuario que crea la solicitud
- `request_date`: Fecha de solicitud (automática)
- `status`: Estado inicial "pending"
- `bank_information`: Información bancaria del proveedor (opcional)
- `created_at`, `updated_at`: Timestamps

### Estados Disponibles
- `pending`: Solicitud creada, pendiente de revisión
- `in_review`: En proceso de revisión
- `approved`: Aprobada
- `rejected`: Rechazada
- `cancelled`: Cancelada

### Lógica Adicional (Pendiente)
La creación de solicitudes tiene comentarios para implementar:
- Validación de riesgo (debt-to-income ratio, límites por país)
- Sistema de auditoría (logging para compliance)
- Procesamiento en segundo plano (credit score, fraud detection)
- Notificaciones (email/SMS)
- Integraciones externas (credit bureaus, banking APIs, KYC/AML)

## 🎯 Próximos Pasos

1. ✅ Implementar modelo y endpoints para solicitudes de crédito
2. Crear formulario de solicitud de crédito (UI)
3. Implementar listado de solicitudes (UI)
4. Integrar proveedor de información bancaria
5. Implementar lógica de validación de riesgo
6. Dashboard con métricas

---

**Última actualización**: 2026-02-13
