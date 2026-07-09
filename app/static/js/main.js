// Initialize AOS animations
AOS.init({
    duration: 1000,
    once: true,
    offset: 100
});

// Counter animation for statistics
function animateCounter(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const currentValue = Math.floor(progress * (end - start) + start);
        element.innerText = currentValue;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Initialize counters when they come into view
const counters = document.querySelectorAll('.counter');
const observerOptions = {
    threshold: 0.5
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const counter = entry.target;
            const target = parseInt(counter.getAttribute('data-target'));
            animateCounter(counter, 0, target, 2000);
            observer.unobserve(counter);
        }
    });
}, observerOptions);

counters.forEach(counter => observer.observe(counter));

// Particles animation for hero section
class ParticleSystem {
    constructor() {
        this.canvas = document.getElementById('particles');
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.resize();
        this.initParticles(100);
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    initParticles(count) {
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                radius: Math.random() * 3 + 1,
                speedX: (Math.random() - 0.5) * 0.5,
                speedY: (Math.random() - 0.5) * 0.5,
                opacity: Math.random() * 0.5 + 0.2
            });
        }
    }
    
    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach(particle => {
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(46, 125, 50, ${particle.opacity})`;
            this.ctx.fill();
            
            particle.x += particle.speedX;
            particle.y += particle.speedY;
            
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;
        });
    }
    
    animate() {
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize particles
new ParticleSystem();

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    let isValid = true;
    const inputs = form.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.id = 'loading-spinner';
        element.appendChild(spinner);
    }
}

// Hide loading spinner
function hideLoading(elementId) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.remove();
}

// Show notification
function showNotification(title, message, type = 'success') {
    Swal.fire({
        title: title,
        text: message,
        icon: type,
        confirmButtonColor: '#2E7D32',
        timer: 3000,
        timerProgressBar: true
    });
}

// Format date for display
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in other scripts
window.utils = {
    showLoading,
    hideLoading,
    showNotification,
    formatDate,
    debounce,
    validateForm
};

/* ============================================
   CATALOG JS - Smart Agriculture AI
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Ajout des interactions sur les éléments du menu
    const menuItems = document.querySelectorAll('.crop-menu-item');
    
    menuItems.forEach(item => {
        // Effet de clic
        item.addEventListener('click', function() {
            const cropName = this.querySelector('.crop-menu-name')?.textContent || '';
            showCropDetail(cropName);
        });
        
        // Effet de survol
        item.addEventListener('mouseenter', function() {
            this.style.borderColor = 'var(--agri-brand-green)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.borderColor = '#f1f5f9';
        });
    });
});

/**
 * Affiche les détails d'une culture
 */
function showCropDetail(cropName) {
    if (typeof Swal !== 'undefined') {
        // Mapping des données des cultures
        const cropData = {
            'Riz': {
                icon: 'fa-seedling',
                description: 'Variété à haut rendement pour conditions humides. Idéal pour les zones tropicales avec irrigation.',
                yield: '4.5 t/ha',
                color: '#2E7D32'
            },
            'Blé': {
                icon: 'fa-wheat-awn',
                description: 'Blé résistant à la sécheresse, adapté aux climats tempérés. Excellente qualité de farine.',
                yield: '3.2 t/ha',
                color: '#D4A017'
            },
            'Maïs': {
                icon: 'fa-corn',
                description: 'Maïs à croissance rapide, rendement élevé. Utilisé pour l\'alimentation humaine et animale.',
                yield: '5.8 t/ha',
                color: '#F4A460'
            },
            'Coton': {
                icon: 'fa-cloud',
                description: 'Coton de qualité supérieure pour l\'industrie textile. Fibres longues et résistantes.',
                yield: '2.1 t/ha',
                color: '#8B8B8B'
            },
            'Café': {
                icon: 'fa-mug-saucer',
                description: 'Café Arabica de haute qualité pour le marché d\'exportation. Arôme riche et équilibré.',
                yield: '1.5 t/ha',
                color: '#6F4E37'
            },
            'Banane': {
                icon: 'fa-banana',
                description: 'Banane sucrée tropicale pour le marché local. Riche en potassium et vitamines.',
                yield: '35.0 t/ha',
                color: '#FFE135'
            },
            'Mangue': {
                icon: 'fa-apple-alt',
                description: 'Mangue Alphonse à haute valeur marchande. Chair sucrée et parfumée.',
                yield: '12.0 t/ha',
                color: '#FF8C00'
            },
            'Noix de Coco': {
                icon: 'fa-tree',
                description: 'Noix de coco polyvalente pour divers produits (huile, lait, fibre). Résistante aux conditions côtières.',
                yield: '80.0 t/ha',
                color: '#8B6B4B'
            }
        };
        
        const data = cropData[cropName] || {
            icon: 'fa-seedling',
            description: 'Culture recommandée par notre IA',
            yield: 'N/A',
            color: 'var(--agri-brand-green)'
        };
        
        Swal.fire({
            title: cropName,
            html: `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; color: ${data.color}; margin-bottom: 1rem;">
                        <i class="fas ${data.icon}"></i>
                    </div>
                    <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">
                        ${data.description}
                    </p>
                    <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.3rem 1rem; background: var(--agri-green-light); border-radius: 20px; margin-top: 0.5rem;">
                        <i class="fas fa-tractor" style="color: var(--agri-brand-green);"></i>
                        <span style="font-weight: 700; color: var(--agri-brand-green);">${data.yield}</span>
                    </div>
                </div>
            `,
            icon: 'info',
            confirmButtonColor: '#1e5e41',
            confirmButtonText: 'Fermer',
            showCancelButton: true,
            cancelButtonColor: '#64748b',
            cancelButtonText: 'Voir en détail',
            customClass: {
                popup: 'crop-detail-popup'
            }
        }).then((result) => {
            if (result.dismiss === Swal.DismissReason.cancel) {
                // Rediriger vers le catalogue complet
                window.location.href = '/catalog';
            }
        });
    } else {
        // Fallback si SweetAlert n'est pas disponible
        alert(`Détails de ${cropName}\n\nConsultez le catalogue complet pour plus d'informations.`);
    }
}

// Export pour utilisation globale
window.showCropDetail = showCropDetail;