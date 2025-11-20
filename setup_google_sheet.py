#!/usr/bin/env python3
"""
Script para configurar la estructura de Google Sheets para Pixely Partners
CORRECCIONES:
1. Borra todos los datos existentes antes de insertar
2. Crea hoja "Ficha Cliente" con datos del cliente
3. Genera contenido relevante para análisis de sentimiento
4. Vincula correctamente: Ficha Cliente <-> id_cliente // Posts <-> link // Comments <-> link
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import random

# Configuración desde config.json del Cliente_01
SPREADSHEET_ID = "1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4"
CREDENTIALS_FILE = "credentials.json"
CLIENT_ID = "eca2c18c-364e-4877-99ef-189b58c1905b"
CLIENT_NAME = "Tech Innovators"
PLATFORM = "Instagram"  # Una sola red social por cliente

def authenticate():
    """Autenticar con Google Sheets API"""
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    return client

def clear_sheet_data(sheet):
    """Borrar TODOS los datos de una hoja (incluyendo headers)"""
    if sheet.row_count > 0:
        sheet.clear()
    print("   ✓ Datos anteriores borrados completamente")

def setup_ficha_cliente_sheet(spreadsheet):
    """Configurar la hoja Ficha Cliente con información del cliente"""
    print("\n📋 Configurando hoja 'Ficha Cliente'...")
    
    # Crear o limpiar la hoja
    try:
        ficha_sheet = spreadsheet.worksheet('Ficha Cliente')
        print("   ✓ Hoja 'Ficha Cliente' encontrada")
        clear_sheet_data(ficha_sheet)
    except gspread.exceptions.WorksheetNotFound:
        ficha_sheet = spreadsheet.add_worksheet(title='Ficha Cliente', rows=10, cols=7)
        print("   ✓ Hoja 'Ficha Cliente' creada")
    
    # Headers vinculados: id_cliente es la clave principal
    headers = [
        'id_cliente',          # UUID vinculado con Posts
        'nombre_cliente',
        'industria',
        'pais',
        'descripcion',
        'fecha_registro',
        'estado'
    ]
    
    # Datos reales del cliente
    data = [[
        CLIENT_ID,
        CLIENT_NAME,
        'Tecnología y Transformación Digital',
        'España',
        'Empresa líder en consultoría tecnológica especializada en transformación digital, inteligencia artificial y soluciones cloud para empresas medianas y grandes.',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Activo'
    ]]
    
    # Escribir todo de una vez
    all_data = [headers] + data
    ficha_sheet.update('A1', all_data, value_input_option='RAW')
    print(f"   ✓ Ficha cliente configurada: {CLIENT_NAME}")
    
    return CLIENT_ID

def setup_posts_sheet(spreadsheet, client_id):
    """Configurar la hoja Posts con contenido relevante para análisis"""
    print("\n📝 Configurando hoja 'Posts'...")
    
    # Crear o limpiar la hoja
    try:
        posts_sheet = spreadsheet.worksheet('Posts')
        print("   ✓ Hoja 'Posts' encontrada")
        clear_sheet_data(posts_sheet)
    except gspread.exceptions.WorksheetNotFound:
        posts_sheet = spreadsheet.add_worksheet(title='Posts', rows=100, cols=9)
        print("   ✓ Hoja 'Posts' creada")
    
    # Headers: link es la clave para vincular con Comments
    headers = [
        'link',               # URL única del post (vincula con Comments)
        'id_cliente',         # UUID vinculado con Ficha Cliente
        'platform',
        'created_at',
        'content',
        'likes',
        'comments_count',
        'shares',
        'views'
    ]
    
    print("   📦 Generando posts con contenido analizable...")
    
    # Contenidos realistas con sentimientos variados para análisis
    contents = [
        "🚀 ¡Gran noticia! Lanzamos nuestra plataforma de IA generativa para empresas. Transformación digital real y medible. #IA #Innovación",
        "💡 El 80% de empresas que adoptan cloud computing reducen costos un 30%. ¿Tu empresa está lista? Webinar gratuito próximamente.",
        "🎯 Caso de éxito: Retail aumenta ventas 45% con machine learning. Los datos son el nuevo petróleo. #DataScience #Resultados",
        "⚡ La IA no es el futuro, es HOY. Implementación sin complicaciones. Agenda tu demo gratuita.",
        "🔐 Ciberseguridad: protege lo más importante. Inversión crítica en 2025. Consulta gratuita disponible.",
        "📊 Empresas data-driven son 23x más propensas a adquirir clientes. La transformación espera por ti.",
        "🌟 'Desde Tech Innovators, productividad +60%' - CTO Fortune 500. Testimonios reales de clientes satisfechos.",
        "🎓 Webinar GRATUITO: Transformación digital para PyMEs. Aprende a competir con gigantes. Inscríbete ya!",
        "💻 Cloud vs On-Premise: análisis completo de costos, ventajas y ROI. Lee nuestro nuevo whitepaper.",
        "🤖 ChatBots inteligentes: atención 24/7, -70% costos, +85% satisfacción cliente. Demo interactiva disponible.",
        "📈 Clientes recuperan inversión en <6 meses. ROI comprobado con casos documentados. Solicita assessment.",
        "🔄 Automatización: libera a tu equipo de tareas repetitivas. Enfócate en estrategia, no en operaciones.",
        "🎨 UX que convierte: rediseñamos tu experiencia digital. De visitantes a clientes fieles en semanas.",
        "⚙️ Arquitectura moderna: APIs y microservicios que escalan. Migración sin interrupciones garantizada.",
        "🌍 Expansión global: tecnología para conquistar mercados internacionales. De España al mundo."
    ]
    
    posts_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(15):
        date = base_date + timedelta(days=i*2, hours=random.randint(9, 20))
        
        posts_data.append([
            f'https://instagram.com/techinnovators/post/{1000+i}',
            client_id,
            PLATFORM,
            date.strftime('%Y-%m-%d %H:%M:%S'),
            contents[i],
            random.randint(150, 4500),
            random.randint(20, 180),
            random.randint(40, 950),
            random.randint(3000, 75000)
        ])
    
    # Escribir todo de una vez
    all_data = [headers] + posts_data
    posts_sheet.update('A1', all_data, value_input_option='RAW')
    print(f"   ✓ {len(posts_data)} posts con contenido relevante generados")
    
    return posts_data

def setup_comments_sheet(spreadsheet, posts_data):
    """Configurar la hoja Comments con sentimientos diversos para análisis"""
    print("\n💬 Configurando hoja 'Comments'...")
    
    # Crear o limpiar la hoja
    try:
        comments_sheet = spreadsheet.worksheet('Comments')
        print("   ✓ Hoja 'Comments' encontrada")
        clear_sheet_data(comments_sheet)
    except gspread.exceptions.WorksheetNotFound:
        comments_sheet = spreadsheet.add_worksheet(title='Comments', rows=300, cols=5)
        print("   ✓ Hoja 'Comments' creada")
    
    # Headers: link vincula con Posts
    headers = [
        'link',               # URL del post (vincula con Posts.link)
        'comment_text',
        'ownerUsername',
        'created_at',
        'likes'
    ]
    
    print("   📦 Generando comentarios con sentimientos diversos...")
    
    # Comentarios POSITIVOS (para análisis de sentimiento)
    positive = [
        "¡Excelente servicio! Implementamos sus soluciones y los resultados son impresionantes 🚀",
        "Totalmente recomendados. Profesionalismo y resultados comprobados. Muy satisfechos.",
        "La mejor decisión para nuestra empresa. ROI increíble en solo 4 meses 💡",
        "Gracias por compartir contenido de tanto valor. Siempre aprendo algo nuevo.",
        "Llevamos un año trabajando juntos. Excelente soporte técnico y resultados constantes.",
        "Transformaron completamente nuestros procesos. Equipo altamente capacitado 👏",
        "Webinar muy profesional y útil. Información práctica que podemos aplicar YA.",
        "Casos de éxito reales y verificables. Transparencia total. Así se trabaja bien."
    ]
    
    # Comentarios NEUTRALES (preguntas e información)
    neutral = [
        "Interesante propuesta. ¿Tienen casos de estudio en mi industria? Me gustaría verlos.",
        "¿Cuáles son los planes de precios para empresas medianas? Necesito cotización.",
        "¿Tiempo estimado de implementación? Tenemos urgencia en Q1 2026.",
        "¿Ofrecen soporte en español 24/7? Es requisito para nuestro equipo.",
        "¿Tienen oficinas o partners en Latinoamérica? Expansión regional planeada.",
        "Buen contenido. Sería útil ver comparativas con otras soluciones del mercado.",
        "¿El entrenamiento del equipo está incluido? ¿Cuántas horas de capacitación?",
        "¿Compatibilidad con SAP y Oracle? Usamos ambos sistemas legacy."
    ]
    
    # Comentarios NEGATIVOS (críticas constructivas)
    negative = [
        "Precios muy altos para PyMEs. Deberían tener opciones más accesibles o escalonadas.",
        "Contacté hace 2 semanas y aún sin respuesta. Deben mejorar tiempos de atención comercial.",
        "Esperaba información más técnica. Mucho marketing y pocas especificaciones reales.",
        "Demo muy básica. Necesito ver funcionalidades avanzadas antes de decidir.",
        "Prometen mucho pero no muestran métricas verificables. ¿Dónde está la transparencia?",
        "Implementación tardó 3 meses más de lo prometido. Planificación deficiente del proyecto."
    ]
    
    # Preguntas técnicas
    questions = [
        "¿Qué stack tecnológico usan? ¿Es compatible con infraestructura AWS?",
        "¿El modelo de pricing es por usuario, por transacción o licencia corporativa?",
        "¿Cumplen con GDPR y normativas europeas de protección de datos?",
        "¿Ofrecen SLA con garantías? ¿Cuál es el uptime comprometido?",
        "¿La migración de datos históricos está incluida? ¿Hay límite de volumen?"
    ]
    
    all_comment_templates = positive + neutral + negative + questions
    
    usernames = [
        'CEO_TechStart', 'DirectorIT_Madrid', 'MariaGomez_Digital', 'JuanPerez_CTO',
        'InnovaConsulting', 'DataScience_Expert', 'CloudArchitect_ES', 'PyME_Digital',
        'TransformacionCorp', 'AI_Specialist', 'CTO_Barcelona', 'DigitalManager_Pro',
        'Empresario_Tech', 'ConsultoraTI_Senior', 'Innovacion_Leader', 'TechDirector_MX',
        'StartupFounder', 'VP_Technology', 'IT_Manager_EU', 'DigitalStrategist'
    ]
    
    comments_data = []
    
    for post in posts_data:
        post_link = post[0]  # link del post para vincular
        post_date_str = post[3]
        post_date = datetime.strptime(post_date_str, '%Y-%m-%d %H:%M:%S')
        
        # 6-12 comentarios por post para análisis robusto
        num_comments = random.randint(6, 12)
        for _ in range(num_comments):
            comment_date = post_date + timedelta(
                hours=random.randint(2, 96),
                minutes=random.randint(0, 59)
            )
            
            comments_data.append([
                post_link,  # Vincula con Posts.link
                random.choice(all_comment_templates),
                random.choice(usernames),
                comment_date.strftime('%Y-%m-%d %H:%M:%S'),
                random.randint(0, 85)
            ])
    
    # Escribir todo de una vez
    all_data = [headers] + comments_data
    comments_sheet.update('A1', all_data, value_input_option='RAW')
    print(f"   ✓ {len(comments_data)} comentarios con sentimientos diversos generados")
    
    return len(comments_data)

def main():
    """Ejecutar configuración completa"""
    print("=" * 70)
    print("🔧 CONFIGURACIÓN DE GOOGLE SHEETS - PIXELY PARTNERS")
    print("=" * 70)
    
    try:
        print("\n🔐 Autenticando con Google Sheets API...")
        client = authenticate()
        
        print(f"📊 Abriendo spreadsheet: {SPREADSHEET_ID}")
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        print(f"   ✓ Spreadsheet: {spreadsheet.title}")
        
        # 1. Configurar Ficha Cliente
        client_id = setup_ficha_cliente_sheet(spreadsheet)
        
        # 2. Configurar Posts
        posts_data = setup_posts_sheet(spreadsheet, client_id)
        
        # 3. Configurar Comments
        num_comments = setup_comments_sheet(spreadsheet, posts_data)
        
        print("\n" + "=" * 70)
        print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"\n📋 Resumen:")
        print(f"   • Cliente: {CLIENT_NAME} ({CLIENT_ID})")
        print(f"   • Posts: {len(posts_data)} registros")
        print(f"   • Comments: {num_comments} registros")
        print(f"\n🔗 Vinculaciones:")
        print(f"   • Ficha Cliente.id_cliente <-> Posts.id_cliente")
        print(f"   • Posts.link <-> Comments.link")
        print(f"\n🌐 Ver spreadsheet:")
        print(f"   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
        print("\n✅ El orchestrator ahora puede leer datos de Google Sheets!")
        print("=" * 70)
        
    except FileNotFoundError:
        print("❌ Error: No se encontró 'credentials.json'")
        print("   Verifica que esté en la raíz del proyecto")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
