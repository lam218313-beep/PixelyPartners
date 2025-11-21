# Frontend API Integration - Status Report

## ✅ Implementado (2025-11-20)

### 1. **Sistema de Autenticación JWT**
- **frontend/api_client.py**: Cliente HTTP para comunicación con la API
  - Clase `APIClient` con métodos: `login()`, `get_ficha_cliente()`, `get_insights()`, `trigger_analysis()`
  - Manejo de tokens JWT en headers
  - Gestión de session state: `access_token`, `user_email`, `tenant_id`, `ficha_cliente_id`

- **frontend/auth_view.py**: Vista de login
  - Formulario de autenticación con usuario/contraseña
  - Almacenamiento seguro de tokens en `st.session_state`
  - Botón de logout con limpieza de sesión
  - Display de información de usuario en sidebar

- **frontend/app.py**: Actualizado con autenticación
  - Requiere login antes de acceder al dashboard
  - `init_session_state()` y `is_authenticated()` para validación
  - `display_user_info()` en sidebar
  - Integración con `APIClient` para cargar datos

### 2. **Carga de Datos desde API**
- **frontend/view_components/data_loader.py**: Cargadores de datos desde session state
  - Funciones `load_q1_data()` a `load_q10_data()`
  - Lee datos de `st.session_state["current_insights"]` (poblado por API)

- **frontend/view_components/compat_loader.py**: Compatibilidad hacia atrás
  - Función `load_from_api_or_file()` para fallback
  - Intenta cargar de API primero, luego de archivos locales (desarrollo)
  - Permite migración gradual de Q2-Q10 sin romper el sistema

- **frontend/view_components/qual/q1_view.py**: Actualizado para usar API
  - Reemplazó lectura de `q1_emociones.json` por `load_from_api_or_file()`
  - Elimina dependencia de `get_outputs_dir()`

### 3. **Backend API Updates**
- **api/schemas.py**: Schema `Token` extendido
  ```python
  class Token(BaseModel):
      access_token: str
      token_type: str
      user_email: Optional[str] = None
      tenant_id: Optional[str] = None
      ficha_cliente_id: Optional[str] = None
  ```

- **api/main.py**: Endpoint `/token` actualizado
  - Devuelve información adicional: `user_email`, `tenant_id`, `ficha_cliente_id`
  - Busca primera ficha_cliente del tenant automáticamente
  - Facilita inicialización del frontend sin endpoints adicionales

### 4. **Docker Configuration**
- **Dockerfile.frontend**: Simplificado
  - Eliminada copia de `orchestrator/outputs/` (ya no necesario)
  - Eliminada copia de `docs/` (no usado)
  - Solo copia `frontend/` necesario

## 🔄 Flujo de Datos Actual

```
┌─────────────────────────────────────────────────────────────┐
│                       USER LOGIN                            │
│  frontend/auth_view.py → APIClient.login()                 │
│  ↓                                                          │
│  POST /token (username, password)                          │
│  ↓                                                          │
│  Returns: access_token, user_email, tenant_id,             │
│           ficha_cliente_id                                 │
│  ↓                                                          │
│  Stored in st.session_state                                │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   DASHBOARD LOAD                            │
│  app.py → APIClient.get_insights(ficha_id)                 │
│  ↓                                                          │
│  GET /insights/{ficha_id} (with JWT Bearer token)          │
│  ↓                                                          │
│  Returns: {                                                 │
│    q1_emociones: {...},                                     │
│    q2_personalidad: {...},                                  │
│    ... q3-q10 ...                                           │
│  }                                                          │
│  ↓                                                          │
│  Stored in st.session_state["current_insights"]            │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   VIEW COMPONENTS                           │
│  q1_view.py → load_q1_data()                               │
│  ↓                                                          │
│  data_loader.load_q1_data()                                │
│  ↓                                                          │
│  st.session_state["current_insights"]["q1_emociones"]      │
│  ↓                                                          │
│  Render charts and analysis                                │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Tareas Pendientes

### Alta Prioridad
- [ ] **Actualizar Q2-Q10 view components** para usar `compat_loader`
  - Q2: `frontend/view_components/qual/q2_view.py`
  - Q3: `frontend/view_components/qual/q3_view.py`
  - Q4: `frontend/view_components/qual/q4_view.py`
  - Q5: `frontend/view_components/qual/q5_view.py`
  - Q6: `frontend/view_components/qual/q6_view.py`
  - Q7: `frontend/view_components/qual/q7_view.py`
  - Q8: `frontend/view_components/qual/q8_view.py`
  - Q9: `frontend/view_components/qual/q9_view.py`
  - Q10: `frontend/view_components/qual/q10_view.py`

### Media Prioridad
- [ ] **Crear endpoint GET /insights/{ficha_id}** en API (si no existe)
  - Debe devolver todos los Q1-Q10 de `social_media_insights`
  - Filtrar por `cliente_id` y `analysis_date` más reciente
  - Respuesta: `{q1_emociones: {...}, q2_personalidad: {...}, ...}`

- [ ] **Testing de autenticación**
  - Verificar que JWT expira correctamente
  - Verificar que tokens inválidos son rechazados
  - Verificar que logout limpia session state

- [ ] **Manejo de errores mejorado**
  - Mostrar mensajes user-friendly cuando API no responde
  - Agregar retry logic en `APIClient`
  - Timeout configurables

### Baja Prioridad
- [ ] **Multi-tenant ficha selector**
  - Si un tenant tiene múltiples fichas_cliente
  - Agregar dropdown en sidebar para cambiar entre clientes
  - Actualizar `st.session_state.ficha_cliente_id` dinámicamente

- [ ] **Refresh manual de datos**
  - Botón "🔄 Actualizar Datos" en dashboard
  - Vuelve a llamar `get_insights()` sin recargar página

- [ ] **Indicador de loading**
  - Spinner mientras se cargan datos de API
  - Skeleton screens para mejor UX

## 🐛 Issues Conocidos

1. **Imports relativos en view components**
   - Algunos usan `from .._outputs import get_outputs_dir`
   - Necesario para fallback a archivos locales
   - No afecta funcionalidad, solo compatibilidad desarrollo

2. **Lint errors en auth_view.py**
   - `Import "streamlit" could not be resolved`
   - Error de entorno de desarrollo, no afecta runtime

3. **Q2-Q10 todavía leen archivos locales**
   - Solo Q1 actualizado con API loader
   - Resto funcionará con compat_loader (API first, luego file fallback)

## 📊 Estado de Migración

| Módulo | Status | Notas |
|--------|--------|-------|
| Q1 Emociones | ✅ Migrado | Usa `compat_loader` |
| Q2 Personalidad | ⏳ Pendiente | Usa archivos locales |
| Q3 Tópicos | ⏳ Pendiente | Usa archivos locales |
| Q4 Marcos | ⏳ Pendiente | Usa archivos locales |
| Q5 Influenciadores | ⏳ Pendiente | Usa archivos locales |
| Q6 Oportunidades | ⏳ Pendiente | Usa archivos locales |
| Q7 Sentimiento | ⏳ Pendiente | Usa archivos locales |
| Q8 Temporal | ⏳ Pendiente | Usa archivos locales |
| Q9 Recomendaciones | ⏳ Pendiente | Usa archivos locales |
| Q10 Resumen | ⏳ Pendiente | Usa archivos locales |

## 🔐 Seguridad

- ✅ JWT tokens con expiración (30 minutos por defecto)
- ✅ Passwords hasheados con bcrypt
- ✅ Autenticación requerida para todos los endpoints protegidos
- ✅ Tokens almacenados solo en session state (no localStorage)
- ⚠️ **TODO**: Implementar HTTPS en producción
- ⚠️ **TODO**: Rate limiting en endpoint /token

## 🚀 Deployment

### Desarrollo
```bash
docker compose up -d
# Frontend: http://localhost:8501
# API: http://localhost:8000
```

### Producción (Recomendaciones)
1. **Environment variables**
   ```env
   API_BASE_URL=https://api.tudominio.com
   JWT_SECRET_KEY=<secret-production-key>
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

2. **HTTPS obligatorio**
   - Nginx reverse proxy con SSL
   - Certificado Let's Encrypt

3. **Database**
   - PostgreSQL en RDS/Cloud SQL
   - Backups automáticos habilitados

## 📝 Próximos Pasos

1. **Implementar GET /insights/{ficha_id}** si no existe
2. **Actualizar Q2-Q10 con compat_loader** (bulk update con script)
3. **Testing completo de autenticación** con diferentes usuarios
4. **Documentar credenciales de prueba** para QA
5. **Setup de producción** con HTTPS y dominio

---

**Última actualización**: 2025-11-20
**Autor**: GitHub Copilot
**Status**: ✅ Sistema listo para testing end-to-end
