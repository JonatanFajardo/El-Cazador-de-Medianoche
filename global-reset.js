// Script para botón de reinicio global flotante
document.addEventListener('DOMContentLoaded', function() {
    const decisions = localStorage.getItem('cazadorMedianoche_decisions');
    const currentPage = window.location.pathname.split('/').pop();
    
    // Mostrar el botón si hay decisiones guardadas O si estamos en el índice
    if ((decisions && Object.keys(JSON.parse(decisions)).length > 0) || currentPage === 'index.html' || currentPage === '') {
        createGlobalResetButton();
    }
    
    // Escuchar cambios en localStorage para mostrar/ocultar botón
    window.addEventListener('storage', function(e) {
        if (e.key === 'cazadorMedianoche_decisions') {
            const existingBtn = document.getElementById('global-reset-btn');
            if (e.newValue && Object.keys(JSON.parse(e.newValue)).length > 0) {
                if (!existingBtn) {
                    createGlobalResetButton();
                }
            } else {
                if (existingBtn) {
                    existingBtn.remove();
                }
            }
        }
    });
});

function createGlobalResetButton() {
    // Evitar duplicados
    if (document.getElementById('global-reset-btn')) {
        return;
    }
    
    const button = document.createElement('button');
    button.id = 'global-reset-btn';
    button.className = 'global-reset-btn';
    button.innerHTML = '🔄';
    button.title = 'Reiniciar Historia - Comenzar nueva aventura';
    
    button.addEventListener('click', function() {
        const currentPage = window.location.pathname.split('/').pop();
        const decisions = localStorage.getItem('cazadorMedianoche_decisions');
        const hasDecisions = decisions && Object.keys(JSON.parse(decisions)).length > 0;
        
        if (currentPage === 'index.html' || currentPage === '') {
            // En el índice, comportamiento diferente
            if (hasDecisions) {
                const confirmed = confirm('🔄 ¿Reiniciar tu aventura actual?\n\n' +
                                        'Tienes decisiones guardadas. ¿Quieres borrarlas y comenzar una nueva historia?\n\n' +
                                        '¿Continuar?');
                
                if (confirmed) {
                    localStorage.removeItem('cazadorMedianoche_decisions');
                    button.innerHTML = '✅';
                    button.style.background = 'linear-gradient(135deg, #27ae60, #229954)';
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
            } else {
                // No hay decisiones, ir directamente a comenzar
                window.location.href = 'seccion-01.html';
            }
        } else {
            // En otras páginas, comportamiento original
            const confirmed = confirm('🔄 ¿Reiniciar tu aventura actual?\n\n' +
                                    'Se borrarán todas tus decisiones y podrás comenzar desde el principio ' +
                                    'eligiendo diferentes opciones.\n\n' +
                                    '¿Continuar?');
            
            if (confirmed) {
                localStorage.removeItem('cazadorMedianoche_decisions');
                
                // Mostrar mensaje temporal
                button.innerHTML = '✅';
                button.style.background = 'linear-gradient(135deg, #27ae60, #229954)';
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
            }
        }
    });
    
    document.body.appendChild(button);
}

// Función para reinicio rápido (sin confirmación) - disponible globalmente
window.quickResetStory = function() {
    localStorage.removeItem('cazadorMedianoche_decisions');
    window.location.href = 'seccion-01.html';
};

// Función para mostrar estado actual de decisiones
window.showCurrentProgress = function() {
    const decisions = localStorage.getItem('cazadorMedianoche_decisions');
    if (!decisions) {
        alert('📖 No hay decisiones guardadas.\n\nComienza una nueva historia desde la Sección I.');
        return;
    }
    
    const parsed = JSON.parse(decisions);
    const count = Object.keys(parsed).length;
    let message = `📊 Progreso Actual: ${count}/5 decisiones tomadas\n\n`;
    
    const labels = {
        1: "Confianza inicial",
        2: "Ruta elegida", 
        3: "Estrategia revelación",
        4: "Preparación final",
        5: "Uso de Lágrimas"
    };
    
    for (let i = 1; i <= 5; i++) {
        const decision = parsed[i];
        const label = labels[i];
        const status = decision ? `✓ ${decision.toUpperCase()}` : '⏳ Pendiente';
        message += `${label}: ${status}\n`;
    }
    
    alert(message);
};