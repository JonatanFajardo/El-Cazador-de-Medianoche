/**
 * Timeline System para El Cazador de Medianoche
 * Sistema de línea de tiempo progresiva que muestra ubicaciones conforme se van visitando
 */

class TimelineSystem {
    constructor(decisionSystem) {
        this.decisionSystem = decisionSystem;
        
        // Seguimiento progresivo de ubicaciones visitadas
        this.ubicacionesVisitadas = JSON.parse(localStorage.getItem('el-cazador-ubicaciones')) || [];
        
        // Configuración del Intersection Observer para seguimiento automático
        this.observer = null;
        this.currentSection = null;
        this.observedSections = new Set();
        
        this.init();
    }

    init() {
        // Construir línea de tiempo inicial
        this.buildDynamicTimeline();
        
        // Configurar observador de secciones
        this.setupSectionObserver();
        
        // Registrar sección inicial si está visible
        setTimeout(() => {
            this.detectInitialSection();
        }, 1000);
    }

    // ===================== OBSERVADOR DE SECCIONES =====================
    setupSectionObserver() {
        if (!window.IntersectionObserver) {
            console.warn('⚠️ [Timeline] IntersectionObserver no soportado');
            return;
        }

        const options = {
            root: null,
            rootMargin: '-20% 0px -20% 0px',
            threshold: 0.3
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.id;
                    console.log('👁️ [Timeline] Sección visible:', sectionId);
                    
                    // Registrar como visitada
                    this.registrarSeccionVisitada(sectionId);
                    
                    // Marcar como sección actual
                    this.currentSection = sectionId;
                    this.updateCurrentSectionIndicator();
                }
            });
        }, options);

        // Observar todas las secciones principales
        this.startObserving();
    }

    startObserving() {
        // Obtener todas las secciones mapeadas
        const mapeoSecciones = this.getMapeoSecciones();
        
        Object.keys(mapeoSecciones).forEach(sectionId => {
            const element = document.getElementById(sectionId);
            if (element && !this.observedSections.has(sectionId)) {
                this.observer.observe(element);
                this.observedSections.add(sectionId);
                console.log('🔍 [Timeline] Observando sección:', sectionId);
            }
        });
        
        // Configurar MutationObserver para detectar cuando las secciones se hacen visibles
        this.setupVisibilityObserver();
    }

    setupVisibilityObserver() {
        const visibilityObserver = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const target = mutation.target;
                    if (target.id && this.getMapeoSecciones()[target.id]) {
                        const wasHidden = mutation.oldValue?.includes('hidden');
                        const isHidden = target.classList.contains('hidden');
                        
                        if (wasHidden && !isHidden) {
                            console.log('👁️ [Timeline] Sección se hizo visible:', target.id);
                            // Pequeño delay para asegurar que está completamente visible
                            setTimeout(() => {
                                this.registrarSeccionVisitada(target.id);
                                this.currentSection = target.id;
                                this.updateCurrentSectionIndicator();
                            }, 100);
                        }
                    }
                }
            });
        });

        // Observar cambios en todas las secciones mapeadas
        const mapeoSecciones = this.getMapeoSecciones();
        Object.keys(mapeoSecciones).forEach(sectionId => {
            const element = document.getElementById(sectionId);
            if (element) {
                visibilityObserver.observe(element, {
                    attributes: true,
                    attributeOldValue: true,
                    attributeFilter: ['class']
                });
            }
        });
    }

    detectInitialSection() {
        // Detectar qué sección está visible al cargar
        const mapeoSecciones = this.getMapeoSecciones();
        
        for (const sectionId of Object.keys(mapeoSecciones)) {
            const element = document.getElementById(sectionId);
            if (element && !element.classList.contains('hidden')) {
                const rect = element.getBoundingClientRect();
                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    console.log('🎯 [Timeline] Sección inicial detectada:', sectionId);
                    this.registrarSeccionVisitada(sectionId);
                    this.currentSection = sectionId;
                    break;
                }
            }
        }
        
        // Si no se encontró ninguna sección, registrar "introduccion" por defecto
        if (!this.currentSection) {
            const introduccion = document.getElementById('introduccion');
            if (introduccion && !introduccion.classList.contains('hidden')) {
                console.log('🎯 [Timeline] Registrando introducción por defecto');
                this.registrarSeccionVisitada('introduccion');
                this.currentSection = 'introduccion';
            }
        }
    }

    // ===================== INTEGRACIÓN CON SISTEMA DE DECISIONES =====================
    conectarConDecisionSystem(decisionSystem) {
        this.decisionSystem = decisionSystem;
        
        // Hook para cuando se muestran nuevas secciones
        const originalMostrarElemento = decisionSystem.mostrarElemento;
        if (originalMostrarElemento) {
            decisionSystem.mostrarElemento = (elementId) => {
                const resultado = originalMostrarElemento.call(decisionSystem, elementId);
                
                // Si es una sección mapeada, registrarla
                setTimeout(() => {
                    const mapeoSecciones = this.getMapeoSecciones();
                    if (mapeoSecciones[elementId]) {
                        console.log('📋 [Timeline] Decisión mostró sección:', elementId);
                        this.registrarSeccionVisitada(elementId);
                        this.currentSection = elementId;
                        this.updateCurrentSectionIndicator();
                    }
                }, 100);
                
                return resultado;
            };
        }
    }

    // ===================== MAPEO DE SECCIONES A UBICACIONES =====================
    getMapeoSecciones() {
        return {
            'introduccion': { 
                nombre: "🏔️ Montañas Heladas", 
                dia: "Día 1", 
                distancia: "📍 Inicio",
                descripcion: "Refugio solitario de Axel, encuentro inicial con Seraphina"
            },
            'encuentro-confianza': { 
                nombre: "🤝 Primer Encuentro - Confianza", 
                dia: "Día 1", 
                distancia: "📏 0 km",
                descripcion: "Axel decide confiar y ayudar inmediatamente"
            },
            'encuentro-cautela': { 
                nombre: "🛡️ Primer Encuentro - Cautela", 
                dia: "Día 1", 
                distancia: "📏 0 km",
                descripcion: "Axel ayuda pero manteniéndose alerta"
            },
            'desarrollo-inicial': { 
                nombre: "🌫️ Valle de los Susurradores", 
                dia: "Día 2", 
                distancia: "📏 15 km",
                descripcion: "Seraphina cuenta su historia sobre las Lágrimas de Luna"
            },
            'viaje-valle': { 
                nombre: "🥾 Descenso de Montañas", 
                dia: "Día 2", 
                distancia: "📏 8 km",
                descripcion: "Sendero peligroso hacia el valle"
            },
            'encuentro-mapaches': { 
                nombre: "🦝 Paso de Piedras Resbaladizas", 
                dia: "Día 2", 
                distancia: "📏 2 km",
                descripcion: "Encuentro con los Mapaches Peajeros"
            },
            'resolucion-mapaches-confianza': { 
                nombre: "🤝 Resolución con Mapaches - Confianza", 
                dia: "Día 2", 
                distancia: "📏 1 km",
                descripcion: "Axel comparte información con confianza"
            },
            'resolucion-mapaches-cautela': { 
                nombre: "🛡️ Resolución con Mapaches - Cautela", 
                dia: "Día 2", 
                distancia: "📏 1 km",
                descripcion: "Axel mantiene prudencia en el intercambio"
            },
            'encuentro-cabras': { 
                nombre: "🐐 Barba Blanca", 
                dia: "Día 2", 
                distancia: "📏 3 km",
                descripcion: "Conversación con la cabra filósofa"
            },
            'encuentro-avalancha': { 
                nombre: "⛰️ Zona de Avalanchas", 
                dia: "Día 3", 
                distancia: "📏 5 km",
                descripcion: "Rescate por los Conejos Guardianes"
            },
            'refugio-conejos': { 
                nombre: "🐰 Refugio de Conejos Salvavidas", 
                dia: "Día 3", 
                distancia: "📏 1 km",
                descripcion: "Recuperación y descanso con los conejos rescatistas"
            },
            'viaje-aliados': { 
                nombre: "🛤️ Sendero hacia los Aliados", 
                dia: "Día 4", 
                distancia: "📏 8 km",
                descripcion: "Camino hacia las tribus aliadas elegidas"
            },
            'ruta-zorros': { 
                nombre: "🛤️ Ruta hacia los Zorros Plateros", 
                dia: "Día 4", 
                distancia: "📏 5 km",
                descripcion: "Sendero hacia las forjas de los zorros"
            },
            'ruta-murcielagos': { 
                nombre: "🛤️ Ruta hacia los Murciélagos Bibliotecarios", 
                dia: "Día 4", 
                distancia: "📏 5 km",
                descripcion: "Sendero hacia las cuevas biblioteca"
            },
            'zorros-confianza': { 
                nombre: "🦊 Aldea Zorros Plateros - Confianza", 
                dia: "Día 4", 
                distancia: "📏 12 km",
                descripcion: "Forjas humeantes, flechas de plata con confianza mutua"
            },
            'zorros-cautela': { 
                nombre: "🦊 Aldea Zorros Plateros - Cautela", 
                dia: "Día 4", 
                distancia: "📏 12 km",
                descripcion: "Prueba de forja, desconfianza inicial superada"
            },
            'murcielagos-confianza': { 
                nombre: "🦇 Biblioteca Suspendida - Confianza", 
                dia: "Día 4", 
                distancia: "📏 10 km",
                descripcion: "Cuevas de conocimiento ancestral con acceso pleno"
            },
            'murcielagos-cautela': { 
                nombre: "🦇 Biblioteca Suspendida - Cautela", 
                dia: "Día 4", 
                distancia: "📏 10 km",
                descripcion: "Acertijo de los sabios, conocimiento ganado con esfuerzo"
            },
            'flechas-plata': { 
                nombre: "⚡ Flechas de Plata", 
                dia: "Día 4", 
                distancia: "📏 0 km",
                descripcion: "Recibiendo flechas mágicas de los Zorros Plateros"
            },
            'flechas-antiengano': { 
                nombre: "🧠 Flechas Anti-Engaño", 
                dia: "Día 4", 
                distancia: "📏 0 km",
                descripcion: "Recibiendo flechas de verdad de los Murciélagos"
            },
            'camino-cuervos': { 
                nombre: "🛣️ Camino al Bosque de Cuervos", 
                dia: "Día 5", 
                distancia: "📏 15 km",
                descripcion: "Sendero hacia el territorio de los cuervos espejo"
            },
            'melodia-ember': { 
                nombre: "🎵 Eco de la Flauta", 
                dia: "Día 5", 
                distancia: "📏 0 km",
                descripcion: "Melodía familiar en las montañas"
            },
            'encuentro-hermanos': { 
                nombre: "👥 Reencuentro Fraternal", 
                dia: "Día 5", 
                distancia: "📏 1 km",
                descripcion: "Axel y Ember se reúnen después de años"
            },
            'dialogo-ember': { 
                nombre: "💬 Conversación Fraternal", 
                dia: "Día 5", 
                distancia: "📏 0 km",
                descripcion: "Diálogos reveladores entre los hermanos"
            },
            'continuar-solo': { 
                nombre: "🚶‍♂️ Axel Continúa Solo", 
                dia: "Día 5", 
                distancia: "📏 0 km",
                descripcion: "Decidió continuar la aventura sin Ember"
            },
            'llegada-cuervos': { 
                nombre: "🐦‍⬛ Bosque de Cuervos Espejo", 
                dia: "Día 6", 
                distancia: "📏 18 km",
                descripcion: "Los cuervos muestran verdades ocultas"
            },
            'revelacion-lyra': { 
                nombre: "⚡ Revelación de Lyra", 
                dia: "Día 6", 
                distancia: "📏 0 km",
                descripcion: "La verdad sobre Seraphina se revela"
            },
            'confrontacion-directa': { 
                nombre: "⚔️ Confrontación Directa", 
                dia: "Día 6", 
                distancia: "📏 0 km",
                descripcion: "Enfrentamiento inmediato con Seraphina"
            },
            'estrategia-espionaje': { 
                nombre: "🕵️ Estrategia de Espionaje", 
                dia: "Día 6", 
                distancia: "📏 0 km",
                descripcion: "Infiltración y observación encubierta"
            },
            'post-revelacion': { 
                nombre: "💭 Reflexión Post-Revelación", 
                dia: "Día 6", 
                distancia: "📏 2 km",
                descripcion: "Procesando la impactante verdad sobre Seraphina"
            },
            'ember-se-va': { 
                nombre: "👋 Ember Regresa a Casa", 
                dia: "Día 7", 
                distancia: "📏 0 km",
                descripcion: "Ember decide proteger a su familia"
            },
            'ember-se-queda': { 
                nombre: "🤝 Ember Se Queda", 
                dia: "Día 7", 
                distancia: "📏 0 km",
                descripcion: "Los hermanos continúan juntos la misión"
            },
            'despedida-ember': { 
                nombre: "😢 Despedida Fraternal", 
                dia: "Día 7", 
                distancia: "📏 0 km",
                descripcion: "Momento emotivo de separación"
            },
            'ember-continua': { 
                nombre: "➡️ Ember Continúa la Aventura", 
                dia: "Día 7", 
                distancia: "📏 0 km",
                descripcion: "Los hermanos siguen unidos en la misión"
            },
            'viaje-post-revelacion': { 
                nombre: "🚶‍♂️ Nueva Estrategia en Marcha", 
                dia: "Día 7", 
                distancia: "📏 10 km",
                descripcion: "Avanzando con la nueva información adquirida"
            },
            'camino-cuervos': { 
                nombre: "🛣️ Camino al Bosque de Cuervos", 
                dia: "Día 5", 
                distancia: "📏 15 km",
                descripcion: "Sendero hacia el territorio de los cuervos espejo"
            },
            'post-revelacion': { 
                nombre: "💭 Reflexión Post-Revelación", 
                dia: "Día 6", 
                distancia: "📏 2 km",
                descripcion: "Procesando la impactante verdad sobre Seraphina"
            },
            'viaje-post-revelacion': { 
                nombre: "🚶‍♂️ Nueva Estrategia en Marcha", 
                dia: "Día 7", 
                distancia: "📏 10 km",
                descripcion: "Avanzando con la nueva información adquirida"
            },
            'viaje-aliados-finales': { 
                nombre: "🧭 Búsqueda de Aliados Finales", 
                dia: "Día 8", 
                distancia: "📏 12 km",
                descripcion: "Último esfuerzo por reunir apoyo antes del templo"
            },
            'entrada-templo': { 
                nombre: "🏛️ Templo Celestial", 
                dia: "Día 9", 
                distancia: "📏 20 km",
                descripcion: "Santuario final de las Lágrimas de Luna"
            },
            'viaje-laberinto': { 
                nombre: "🌀 Hacia el Laberinto Final", 
                dia: "Día 10", 
                distancia: "📏 8 km",
                descripcion: "Aproximación al desafío final"
            },
            'resolucion-final': { 
                nombre: "✨ Resolución en el Templo", 
                dia: "Día 10", 
                distancia: "📏 0 km",
                descripcion: "El momento decisivo con las Lágrimas de Luna"
            }
        };
    }

    // ===================== REGISTRO DE SECCIONES VISITADAS =====================
    registrarSeccionVisitada(seccionId) {
        const mapeoSecciones = this.getMapeoSecciones();
        
        // Debug: log para ver si la sección tiene mapeo
        console.log('🔍 [Timeline] Registrando sección:', seccionId);
        console.log('🗺️ [Timeline] Mapeo existe:', !!mapeoSecciones[seccionId]);
        console.log('📋 [Timeline] Ya registrada:', !!this.ubicacionesVisitadas.find(u => u.seccionId === seccionId));
        
        // Solo agregar si la sección tiene mapeo y no está ya registrada
        if (mapeoSecciones[seccionId] && !this.ubicacionesVisitadas.find(u => u.seccionId === seccionId)) {
            const ubicacion = { ...mapeoSecciones[seccionId], seccionId: seccionId };
            this.ubicacionesVisitadas.push(ubicacion);
            
            console.log('✅ [Timeline] Ubicación agregada:', ubicacion.nombre);
            console.log('📊 [Timeline] Total ubicaciones:', this.ubicacionesVisitadas.length);
            
            // Guardar en localStorage
            localStorage.setItem('el-cazador-ubicaciones', JSON.stringify(this.ubicacionesVisitadas));
            
            // Actualizar línea de tiempo inmediatamente
            setTimeout(() => {
                console.log('🔄 [Timeline] Actualizando línea de tiempo...');
                this.buildDynamicTimeline();
            }, 300);
        }
    }

    // ===================== CONSTRUCCIÓN DE LÍNEA DE TIEMPO =====================
    buildDynamicTimeline() {
        const timelineContainer = document.getElementById('dynamic-timeline');
        if (!timelineContainer) {
            console.warn('⚠️ [Timeline] Contenedor dynamic-timeline no encontrado');
            return;
        }

        // Usar ubicaciones visitadas progresivamente en lugar de generar todo
        const locations = this.ubicacionesVisitadas.length > 0 
            ? this.ubicacionesVisitadas 
            : [{
                name: "🏔️ Montañas Heladas",
                day: "Día 1", 
                distance: "📍 Inicio",
                description: "Refugio solitario de Axel donde comienza la aventura",
                seccionId: "introduccion"
              }];

        let timelineHTML = '';
        let totalDistance = 0;
        
        locations.forEach((location, index) => {
            const isCurrent = this.currentSection === location.seccionId;
            const isVisited = index < locations.length - 1 || (index === locations.length - 1 && !isCurrent);
            
            let itemClass = '';
            if (isCurrent) {
                itemClass = 'current';
            } else if (isVisited) {
                itemClass = 'visited';
            }
            
            // Usar propiedades correctas dependiendo del formato
            const nombre = location.nombre || location.name;
            const dia = location.dia || location.day;
            const distancia = location.distancia || location.distance;
            const descripcion = location.descripcion || location.description;
            
            timelineHTML += `
                <div class="timeline-item ${itemClass}" data-day="${dia}" data-section="${location.seccionId}">
                    <div class="timeline-marker">
                        ${isCurrent ? '<span class="current-indicator">📍</span>' : ''}
                        ${isVisited ? '<span class="visited-indicator">✓</span>' : ''}
                    </div>
                    <div class="timeline-info">
                        <div class="location-name">${nombre}</div>
                        <div class="day-info">${dia}</div>
                        <div class="distance-info">${distancia}</div>
                        ${descripcion ? `<div class="location-description">${descripcion}</div>` : ''}
                        ${isCurrent ? '<div class="reading-status">📖 Leyendo actualmente...</div>' : ''}
                    </div>
                </div>
            `;
            
            // Sumar distancias para estadísticas
            const distanceMatch = distancia.match(/(\d+)/);
            if (distanceMatch) {
                totalDistance += parseInt(distanceMatch[1]);
            }
        });

        // Añadir estadísticas mejoradas
        const progressPercentage = this.calculateReadingProgress();
        timelineHTML += `
            <div class="timeline-stats">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progressPercentage}%"></div>
                    <span class="progress-text">Progreso: ${progressPercentage.toFixed(1)}%</span>
                </div>
                <p><strong>Lugares Visitados:</strong> ${locations.length}</p>
                <p><strong>Distancia Recorrida:</strong> ~${totalDistance} km</p>
                <p><strong>Días de Viaje:</strong> ${this.getCurrentDay()}</p>
                <p><strong>Sección Actual:</strong> ${this.getCurrentSectionName()}</p>
            </div>
        `;

        timelineContainer.innerHTML = timelineHTML;
        console.log('🌙 [Timeline] Línea de tiempo actualizada con', locations.length, 'ubicaciones');
    }

    // ===================== INDICADORES DE PROGRESO =====================
    updateCurrentSectionIndicator() {
        // Remover marcadores actuales previos
        document.querySelectorAll('.timeline-item.current').forEach(item => {
            item.classList.remove('current');
        });
        
        // Marcar nuevo elemento actual
        const currentItem = document.querySelector(`[data-section="${this.currentSection}"]`);
        if (currentItem) {
            currentItem.classList.add('current');
        }
        
        // Actualizar estadísticas
        this.updateTimelineStats();
    }

    updateTimelineStats() {
        const statsContainer = document.querySelector('.timeline-stats');
        if (statsContainer) {
            const progressPercentage = this.calculateReadingProgress();
            const progressBar = statsContainer.querySelector('.progress-fill');
            const progressText = statsContainer.querySelector('.progress-text');
            const currentSection = statsContainer.querySelector('p:last-child strong');
            
            if (progressBar) {
                progressBar.style.width = `${progressPercentage}%`;
            }
            if (progressText) {
                progressText.textContent = `Progreso: ${progressPercentage.toFixed(1)}%`;
            }
            if (currentSection && currentSection.parentNode) {
                currentSection.parentNode.innerHTML = `<strong>Sección Actual:</strong> ${this.getCurrentSectionName()}`;
            }
        }
    }

    calculateReadingProgress() {
        const mapeoCompleto = this.getMapeoSecciones();
        const totalSections = Object.keys(mapeoCompleto).length;
        const visitedSections = this.ubicacionesVisitadas.length;
        
        return totalSections > 0 ? (visitedSections / totalSections) * 100 : 0;
    }

    getCurrentSectionName() {
        if (!this.currentSection) return 'Sin determinar';
        
        const mapeoSecciones = this.getMapeoSecciones();
        const seccionInfo = mapeoSecciones[this.currentSection];
        
        return seccionInfo ? seccionInfo.nombre : 'Sección desconocida';
    }

    // ===================== UTILIDADES =====================
    getCurrentDay() {
        if (this.ubicacionesVisitadas.length === 0) return 1;
        
        // Obtener el día más alto de las ubicaciones visitadas
        const days = this.ubicacionesVisitadas.map(loc => {
            const dayMatch = (loc.dia || loc.day || 'Día 1').match(/(\d+)/);
            return dayMatch ? parseInt(dayMatch[1]) : 1;
        });
        
        return Math.max(...days);
    }

    updateTimelineProgress() {
        // Reconstruir toda la línea de tiempo
        this.buildDynamicTimeline();
    }

    // ===================== LIMPIEZA Y REINICIO =====================
    limpiarTimeline() {
        this.ubicacionesVisitadas = [];
        localStorage.removeItem('el-cazador-ubicaciones');
        this.buildDynamicTimeline();
        console.log('🧹 [Timeline] Timeline limpiada y reiniciada');
    }

    // ===================== CARGA DE ESTADO =====================
    cargarUbicacionesGuardadas() {
        setTimeout(() => {
            if (this.ubicacionesVisitadas.length > 0) {
                console.log('📍 [Timeline] Cargando timeline con ubicaciones guardadas:', this.ubicacionesVisitadas.length);
                this.buildDynamicTimeline();
            }
        }, 500);
    }
}

// ===================== FUNCIONES GLOBALES =====================
function toggleTimelinePanel() {
    const panel = document.getElementById('timeline-panel');
    const toggle = document.getElementById('timeline-toggle');
    
    if (panel.style.display === 'none') {
        panel.style.display = 'block';
        toggle.textContent = '📍';
    } else {
        panel.style.display = 'none';
        toggle.textContent = '🕒';
    }
}

// Función para mostrar debug de timeline
function mostrarTimelineDebug() {
    if (window.timelineSystem) {
        console.log('🌙 [Timeline Debug]');
        console.log('📍 Ubicaciones visitadas:', window.timelineSystem.ubicacionesVisitadas);
        console.log('📊 Total:', window.timelineSystem.ubicacionesVisitadas.length);
        console.log('🗓️ Día actual:', window.timelineSystem.getCurrentDay());
        
        // Mostrar detalles de cada ubicación
        window.timelineSystem.ubicacionesVisitadas.forEach((ubicacion, index) => {
            console.log(`${index + 1}. ${ubicacion.nombre} (${ubicacion.dia}) - ${ubicacion.descripcion}`);
        });
        
        // Mostrar mapeo completo disponible
        console.log('🗺️ [Mapeo disponible]:');
        const mapeo = window.timelineSystem.getMapeoSecciones();
        Object.keys(mapeo).forEach(key => {
            console.log(`- ${key}: ${mapeo[key].nombre}`);
        });
    }
}

// Función para forzar registro de todas las secciones visibles
function forzarRegistroSecciones() {
    if (window.timelineSystem) {
        console.log('🔧 [Timeline] Forzando registro de secciones visibles...');
        const mapeo = window.timelineSystem.getMapeoSecciones();
        let registradas = 0;
        let seccionActual = null;
        
        Object.keys(mapeo).forEach(seccionId => {
            const elemento = document.getElementById(seccionId);
            if (elemento && !elemento.classList.contains('hidden')) {
                console.log(`✅ Registrando sección visible: ${seccionId} - ${mapeo[seccionId].nombre}`);
                window.timelineSystem.registrarSeccionVisitada(seccionId);
                registradas++;
                
                // Verificar si está en el viewport para marcarlo como actual
                const rect = elemento.getBoundingClientRect();
                if (rect.top < window.innerHeight * 0.8 && rect.bottom > window.innerHeight * 0.2) {
                    seccionActual = seccionId;
                }
            }
        });
        
        // Establecer la sección actual si se detectó una
        if (seccionActual) {
            window.timelineSystem.currentSection = seccionActual;
            console.log(`🎯 [Timeline] Sección actual establecida: ${seccionActual}`);
        }
        
        console.log(`🎯 [Timeline] Total secciones registradas: ${registradas}`);
        
        // Forzar actualización de timeline
        setTimeout(() => {
            window.timelineSystem.buildDynamicTimeline();
        }, 500);
    }
}

// Nueva función para registrar una sección específica manualmente
function registrarSeccionActual(seccionId) {
    if (window.timelineSystem && seccionId) {
        console.log(`🔍 [Timeline] Registro manual de sección: ${seccionId}`);
        window.timelineSystem.registrarSeccionVisitada(seccionId);
        window.timelineSystem.currentSection = seccionId;
        window.timelineSystem.updateCurrentSectionIndicator();
    }
}

// Función para limpiar y reiniciar timeline
function reiniciarTimeline() {
    if (window.timelineSystem) {
        console.log('🧹 [Timeline] Reiniciando timeline...');
        window.timelineSystem.limpiarTimeline();
        // Esperar un poco y luego registrar secciones visibles
        setTimeout(() => {
            forzarRegistroSecciones();
        }, 1000);
    }
}

// Exportar para uso global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimelineSystem;
}