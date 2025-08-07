// Script para marcar automáticamente el contenido nuevo agregado
// Este script identifica y marca elementos que son parte del contenido nuevo

document.addEventListener('DOMContentLoaded', function() {
    
    // Lista de IDs de elementos que son contenido nuevo
    const newContentIds = [
        // Viajes
        'viaje-valle',
        'viaje-aliados', 
        'viaje-post-revelacion',
        'viaje-aliados-finales',
        'viaje-laberinto',
        
        // Encuentros
        'encuentro-mapaches',
        'encuentro-cabras',
        'encuentro-avalancha',
        'refugio-conejos',
        
        // Resoluciones
        'resolucion-mapaches-confianza',
        'resolucion-mapaches-cautela',
        'respuesta-axel-confianza',
        'respuesta-axel-cautela',
        'respuesta-seraphina',
        
        // Rutas específicas
        'ruta-zorros',
        'ruta-murcielagos',
        'ruta-arañas',
        'ruta-conejos-herbolarios'
    ];
    
    // Marcar elementos por ID
    newContentIds.forEach(id => {
        const element = document.getElementById(id);
        if (element && !element.classList.contains('new-content')) {
            element.classList.add('new-content');
        }
    });
    
    // Marcar todos los elementos dentro de secciones marcadas como nuevas
    const newSections = document.querySelectorAll('section.new-content');
    newSections.forEach(section => {
        const innerElements = section.querySelectorAll('p, h3, h4, h5, .dialogo, .texto-narrativo, .mini-decision, .encuentro-menor, div');
        innerElements.forEach(el => {
            if (!el.classList.contains('new-content')) {
                el.classList.add('new-content');
            }
        });
    });
    
    // Marcar elementos por patrones de texto que indican contenido nuevo
    const newContentPatterns = [
        /Rigoberto Rinconada/i,
        /Ruperto y Reinaldo/i,
        /Filosofa Barbaespuma/i,
        /Saltarina Valiente/i,
        /Ferromax el Fuerte/i,
        /Madam Seda Antigua/i,
        /Pupila Lunabrillante/i,
        /Túnel Ojosnublados/i,
        /Alpha Cicatriz-de-Luna/i,
        /Resplandor Ancestral/i,
        /Corona de Flores/i,
        /Nuez Brillanteojos/i,
        /Garra Plateada/i,
        /Mapaches Mercantes/i,
        /Puente de las Reflexiones/i,
        /Cuevas de Cobre Brillante/i,
        /Bosque de los Susurros Antiguos/i,
        /Arañas Tejedoras del Destino/i,
        /Conejos Herbolarios/i
    ];
    
    // Buscar párrafos que contengan estos patrones y marcarlos
    const allParagraphs = document.querySelectorAll('p, .dialogo');
    allParagraphs.forEach(p => {
        const text = p.textContent;
        if (newContentPatterns.some(pattern => pattern.test(text))) {
            if (!p.classList.contains('new-content')) {
                p.classList.add('new-content');
                // También marcar el contenedor padre si es apropiado
                if (p.closest('section') && !p.closest('section').classList.contains('new-content')) {
                    p.closest('section').classList.add('new-content');
                }
            }
        }
    });
    
    console.log('Contenido nuevo marcado automáticamente');
});