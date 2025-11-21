// Particles Background Animation
(function() {
    // Evitar crear múltiples canvas
    if (document.getElementById('particles-canvas')) return;
    
    const canvas = document.createElement('canvas');
    canvas.id = 'particles-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '0';
    canvas.style.pointerEvents = 'none';
    
    document.body.insertBefore(canvas, document.body.firstChild);
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationFrameId;
    
    // Configuración
    const config = {
        particleCount: 80,
        particleSize: 2,
        particleColor: 'rgba(255, 255, 255, 0.6)',
        lineColor: 'rgba(255, 255, 255, 0.15)',
        maxDistance: 150,
        speed: 0.3
    };
    
    // Ajustar canvas al tamaño de ventana
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    // Clase Particle
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * config.speed;
            this.vy = (Math.random() - 0.5) * config.speed;
        }
        
        update() {
            this.x += this.vx;
            this.y += this.vy;
            
            // Rebotar en los bordes
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            
            // Mantener dentro de límites
            this.x = Math.max(0, Math.min(canvas.width, this.x));
            this.y = Math.max(0, Math.min(canvas.height, this.y));
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, config.particleSize, 0, Math.PI * 2);
            ctx.fillStyle = config.particleColor;
            ctx.fill();
        }
    }
    
    // Inicializar partículas
    function init() {
        particles = [];
        for (let i = 0; i < config.particleCount; i++) {
            particles.push(new Particle());
        }
    }
    
    // Dibujar líneas entre partículas cercanas
    function drawLines() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < config.maxDistance) {
                    const opacity = (1 - distance / config.maxDistance) * 0.15;
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`;
                    ctx.lineWidth = 1;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }
    
    // Animar
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        drawLines();
        
        animationFrameId = requestAnimationFrame(animate);
    }
    
    // Iniciar
    resize();
    init();
    animate();
    
    // Redimensionar con ventana
    window.addEventListener('resize', () => {
        resize();
        init();
    });
    
    // Limpiar al desmontar
    window.addEventListener('beforeunload', () => {
        cancelAnimationFrame(animationFrameId);
    });
})();
