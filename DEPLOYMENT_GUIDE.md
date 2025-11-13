# 🌐 DEPLOYMENT GUIDE - Guía Completa de Despliegue

**Pixely Partners v1.0.0**  
**Última actualización:** Enero 2025

---

## 📋 Índice de Opciones de Deployment

1. [Heroku (Más Fácil - Recomendado)](#heroku-mas-facil)
2. [AWS (Escalable - Enterprise)](#aws-escalable)
3. [Google Cloud (Flexible)](#google-cloud-flexible)
4. [Azure (Integración Microsoft)](#azure-integracion-microsoft)
5. [DigitalOcean (Simple y Barato)](#digitalocean-simple)
6. [Servidor Propio (Full Control)](#servidor-propio)

---

## 🎯 ¿Cuál Elegir?

| Plataforma | Dificultad | Costo | Tiempo | Mejor Para |
|-----------|-----------|-------|--------|-----------|
| **Heroku** | ⭐ Muy Fácil | $$ (7-50 USD/mes) | 10 min | Prototipo + Producción pequeña |
| **AWS** | ⭐⭐⭐ Intermedio | $$ Variable | 1-2 horas | Producción escalable |
| **Google Cloud** | ⭐⭐⭐ Intermedio | $$ Variable | 1-2 horas | Equipos Google |
| **Azure** | ⭐⭐⭐ Intermedio | $$ Variable | 1-2 horas | Equipos Microsoft |
| **DigitalOcean** | ⭐⭐ Fácil | $ (5-20 USD/mes) | 30 min | Startups |
| **Servidor Propio** | ⭐⭐⭐⭐ Difícil | $ | 2-4 horas | Control total |

---

# 1️⃣ HEROKU (Más Fácil - ⭐⭐⭐⭐⭐ Recomendado para Empezar)

## Ventajas
✅ Muy fácil de usar  
✅ 1 comando para desplegar  
✅ Tier gratuito disponible (limitado)  
✅ Escalado automático  
✅ SSL/HTTPS incluido  

## Requisitos
- Cuenta en Heroku (gratuita)
- Heroku CLI instalado
- Git instalado
- Docker (opcional)

## Paso a Paso

### 1. Registrate en Heroku
```bash
# Ir a https://signup.heroku.com/
# Crear cuenta gratuita
```

### 2. Instala Heroku CLI
```bash
# Windows (Chocolatey)
choco install heroku-cli

# O descarga desde:
# https://devcenter.heroku.com/articles/heroku-cli
```

### 3. Login
```bash
heroku login
# Te abrirá navegador, confirma
```

### 4. Crea App en Heroku
```bash
cd "c:\Users\ronal\Music\0.-pixely_partners_001_v1\Pixely Partners"

# Crea una app (elige nombre único)
heroku create pixely-partners-app
# O sin nombre, Heroku genera uno automático
heroku create
```

### 5. Configura Variables de Entorno
```bash
# Agrega tu OPENAI_API_KEY
heroku config:set OPENAI_API_KEY=sk-your-key-here

# Verifica
heroku config
```

### 6. Configura para Streamlit
```bash
# Streamlit en Heroku necesita un archivo special
# Ya está incluido en el proyecto, pero verifica que exista:
# frontend/streamlit_config.toml

# Si no existe, créalo:
cat > frontend/.streamlit/config.toml << EOF
[server]
port = $PORT
headless = true
runOnSave = true

[browser]
gatherUsageStats = false

[client]
toolbarMode = "minimal"
EOF
```

### 7. Deploy
```bash
# Con Git
git init
git add .
git commit -m "Initial deployment to Heroku"
git remote add heroku https://git.heroku.com/pixely-partners-app.git
git push heroku main

# O con Docker
heroku stack:set container
git push heroku main
```

### 8. Abre tu App
```bash
# Automáticamente en navegador
heroku open

# O manual
https://pixely-partners-app.herokuapp.com/
```

### 9. Ver Logs
```bash
heroku logs --tail
```

### 10. Escalado (si es necesario)
```bash
# Agregar más recursos
heroku ps:scale web=2

# Ver dynos en uso
heroku ps
```

---

## ⚠️ Limitaciones de Heroku

- **Tier Gratuito:** 550 horas/mes (suficiente si 1 app)
- **Timeout:** 30 segundos (para requests largo, necesitas worker)
- **Almacenamiento:** Efímero (datos se pierden al reiniciar)

**Solución para datos persistentes:**
```bash
# Usar PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev
```

---

# 2️⃣ AWS (Escalable - ⭐⭐⭐⭐ Enterprise)

## Ventajas
✅ Muy escalable  
✅ Muchas opciones  
✅ Buen soporte  
✅ Free tier generoso (primer año)  

## Opciones en AWS

### A. ECS + Fargate (Recomendado para Streamlit)

```bash
# 1. Instala AWS CLI
pip install awscli

# 2. Configura credenciales
aws configure
# Ingresa Access Key ID y Secret Access Key
# Region: us-east-1
# Output: json

# 3. Sube imagen a ECR (Elastic Container Registry)
aws ecr create-repository --repository-name pixely-partners --region us-east-1

# 4. Login en ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# 5. Build imagen
docker build -f Dockerfile.frontend -t pixely-partners-frontend .
docker build -f Dockerfile.orchestrator -t pixely-partners-orchestrator .

# 6. Tag imagen
docker tag pixely-partners-frontend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/pixely-partners:frontend
docker tag pixely-partners-orchestrator:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/pixely-partners:orchestrator

# 7. Push a ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/pixely-partners:frontend
docker push 123456789.dkr.ecm.us-east-1.amazonaws.com/pixely-partners:orchestrator

# 8. Crea ECS Task Definition
aws ecs create-task-definition \
  --family pixely-partners-frontend \
  --container-definitions file://frontend-task.json \
  --execution-role-arn arn:aws:iam::123456789:role/ecsTaskExecutionRole

# 9. Crea ECS Service
aws ecs create-service \
  --cluster pixely-cluster \
  --service-name pixely-frontend \
  --task-definition pixely-partners-frontend:1 \
  --desired-count 1 \
  --launch-type FARGATE
```

**Costo:** Desde $0 (free tier) hasta $50+/mes según uso

---

### B. Elastic Beanstalk (Más Fácil)

```bash
# 1. Instala EB CLI
pip install awsebcli

# 2. Inicializa proyecto
eb init -p docker pixely-partners --region us-east-1

# 3. Deploy
eb create pixely-partners-env
eb deploy

# 4. Abre
eb open
```

**Ventaja:** Muy simplificado, casi como Heroku

---

# 3️⃣ Google Cloud (Flexible - ⭐⭐⭐ Recomendado si usas Google)

## Opción A: Cloud Run (Recomendado)

```bash
# 1. Instala Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# 2. Autentica
gcloud auth login

# 3. Crea proyecto
gcloud projects create pixely-partners --name="Pixely Partners"
gcloud config set project pixely-partners

# 4. Activa API
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 5. Build y Deploy frontend
gcloud run deploy pixely-frontend \
  --source . \
  --build-config cloudbuild.yaml \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=sk-your-key

# 6. Deploy orchestrator (como Cloud Task)
gcloud tasks create pixely-orchestrator \
  --source ./orchestrator

# 7. URL
gcloud run services describe pixely-frontend --platform managed --region us-central1
```

**Costo:** Primer millón de requests/mes GRATIS

---

## Opción B: App Engine

```bash
# 1. Crea app.yaml
cat > app.yaml << EOF
runtime: python311
entrypoint: streamlit run frontend/app.py --server.port 8080 --server.address 0.0.0.0

env: standard
instance_class: F2

env_variables:
  OPENAI_API_KEY: "sk-your-key"

EOF

# 2. Deploy
gcloud app deploy

# 3. Ver
gcloud app browse
```

---

# 4️⃣ Azure (Integración Microsoft - ⭐⭐⭐)

## Opción A: Container Instances (Simple)

```bash
# 1. Instala Azure CLI
choco install azure-cli

# 2. Login
az login

# 3. Crea resource group
az group create --name pixely-rg --location eastus

# 4. Sube imagen a ACR (Azure Container Registry)
az acr create --resource-group pixely-rg --name pixelyacr --sku Basic

# 5. Build y push
az acr build --registry pixelyacr --image pixely-frontend:latest -f Dockerfile.frontend .
az acr build --registry pixelyacr --image pixely-orchestrator:latest -f Dockerfile.orchestrator .

# 6. Deploy Container Instance
az container create \
  --resource-group pixely-rg \
  --name pixely-frontend \
  --image pixelyacr.azurecr.io/pixely-frontend:latest \
  --ports 8501 \
  --environment-variables OPENAI_API_KEY=sk-your-key \
  --registry-login-server pixelyacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password>

# 7. Ver URL
az container show --resource-group pixely-rg --name pixely-frontend --query ipAddress.fqdn
```

---

## Opción B: App Service

```bash
# 1. Crea App Service Plan
az appservice plan create --name pixely-plan --resource-group pixely-rg --sku F1

# 2. Crea Web App
az webapp create --resource-group pixely-rg --plan pixely-plan --name pixely-web

# 3. Deploy desde Git
cd project-folder
git init
git add .
git commit -m "Deploy to Azure"
git remote add azure https://pixely-web.scm.azurewebsites.net:443/pixely-web.git
git push azure main
```

---

# 5️⃣ DigitalOcean (Simple y Barato - ⭐⭐⭐⭐)

## Opción A: App Platform (Más Fácil)

```bash
# 1. Registrate en DigitalOcean
# https://www.digitalocean.com/

# 2. Instala doctl CLI
choco install doctl

# 3. Autentica
doctl auth init

# 4. Crea app desde spec
cat > app.yaml << EOF
name: pixely-partners
services:
- name: frontend
  github:
    repo: tu-usuario/pixely-partners
    branch: main
  build_command: pip install -r requirements.txt
  run_command: streamlit run frontend/app.py --server.port 8080
  http_port: 8080
  envs:
  - key: OPENAI_API_KEY
    value: sk-your-key

- name: orchestrator
  github:
    repo: tu-usuario/pixely-partners
    branch: main
  build_command: pip install -r requirements.txt
  run_command: python orchestrator/analyze.py
  
EOF

# 5. Deploy
doctl apps create --spec app.yaml
```

---

## Opción B: Droplet + Docker Compose

```bash
# 1. Crea Droplet
doctl compute droplet create pixely-partners \
  --region nyc1 \
  --image docker-20-04 \
  --size s-1vcpu-1gb

# 2. SSH en Droplet
ssh root@<IP-DROPLET>

# 3. Clone proyecto
git clone https://github.com/tu-usuario/pixely-partners.git
cd pixely-partners

# 4. Configura .env
nano .env
# Ingresa tu OPENAI_API_KEY

# 5. Deploy
docker-compose up -d

# 6. Nginx reverse proxy (opcional)
# ... ver sección "Servidor Propio" abajo
```

**Costo:** $5-20 USD/mes

---

# 6️⃣ Servidor Propio (Full Control - ⭐⭐⭐⭐⭐)

## Opción A: Ubuntu Server + Docker Compose

### Prerrequisitos
- Servidor Linux (AWS EC2, DigitalOcean, Linode, etc.)
- SSH access
- Dominio (opcional)

### Pasos

```bash
# 1. SSH en servidor
ssh ubuntu@your-server-ip

# 2. Actualiza sistema
sudo apt update && sudo apt upgrade -y

# 3. Instala Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 4. Instala Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 5. Clone proyecto
git clone https://github.com/tu-usuario/pixely-partners.git
cd pixely-partners

# 6. Configura variables
cp .env.example .env
nano .env
# Ingresa OPENAI_API_KEY y otros valores

# 7. Inicia servicios
sudo docker-compose up -d

# 8. Ver logs
docker-compose logs -f
```

---

### Opción B: Con Nginx Reverse Proxy + SSL

```bash
# Crea archivo docker-compose extendido
cat > docker-compose.prod.yml << EOF
version: '3.9'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: pixely-frontend
    ports:
      - "127.0.0.1:8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PIXELY_OUTPUTS_DIR=/app/orchestrator/outputs
    volumes:
      - ./orchestrator/outputs:/app/orchestrator/outputs
    networks:
      - pixely_network
    restart: always

  orchestrator:
    build:
      context: .
      dockerfile: Dockerfile.orchestrator
    container_name: pixely-orchestrator
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./orchestrator/outputs:/app/orchestrator/outputs
    networks:
      - pixely_network
    restart: always
    # Ejecuta una vez al día
    command: sh -c "while true; do python analyze.py; sleep 86400; done"

  nginx:
    image: nginx:latest
    container_name: pixely-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/html:/usr/share/nginx/html:ro
    depends_on:
      - frontend
    networks:
      - pixely_network
    restart: always

networks:
  pixely_network:
    driver: bridge

volumes:
  outputs:
EOF

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

---

### Opción C: Con Let's Encrypt SSL Gratuito

```bash
# 1. Instala Certbot
sudo apt install certbot python3-certbot-nginx -y

# 2. Crea certificado SSL
sudo certbot certonly --standalone -d tu-dominio.com -d www.tu-dominio.com

# 3. Configura Nginx para usar SSL
# Ver archivo de ejemplo: nginx/nginx.ssl.conf en proyecto

# 4. Auto-renovación
sudo certbot renew --dry-run
```

---

# 🚀 RESUMEN DE DEPLOYMENT

## Flujo General (Todos los Métodos)

```
1. Prepara código
   ├─ git init
   ├─ git add .
   ├─ git commit -m "Initial commit"
   └─ git push origin main

2. Elige plataforma
   ├─ Heroku (recomendado para empezar)
   ├─ AWS (escalable)
   ├─ Google Cloud (flexible)
   ├─ Azure (Microsoft)
   ├─ DigitalOcean (simple)
   └─ Tu servidor (full control)

3. Prepara configuración
   ├─ Configura variables de entorno
   ├─ Agrega OPENAI_API_KEY
   ├─ Verifica conexión DB (si la hay)
   └─ Prueba localmente

4. Deploy
   ├─ Sigue pasos de plataforma
   ├─ Ver logs en tiempo real
   ├─ Verifica que funciona
   └─ Configura dominio (opcional)

5. Monitoreo
   ├─ Configura alertas
   ├─ Revisa logs regularmente
   ├─ Escalado si es necesario
   └─ Backups automáticos
```

---

# 📋 CHECKLIST PRE-DEPLOYMENT

```
[ ] Código committeado en Git
[ ] .env.example documentado
[ ] OPENAI_API_KEY configurada
[ ] Tests pasados localmente
[ ] Docker builds sin errores
[ ] docker-compose up --build funciona
[ ] No hay secrets en código
[ ] .gitignore está completo
[ ] Documentación actualizada
[ ] README tiene instrucciones deployment
[ ] Logs configurados
[ ] Health checks implementados
```

---

# 🔒 CONSIDERACIONES DE SEGURIDAD

```
ANTES de producción:

[ ] Usar secrets manager (AWS Secrets, Azure KeyVault)
[ ] SSL/HTTPS habilitado (Let's Encrypt o acme)
[ ] Firewall configurado
[ ] DDoS protection (Cloudflare, AWS Shield)
[ ] WAF (Web Application Firewall)
[ ] Rate limiting
[ ] Monitoreo y logging centralizado
[ ] Backups automáticos
[ ] Plan de recuperación ante desastres
[ ] Auditoría de seguridad
```

---

# 💰 ESTIMADO DE COSTOS

| Plataforma | Tier Básico | Tier Production |
|-----------|-----------|-----------------|
| **Heroku** | GRATIS* | $7-50/mes |
| **AWS** | GRATIS (1 año) | $20-100/mes |
| **Google Cloud** | GRATIS (ciertos límites) | $10-50/mes |
| **Azure** | GRATIS (12 meses) | $10-50/mes |
| **DigitalOcean** | N/A | $5-20/mes |
| **Servidor Propio** | $2-5/mes | $5-50/mes |

*Heroku free tier limitado (550 horas/mes, 1 dyno)

---

# 🎯 RECOMENDACIÓN

### Para EMPEZAR:
→ **Heroku** (10 minutos, muy fácil)

### Para PRODUCCIÓN PEQUEÑA:
→ **DigitalOcean** (simple, barato)

### Para PRODUCCIÓN ESCALABLE:
→ **AWS ECS/Fargate** (robusto, escalable)

### Para EQUIPOS GOOGLE:
→ **Google Cloud Run** (flexible, integrado)

### Para EQUIPOS MICROSOFT:
→ **Azure Container Instances** (fácil, integrado)

---

# ✨ PRÓXIMOS PASOS

1. **Elige una plataforma** (recomiendo Heroku para empezar)
2. **Sigue los pasos** de la sección correspondiente
3. **Prueba en staging** antes de producción
4. **Configura monitoreo** (logs, alertas)
5. **Implementa CI/CD** (GitHub Actions, GitLab CI)

---

**¿Preguntas sobre alguna plataforma específica?**
