# Fintech Frontend

Frontend React + Vite + Tailwind basado en openmaps.

## Requisitos
- Node.js 18+
- npm 9+ (o pnpm/yarn)
  
## Instalación
```bash
npm install
```

## Ejecutar en desarrollo

1. Asegúrate de que la API esté corriendo:
```bash
cd ../fintech-api
make up
```

2. Ejecuta el frontend:
```bash
npm run dev
```
Abre: http://localhost:8001

## Build de producción
```bash
npm run build
npm run preview
```

## Estructura

- `src/pages/` - Páginas de la aplicación
- `src/components/ui/` - Componentes UI reutilizables
- `src/context/` - Contextos de React (Auth, etc.)
- `src/api/` - Clientes de API
- `src/i18n/` - Internacionalización

## Estado actual

- ✅ Página de login funcional (igual a openmaps)
- ✅ Componentes UI básicos (Card, Input, Button, Spinner)
- ✅ Contextos de autenticación e i18n
- ✅ Estructura lista para trabajar

## Conectar a tu API

Reemplazá `API_BASE_URL` en `src/api/authApi.js` por la URL de tu backend FastAPI.
