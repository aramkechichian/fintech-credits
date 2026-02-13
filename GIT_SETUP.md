# Comandos Git para conectar el repositorio

## 1. Agregar todos los archivos al staging
```bash
git add .
```

## 2. Hacer commit inicial
```bash
git commit -m "Initial commit: Fintech Challenge - Auth system and credit requests backend"
```

## 3. Agregar el repositorio remoto
```bash
# Si tu repo es HTTPS:
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git

# O si es SSH:
git remote add origin git@github.com:TU_USUARIO/TU_REPO.git
```

## 4. Verificar el remote agregado
```bash
git remote -v
```

## 5. Push al repositorio remoto
```bash
# Primera vez (crear la rama main/master en el remoto):
git push -u origin master

# O si tu repo usa 'main' en lugar de 'master':
git branch -M main
git push -u origin main
```

## Comandos adicionales útiles

### Ver el estado
```bash
git status
```

### Ver los archivos que se van a commitear
```bash
git status --short
```

### Si necesitas cambiar la URL del remote
```bash
git remote set-url origin NUEVA_URL
```

### Si ya existe un remote y quieres reemplazarlo
```bash
git remote remove origin
git remote add origin TU_REPO_URL
```
