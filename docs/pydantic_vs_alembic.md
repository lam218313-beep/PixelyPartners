# Pydantic vs Alembic: Roles Complementarios en Pixely Partners

## 🎯 Resumen Ejecutivo

**Pydantic** y **Alembic** son herramientas **COMPLEMENTARIAS**, no intercambiables. Trabajan en capas diferentes del stack y resuelven problemas distintos.

---

## 📊 Comparación Técnica

| Característica | **Pydantic** | **Alembic** |
|----------------|-------------|-------------|
| **Capa del Stack** | Aplicación (FastAPI) | Base de Datos (PostgreSQL) |
| **Momento de Acción** | **Runtime** (cada request HTTP) | **Design-time** (al cambiar schema) |
| **Objetivo Principal** | Validar datos en memoria | Evolucionar estructura de tablas |
| **Lenguaje** | Python (BaseModel) | SQL + Python (migrations) |
| **Scope** | Request/Response individual | Schema completo de BD |
| **Reversibilidad** | No aplica (valida o rechaza) | Sí (upgrade/downgrade) |

---

## 🔄 Flujo de Trabajo Conjunto

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE HTTP                              │
└──────────────────┬──────────────────────────────────────────┘
                   │ POST /fichas_cliente
                   │ {"brand_name": "Nike", "industry": "Sports"}
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              PYDANTIC (Validación Runtime)                   │
│  ✅ Verifica tipos: brand_name es str?                      │
│  ✅ Valida obligatorios: industry presente?                 │
│  ✅ Aplica reglas: brand_name mínimo 2 caracteres?          │
│  ❌ Si falla → HTTP 422 (sin tocar BD)                      │
└──────────────────┬──────────────────────────────────────────┘
                   │ Datos validados
                   ▼
┌─────────────────────────────────────────────────────────────┐
│           SQLAlchemy ORM (Mapeo Objeto-Relacional)          │
│  Convierte FichaClienteCreate → modelo FichaCliente         │
└──────────────────┬──────────────────────────────────────────┘
                   │ SQL INSERT
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL (Schema por ALEMBIC)                 │
│  Tabla: fichas_cliente                                       │
│  Columnas: id, brand_name, industry, created_at...          │
│  Constraints: NOT NULL, UNIQUE, FOREIGN KEY...               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Rol de Pydantic: El Guardián de la Aplicación

### **Qué Protege:**
1. **Tipos incorrectos**: `{"brand_name": 12345}` → Rechazado antes de llegar a la BD
2. **Campos faltantes**: `{"industry": "Tech"}` sin `brand_name` → Error HTTP 422
3. **Datos malformados**: `{"email": "no-es-email"}` → Validación de formato
4. **Ataques de inyección**: Campos extra maliciosos → Ignorados automáticamente

### **Ejemplo Real:**

```python
# ❌ SIN PYDANTIC (Código vulnerable):
@app.post("/fichas_cliente")
def create_ficha(data: dict, db: Session = Depends(get_db)):
    # Acepta CUALQUIER JSON, incluso:
    # {"brand_name": null, "malicious_field": "DROP TABLE users;"}
    new_ficha = FichaCliente(**data)
    db.add(new_ficha)
    db.commit()  # 💥 Explosión aquí o en la BD

# ✅ CON PYDANTIC (Código seguro):
@app.post("/fichas_cliente")
def create_ficha(
    data: FichaClienteCreate,  # ← Pydantic BaseModel
    db: Session = Depends(get_db)
):
    # Solo acepta: {"brand_name": str, "industry": Optional[str], ...}
    # Campos extra → Ignorados
    # Tipos incorrectos → HTTP 422 con mensaje claro
    new_ficha = FichaCliente(**data.dict())
    db.add(new_ficha)
    db.commit()  # ✅ Seguro: datos ya validados
```

---

## 🏗️ Rol de Alembic: El Arquitecto de la Base de Datos

### **Qué Gestiona:**
1. **Evolución del schema**: Agregar/eliminar columnas sin perder datos
2. **Versionado de estructura**: Historial de cambios en tablas
3. **Migraciones reversibles**: Rollback si algo falla en producción
4. **Constraints de BD**: UNIQUE, FOREIGN KEY, CHECK, DEFAULT

### **Ejemplo Real:**

```python
# FASE 1: Schema inicial (Alembic genera esto)
def upgrade():
    op.create_table(
        'fichas_cliente',
        sa.Column('id', UUID(), primary_key=True),
        sa.Column('brand_name', String(), nullable=False),
        sa.Column('created_at', DateTime(), default=datetime.utcnow)
    )

# FASE 2: Evolución (nueva columna sin perder datos)
def upgrade():
    # Agregar columna para Q12 (Posicionamiento de Comunidad)
    op.add_column('fichas_cliente', 
        sa.Column('seguidores_instagram', Integer(), default=0)
    )
    # Datos existentes mantienen valor 0, aplicación actualiza después

def downgrade():
    # Reversible: quitar columna si hay problema
    op.drop_column('fichas_cliente', 'seguidores_instagram')
```

---

## ⚖️ ¿Por qué AMBOS son necesarios?

### **Caso 1: Solo Pydantic (sin Alembic)**
```python
# ❌ PROBLEMA: Cambio de schema manual
# 1. Modificas models.py (agregas columna)
# 2. Reinicias app
# 3. 💥 BD no tiene la columna → "column does not exist"
# 4. Tienes que hacer ALTER TABLE manual en producción (riesgoso)
```

### **Caso 2: Solo Alembic (sin Pydantic)**
```python
# ❌ PROBLEMA: Datos corruptos en runtime
# 1. Cliente envía {"brand_name": null}
# 2. SQLAlchemy intenta insertar
# 3. 💥 BD rechaza (constraint NOT NULL)
# 4. Error 500 en producción, logs poco claros
# 5. Datos parcialmente insertados → corrupción
```

### **Caso 3: Pydantic + Alembic (CORRECTO)**
```python
# ✅ SOLUCIÓN: Defensa en profundidad
# 1. Pydantic valida en la API (primera línea de defensa)
# 2. Si pasa validación, datos son correctos
# 3. Alembic asegura que la BD tenga el schema esperado
# 4. SQLAlchemy mapea objetos validados → tablas correctas
# 5. Resultado: 0 errores de integridad
```

---

## 🎯 Decisión de Arquitectura para Pixely Partners

### **Estrategia Actual (RECOMENDADA):**

1. **Pydantic Simple (ya implementado):**
   ```python
   class FichaClienteCreate(BaseModel):
       brand_name: str  # ← Validación básica de tipo
       industry: Optional[str] = None
       # No necesitamos validaciones milímétricas AHORA
   ```

2. **Alembic Robusto (ya implementado):**
   ```bash
   # Gestión profesional de schema
   alembic revision --autogenerate -m "Add seguidores fields"
   alembic upgrade head
   ```

### **Evolución Futura (si surge corrupción):**

```python
# Refinar Pydantic SOLO cuando detectes patrones de error:
class FichaClienteCreate(BaseModel):
    brand_name: str = Field(min_length=2, max_length=100)
    industry: Optional[str] = Field(max_length=50)
    seguidores_instagram: int = Field(ge=0, le=1_000_000_000)
    
    @validator('brand_name')
    def brand_name_no_numbers(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError('Brand name cannot contain numbers')
        return v
```

---

## 📋 Checklist de Validación

### ✅ **Lo que SÍ tienes implementado:**
- [x] Pydantic básico en todos los endpoints (`FichaClienteCreate`, `UserCreate`, etc.)
- [x] Alembic con migración inicial (`f62d190dfcf4`)
- [x] SQLAlchemy ORM con relaciones (`Tenant → User → FichaCliente`)
- [x] Validación de autenticación (`get_current_user`)
- [x] Aislamiento multi-tenant (validación por `tenant_id`)

### ⚠️ **Lo que PODRÍAS agregar (solo si hay problemas):**
- [ ] Validators personalizados en Pydantic (ej: regex para emails)
- [ ] Field constraints en Pydantic (min_length, max_length, ge, le)
- [ ] Migraciones de datos complejas en Alembic (transformaciones)
- [ ] Triggers de BD para validaciones complejas

---

## 🚀 Recomendación Final

**MANTÉN la implementación actual.** Está correctamente diseñada:

1. **Pydantic proporciona:**
   - Validación de tipos en tiempo de ejecución ✅
   - Documentación automática en `/docs` ✅
   - Serialización segura ✅

2. **Alembic proporciona:**
   - Migraciones versionadas ✅
   - Evolución segura del schema ✅
   - Reversibilidad en caso de errores ✅

**Solo refina Pydantic si observas:**
- Datos inválidos llegando a la BD (logs de IntegrityError)
- Clientes enviando payloads malformados repetidamente
- Necesidad de validaciones de negocio complejas (ej: "brand_name debe ser único por tenant")

---

## 📚 Referencias

- [Pydantic Docs](https://docs.pydantic.dev/) - Validación de datos
- [Alembic Docs](https://alembic.sqlalchemy.org/) - Migraciones de BD
- [FastAPI with Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/) - Integración completa
