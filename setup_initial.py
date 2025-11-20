# Script para configuración inicial del sistema
# Crea tenant, usuario admin y ficha de cliente

import requests
import json

API_BASE_URL = "http://localhost:8000"

print("="*80)
print("PIXELY PARTNERS - Configuración Inicial")
print("="*80)

# Paso 1: Registrar primer usuario (admin)
print("\n1. Creando tenant y usuario admin...")
register_data = {
    "email": "admin@pixelypartners.com",
    "password": "pixelyadmin2025",
    "full_name": "Admin Pixely Partners",
    "tenant_name": "Pixely Partners Agency"
}

response = requests.post(f"{API_BASE_URL}/register", json=register_data)
if response.status_code == 200:
    user = response.json()
    print(f"✅ Usuario admin creado: {user['email']}")
    print(f"   - User ID: {user['id']}")
    print(f"   - Tenant ID: {user['tenant_id']}")
else:
    print(f"⚠️  Usuario ya existe o error: {response.text}")

# Paso 2: Autenticar
print("\n2. Autenticando usuario admin...")
login_data = {
    "username": "admin@pixelypartners.com",
    "password": "pixelyadmin2025"
}

response = requests.post(f"{API_BASE_URL}/token", data=login_data)
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"✅ Token obtenido: {access_token[:50]}...")
else:
    print(f"❌ Error en autenticación: {response.text}")
    exit(1)

headers = {"Authorization": f"Bearer {access_token}"}

# Paso 3: Crear ficha de cliente
print("\n3. Creando ficha de cliente de prueba...")
ficha_data = {
    "brand_name": "Tech Innovators",
    "industry": "Technology",
    "brand_archetype": "Creator",
    "tone_of_voice": "Professional, Innovative, Inspiring",
    "target_audience": "Tech entrepreneurs, startups, innovators aged 25-45",
    "competitors": ["TechCorp", "InnovateLab", "Digital Pioneers"]
}

response = requests.post(f"{API_BASE_URL}/fichas_cliente", json=ficha_data, headers=headers)
if response.status_code == 200:
    ficha = response.json()
    print(f"✅ Ficha cliente creada: {ficha['brand_name']}")
    print(f"   - Ficha ID: {ficha['id']}")
    print(f"\n" + "="*80)
    print("IMPORTANTE: Agrega este UUID al archivo .env:")
    print("="*80)
    print(f"FICHA_CLIENTE_ID={ficha['id']}")
    print("="*80)
    
    # Guardar en archivo temporal
    with open("ficha_cliente_id.txt", "w") as f:
        f.write(ficha['id'])
    print("\n✅ UUID guardado en archivo: ficha_cliente_id.txt")
else:
    print(f"❌ Error al crear ficha: {response.text}")
    exit(1)

# Paso 4: Verificar usuarios
print("\n4. Listando usuarios del tenant...")
response = requests.get(f"{API_BASE_URL}/users", headers=headers)
if response.status_code == 200:
    users_data = response.json()
    print(f"✅ Total de usuarios: {users_data['total']}")
    for user in users_data['users']:
        print(f"   - {user['email']} ({user['role']}) - Active: {user['is_active']}")
else:
    print(f"⚠️  Error al listar usuarios: {response.text}")

print("\n" + "="*80)
print("CONFIGURACIÓN INICIAL COMPLETADA")
print("="*80)
print("\nPróximos pasos:")
print("1. Actualizar .env con FICHA_CLIENTE_ID (ver arriba)")
print("2. Configurar GOOGLE_SHEETS_SPREADSHEET_ID en .env")
print("3. Rebuild orchestrator: docker compose build orchestrator")
print("4. Lanzar sistema completo: docker compose up -d")
