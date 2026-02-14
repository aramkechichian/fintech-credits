# Sistema de Reglas de Países

## Descripción General

El sistema de reglas de países permite definir y gestionar reglas de validación específicas para cada país. Estas reglas se aplican durante la creación y actualización de solicitudes de crédito para asegurar que cumplan con los requisitos legales y de negocio de cada país.

## Inicialización Automática

Al iniciar la aplicación con `make up`, el sistema ejecuta automáticamente el script de inicialización (`app/core/init_country_rules.py`) que crea reglas por defecto para todos los países si no existen.

### Reglas por Defecto

El sistema crea automáticamente reglas para los siguientes países:

#### 🇪🇸 España (Spain)
- **Documento requerido**: DNI
- **Reglas de validación**:
  - Verificación de formato de DNI
  - Umbral de monto: Si el monto solicitado supera 50,000 EUR, requiere revisión adicional

#### 🇵🇹 Portugal
- **Documento requerido**: NIF
- **Reglas de validación**:
  - Verificación de formato de NIF
  - Relación ingreso/monto: El monto solicitado no debe exceder el 30% del ingreso mensual

#### 🇮🇹 Italia (Italy)
- **Documento requerido**: Codice Fiscale
- **Reglas de validación**:
  - Verificación de formato de Codice Fiscale
  - Estabilidad financiera: Se requiere estabilidad financiera de al menos 6 meses

#### 🇲🇽 México (Mexico)
- **Documento requerido**: CURP
- **Reglas de validación**:
  - Verificación de formato de CURP
  - Relación ingreso/monto: El monto solicitado no debe exceder el 40% del ingreso mensual

#### 🇨🇴 Colombia
- **Documento requerido**: Cédula de Ciudadanía
- **Reglas de validación**:
  - Verificación de formato de Cédula de Ciudadanía
  - Relación deuda/ingreso: La deuda total no debe exceder el 50% del ingreso mensual

#### 🇧🇷 Brasil (Brazil)
- **Documento requerido**: CPF
- **Reglas de validación**:
  - Verificación de formato de CPF
  - Score de crédito: Se requiere un score mínimo de 600

## Estructura de Datos

### Modelo CountryRule

```python
{
  "country": "Spain",  # Enum: Brazil, Mexico, Portugal, Spain, Italy, Colombia
  "required_document_type": "DNI",
  "description": "Reglas de validación para España - DNI requerido",
  "is_active": true,
  "validation_rules": [
    {
      "rule_type": "document_verification",
      "enabled": true,
      "config": {
        "document_type": "DNI",
        "format_validation": true
      },
      "error_message": "El DNI proporcionado no es válido",
      "requires_review": false
    },
    {
      "rule_type": "amount_threshold",
      "enabled": true,
      "config": {
        "threshold": 50000,
        "currency": "EUR"
      },
      "error_message": "El monto solicitado supera el umbral y requiere revisión adicional",
      "requires_review": true
    }
  ],
  "created_at": "2026-02-13T20:00:00Z",
  "updated_at": "2026-02-13T20:00:00Z"
}
```

### Tipos de Reglas de Validación

El sistema soporta los siguientes tipos de reglas:

1. **`document_verification`**: Verifica el formato y validez del documento de identidad
2. **`amount_threshold`**: Valida que el monto solicitado no supere un umbral definido
3. **`income_ratio`**: Valida la relación entre el monto solicitado y el ingreso mensual
4. **`debt_ratio`**: Valida la relación entre la deuda total y el ingreso mensual
5. **`financial_stability`**: Valida la estabilidad financiera del solicitante
6. **`credit_score`**: Valida el score de crédito mínimo requerido

### Configuración de Reglas

Cada regla de validación puede tener una configuración personalizada en el campo `config`:

```json
{
  "rule_type": "amount_threshold",
  "config": {
    "threshold": 50000,
    "currency": "EUR"
  }
}
```

```json
{
  "rule_type": "income_ratio",
  "config": {
    "max_ratio": 0.3,
    "description": "El monto solicitado no debe exceder el 30% del ingreso mensual"
  }
}
```

```json
{
  "rule_type": "financial_stability",
  "config": {
    "min_income_months": 6,
    "description": "Se requiere estabilidad financiera de al menos 6 meses"
  }
}
```

## API Endpoints

### Crear Regla
```http
POST /country-rules
Authorization: Bearer <token>
Content-Type: application/json

{
  "country": "Spain",
  "required_document_type": "DNI",
  "description": "Reglas de validación para España",
  "is_active": true,
  "validation_rules": [...]
}
```

### Listar Reglas
```http
GET /country-rules?skip=0&limit=100&is_active=true
Authorization: Bearer <token>
```

### Obtener Regla por ID
```http
GET /country-rules/{rule_id}
Authorization: Bearer <token>
```

### Obtener Regla por País
```http
GET /country-rules/country/{country}
Authorization: Bearer <token>
```

### Actualizar Regla
```http
PUT /country-rules/{rule_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "required_document_type": "DNI",
  "description": "Nueva descripción",
  "is_active": true,
  "validation_rules": [...]
}
```

### Eliminar Regla (Soft Delete)
```http
DELETE /country-rules/{rule_id}
Authorization: Bearer <token>
```

## Gestión desde el Frontend

### Acceso

1. Inicia sesión en la aplicación
2. En el menú lateral (sidebar), haz clic en **"Gestionar Reglas de Países"**
3. Verás la lista de todas las reglas configuradas

### Crear Nueva Regla

1. Haz clic en el botón **"Crear Regla"**
2. Completa el formulario:
   - Selecciona el país
   - Ingresa el tipo de documento requerido
   - Agrega una descripción (opcional)
   - Marca si está activa
   - Agrega reglas de validación (opcional)
3. Haz clic en **"Guardar"**

### Editar Regla Existente

1. En la lista de reglas, haz clic en **"Editar"** en la regla que deseas modificar
2. Modifica los campos necesarios
3. Haz clic en **"Guardar"**

### Eliminar Regla

1. En la lista de reglas, haz clic en **"Eliminar"** en la regla que deseas eliminar
2. Confirma la eliminación
3. La regla se desactiva (soft delete) y ya no se aplicará a nuevas solicitudes

### Agregar Reglas de Validación

Dentro del formulario de crear/editar regla:

1. Haz clic en **"+ Agregar Regla"**
2. Selecciona el tipo de regla
3. Configura los parámetros:
   - **Habilitada**: Marca si la regla está activa
   - **Requiere Revisión**: Marca si el incumplimiento requiere revisión manual
   - **Mensaje de Error**: Ingresa el mensaje que se mostrará si la regla falla
4. Puedes agregar múltiples reglas de validación

## Uso en Validaciones (Futuro)

Las reglas de países están diseñadas para ser utilizadas durante la creación y actualización de solicitudes de crédito. La lógica de validación se implementará en el servicio de credit requests.

### Ejemplo de Validación

```python
# Obtener regla del país
country_rule = await get_country_rule_by_country(Country.SPAIN)

# Validar documento
if country_rule:
    # Verificar tipo de documento
    if credit_request.identity_document_type != country_rule.required_document_type:
        raise ValueError("Tipo de documento incorrecto")
    
    # Aplicar reglas de validación
    for validation_rule in country_rule.validation_rules:
        if validation_rule.enabled:
            if validation_rule.rule_type == "amount_threshold":
                threshold = validation_rule.config.get("threshold", 0)
                if credit_request.requested_amount > threshold:
                    if validation_rule.requires_review:
                        credit_request.status = CreditRequestStatus.IN_REVIEW
                    else:
                        raise ValueError(validation_rule.error_message)
```

## Características

- ✅ **Inicialización automática**: Las reglas por defecto se crean al iniciar la aplicación
- ✅ **CRUD completo**: Crear, leer, actualizar y eliminar reglas
- ✅ **Soft delete**: Las reglas eliminadas se desactivan, no se borran permanentemente
- ✅ **Reglas flexibles**: Sistema de configuración extensible para agregar nuevos tipos de reglas
- ✅ **Multi-idioma**: Interfaz disponible en español, inglés, portugués e italiano
- ✅ **Trazabilidad**: Registro de quién creó y modificó cada regla
- ✅ **Gestión visual**: Interfaz web para gestionar reglas sin necesidad de código

## Próximos Pasos

1. **Implementar validación real**: Integrar las reglas en el proceso de creación de solicitudes de crédito
2. **Validación de documentos**: Implementar la lógica de verificación de formato de documentos
3. **Integración con proveedores**: Obtener información de deuda y score de crédito desde proveedores externos
4. **Notificaciones**: Enviar alertas cuando una solicitud requiere revisión adicional
5. **Historial de cambios**: Registrar todos los cambios realizados en las reglas

## Notas Técnicas

- Las reglas se almacenan en la colección `country_rules` de MongoDB
- Solo puede haber una regla activa por país
- Las reglas inactivas no se aplican a nuevas solicitudes
- El campo `config` es flexible y puede contener cualquier estructura JSON según el tipo de regla
- Todas las operaciones requieren autenticación JWT
