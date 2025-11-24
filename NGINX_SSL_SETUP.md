# 🔐 Nginx + SSL/TLS Configuration Guide

## 📋 Arquitectura

```
Internet (HTTPS)
    ↓
Nginx (puerto 443) ← Certbot (SSL certificates)
    ↓
Frontend (Streamlit:8501) [Solo público]
```

### Servicios:
- **Público**: Frontend vía HTTPS (partners.pixely.pe)
- **Privado**: API, Adminer, DB (solo red interna Docker)

---

## 🚀 Configuración Inicial

### 1. Verificar DNS
Asegúrate de que `partners.pixely.pe` apunta a la IP de tu VM:

```bash
# Verificar DNS
nslookup partners.pixely.pe

# Debe retornar la IP de tu VM
```

### 2. Configurar Firewall (En la VM)

```bash
# Permitir HTTP (80) para validación de Certbot
sudo ufw allow 80/tcp

# Permitir HTTPS (443)
sudo ufw allow 443/tcp

# Verificar
sudo ufw status
```

### 3. Inicializar Certificados SSL

**IMPORTANTE**: Asegúrate de que los servicios estén levantados primero:

```bash
# Levantar servicios sin nginx
docker compose up -d db api frontend orchestrator adminer

# Esperar que inicien (30 segundos)
sleep 30

# Ejecutar script de inicialización SSL
bash scripts/init-letsencrypt.sh
```

El script te preguntará:
- **¿Usar modo STAGING?**: Responde `Y` para testing (recomendado la primera vez)
- Una vez verificado que funciona, re-ejecuta con `N` para producción

### 4. Verificar Certificados

```bash
# Ver certificados obtenidos
docker compose run --rm certbot certificates

# Debe mostrar:
# Certificate Name: partners.pixely.pe
# Domains: partners.pixely.pe
# Expiry Date: [fecha en ~90 días]
```

---

## 🔄 Activar Configuración SSL

Una vez obtenidos los certificados:

```bash
# 1. Activar configuración SSL
# El archivo ssl.conf ya está en nginx/conf.d/

# 2. Reiniciar nginx para aplicar cambios
docker compose restart nginx

# 3. Verificar logs
docker logs pixely_nginx

# Debe mostrar: "Configuration is ok" y "Reloaded"
```

---

## ✅ Verificación del Sistema

### 1. Test de Conectividad

```bash
# Test HTTP (debe redirigir a HTTPS)
curl -I http://partners.pixely.pe

# Debe retornar: HTTP/1.1 301 Moved Permanently
# Location: https://partners.pixely.pe

# Test HTTPS
curl -I https://partners.pixely.pe

# Debe retornar: HTTP/2 200
```

### 2. Test SSL Grade

Verificar calidad del SSL en: https://www.ssllabs.com/ssltest/

- Ingresa: `partners.pixely.pe`
- Objetivo: **A o A+**

### 3. Verificar Frontend

Abre en navegador: `https://partners.pixely.pe`

Debe mostrar el dashboard de Streamlit sin errores de certificado.

---

## 🔄 Renovación Automática

Los certificados se renuevan automáticamente cada 12 horas vía el servicio Certbot.

### Verificar Renovación Manual

```bash
# Simular renovación (dry-run)
docker compose run --rm certbot renew --dry-run

# Debe mostrar: "Congratulations, all simulated renewals succeeded"
```

### Logs de Renovación

```bash
# Ver logs de certbot
docker logs pixely_certbot

# Ver última renovación
docker compose exec certbot certbot certificates
```

---

## 📁 Estructura de Archivos

```
PixelyPartners/
├── nginx/
│   ├── nginx.conf              # Configuración principal
│   └── conf.d/
│       ├── default.conf        # HTTP only (pre-SSL)
│       └── ssl.conf            # HTTPS + SSL (activo)
├── certbot/
│   ├── conf/                   # Certificados (persistente)
│   │   ├── live/
│   │   │   └── partners.pixely.pe/
│   │   │       ├── fullchain.pem
│   │   │       ├── privkey.pem
│   │   │       └── chain.pem
│   │   ├── archive/
│   │   └── renewal/
│   └── www/                    # Webroot para validación
├── scripts/
│   └── init-letsencrypt.sh     # Script de inicialización
└── docker-compose.yml          # Nginx + Certbot habilitados
```

---

## 🛠️ Comandos Útiles

### Gestión de Servicios

```bash
# Ver estado de servicios
docker compose ps

# Ver logs de nginx
docker logs -f pixely_nginx

# Reiniciar nginx (si cambias config)
docker compose restart nginx

# Recargar nginx (sin downtime)
docker compose exec nginx nginx -s reload
```

### Gestión de Certificados

```bash
# Ver certificados
docker compose run --rm certbot certificates

# Renovar manualmente (solo si expiran pronto)
docker compose run --rm certbot renew

# Revocar certificado
docker compose run --rm certbot revoke --cert-name partners.pixely.pe
```

### Debug

```bash
# Test de configuración nginx
docker compose exec nginx nginx -t

# Ver configuración activa
docker compose exec nginx cat /etc/nginx/conf.d/ssl.conf

# Ver archivos de certificado
docker compose exec nginx ls -la /etc/letsencrypt/live/partners.pixely.pe/
```

---

## 🚨 Troubleshooting

### Error: "Connection refused" al ejecutar init-letsencrypt.sh

**Solución**: Asegúrate de que frontend esté corriendo:

```bash
docker compose up -d frontend
docker logs pixely_frontend
# Debe mostrar: "You can now view your Streamlit app in your browser"
```

### Error: "DNS resolution failed"

**Solución**: Verifica que el DNS esté propagado:

```bash
# Esperar propagación DNS (puede tomar hasta 48h)
nslookup partners.pixely.pe 8.8.8.8

# Si no resuelve, espera más tiempo
```

### Error: "Rate limit exceeded"

**Solución**: Estás usando certificados de producción muy frecuentemente.

```bash
# Usar modo staging para testing
bash scripts/init-letsencrypt.sh
# Responder Y a "Use STAGING"

# Esperar 1 semana para usar producción nuevamente
```

### Error: "Certificate files not found"

**Solución**: Los volúmenes no están persistiendo correctamente.

```bash
# Verificar permisos
ls -la certbot/conf/

# Recrear volúmenes
docker compose down -v
bash scripts/init-letsencrypt.sh
```

### Nginx no inicia

```bash
# Ver logs detallados
docker compose logs nginx

# Test de sintaxis
docker compose run --rm nginx nginx -t

# Verificar puertos en uso
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

---

## 🔒 Seguridad

### Configuraciones Aplicadas:

- ✅ TLS 1.2 y 1.3 únicamente
- ✅ Cifrados seguros (Mozilla Intermediate)
- ✅ HSTS habilitado (31536000 segundos)
- ✅ Headers de seguridad (X-Frame-Options, X-Content-Type-Options, etc.)
- ✅ Renovación automática de certificados
- ✅ API y Adminer NO expuestos públicamente

### Recomendaciones Adicionales:

```bash
# Cambiar SECRET_KEY en .env (producción)
# Generar una nueva con:
openssl rand -hex 32

# Actualizar contraseñas de base de datos
# En .env cambiar: POSTGRES_PASSWORD, ORCHESTRATOR_PASSWORD
```

---

## 📊 Monitoreo

### Health Checks

```bash
# Check SSL certificate expiry
docker compose run --rm certbot certificates | grep "Expiry Date"

# Check nginx status
docker compose exec nginx nginx -t

# Check all services
docker compose ps --all
```

### Logs Centralizados

```bash
# Ver todos los logs
docker compose logs -f

# Solo nginx y certbot
docker compose logs -f nginx certbot

# Desde timestamp específico
docker compose logs --since 2024-01-01T00:00:00 nginx
```

---

## 📞 Contacto y Soporte

- **Dominio**: partners.pixely.pe
- **Email SSL**: lsckryl@gmail.com
- **Organización**: Pixely Partners

Para problemas específicos, revisa los logs primero:
```bash
docker compose logs --tail=100 nginx certbot
```

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0.0
