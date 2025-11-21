# Frontend Assets - CSS Styles

Este directorio contiene los archivos CSS externos para personalizar la interfaz de Pixely Partners.

## Estructura de Archivos

```
assets/
├── login_styles.css      # Estilos del formulario de login
├── sidebar_styles.css    # Estilos del sidebar y navegación
├── header_footer.css     # Estilos del header y footer
└── README.md            # Este archivo
```

## Cómo Trabajar con los Estilos

### 1. Editar CSS Directamente

Puedes editar cualquiera de los archivos `.css` en este directorio. Los cambios se aplicarán automáticamente cuando reinicies el contenedor frontend:

```bash
docker compose restart frontend
```

### 2. Probar Estilos Localmente (Fuera de Docker)

Para trabajar más cómodamente, puedes crear un archivo HTML de prueba:

**test_styles.html**
```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="login_styles.css">
    <link rel="stylesheet" href="sidebar_styles.css">
    <link rel="stylesheet" href="header_footer.css">
</head>
<body>
    <!-- Copia aquí el HTML generado por Streamlit para probar -->
</body>
</html>
```

Abre este archivo en tu navegador y ajusta los CSS hasta que estén como quieres.

### 3. Selectores de Streamlit Importantes

#### Login Page
- `[data-testid="stForm"]` - Formulario de login
- `[data-testid="stForm"] input` - Campos de texto
- `[data-testid="stForm"] button` - Botón de submit

#### Sidebar
- `[data-testid="stSidebar"]` - Container del sidebar
- `[data-testid="stRadio"]` - Menú de navegación
- `[data-testid="stCheckbox"]` - Checkboxes

#### General
- `[data-testid="stHeader"]` - Header de Streamlit
- `[data-testid="stToolbar"]` - Toolbar (Deploy button, etc)
- `.main .block-container` - Contenedor principal

### 4. Inspeccionar Elementos en el Navegador

Para encontrar los selectores correctos:
1. Abre la aplicación en el navegador
2. Click derecho → "Inspeccionar elemento" (F12)
3. Busca los atributos `data-testid` en el HTML
4. Usa esos selectores en tu CSS

## Workflow Recomendado

1. **Desarrollo Local**
   - Edita los archivos CSS en este directorio
   - Usa un HTML local para previsualizar rápidamente

2. **Pruebas en Docker**
   ```bash
   docker compose restart frontend
   ```

3. **Inspección en Vivo**
   - Abre http://localhost:8501
   - Usa DevTools del navegador para ajustes finos
   - Copia los cambios finales a los archivos CSS

4. **Commit Changes**
   ```bash
   git add frontend/assets/*.css
   git commit -m "style: update login/sidebar styles"
   ```

## Tips

- **Usa `!important`** solo cuando sea necesario para sobrescribir estilos de Streamlit
- **Prefiere selectores específicos** como `[data-testid="..."]` en lugar de clases genéricas
- **Mantén la consistencia** de colores, espaciados y tipografía entre archivos
- **Comenta secciones** importantes para facilitar mantenimiento futuro

## Colores por Defecto (Personalízalos)

```css
--primary-color: #4CAF50;
--secondary-color: #007bff;
--danger-color: #dc3545;
--background-light: #f8f9fa;
--border-color: #e0e0e0;
--text-dark: #333;
--text-light: #666;
```
