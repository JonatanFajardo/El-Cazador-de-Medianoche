/**
 * Timeline System para El Cazador de Medianoche
 * Sistema de línea de tiempo progresiva que muestra ubicaciones conforme se van visitando
 */

class TimelineSystem {
    constructor(decisionSystem) {
        this.decisionSystem = decisionSystem;
        
        // Seguimiento progresivo de ubicaciones visitadas
        this.ubicacionesVisitadas = JSON.parse(localStorage.getItem('el-cazador-ubicaciones')) || [];
        
        this.init();
    }

    init() {
        // Solo construir línea de tiempo si no hay ubicaciones visitadas guardadas
        // Esto permite que el sistema progresivo maneje la línea de tiempo
        if (this.ubicacionesVisitadas.length === 0) {
            this.buildDynamicTimeline();
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
            'encuentro-cabras': { 
                nombre: "🐐 Barba Blanca", 
                dia: "Día 2", 
                distancia: "📏 3 km",
                descripcion: "Conversación con la cabra filosofa"
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
            'zorros-confianza': { 
                nombre: "🦊 Aldea Zorros Plateros", 
                dia: "Día 4", 
                distancia: "📏 12 km",
                descripcion: "Forjas humeantes, flechas de plata"
            },
            'murcielagos-confianza': { 
                nombre: "🦇 Biblioteca Suspendida", 
                dia: "Día 4", 
                distancia: "📏 10 km",
                descripcion: "Cuevas de conocimiento ancestral"
            },
            'zorros-cautela': { 
                nombre: "🦊 Aldea Zorros Plateros", 
                dia: "Día 4", 
                distancia: "📏 12 km",
                descripcion: "Prueba de forja, desconfianza inicial"
            },
            'murcielagos-cautela': { 
                nombre: "🦇 Biblioteca Suspendida", 
                dia: "Día 4", 
                distancia: "📏 10 km",
                descripcion: "Acertijo de los sabios"
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
            'preparacion-final': { 
                nombre: "⚔️ Preparación Final", 
                dia: "Día 7", 
                distancia: "📏 5 km",
                descripcion: "Últimos preparativos antes del Templo"
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
                description: "Refugio solitario de Axel donde comienza la aventura"
              }];

        let timelineHTML = '';
        let totalDistance = 0;
        
        locations.forEach((location, index) => {
            const isCurrent = index === locations.length - 1;
            const currentClass = isCurrent ? 'current' : '';
            
            // Usar propiedades correctas dependiendo del formato
            const nombre = location.nombre || location.name;
            const dia = location.dia || location.day;
            const distancia = location.distancia || location.distance;
            const descripcion = location.descripcion || location.description;
            
            timelineHTML += `
                <div class="timeline-item ${currentClass}" data-day="${dia}">
                    <div class="timeline-marker"></div>
                    <div class="timeline-info">
                        <div class="location-name">${nombre}</div>
                        <div class="day-info">${dia}</div>
                        <div class="distance-info">${distancia}</div>
                        ${descripcion ? `<div class="location-description">${descripcion}</div>` : ''}
                    </div>
                </div>
            `;
            
            // Sumar distancias para estadísticas
            const distanceMatch = distancia.match(/(\d+)/);
            if (distanceMatch) {
                totalDistance += parseInt(distanceMatch[1]);
            }
        });

        // Añadir estadísticas
        timelineHTML += `
            <div class="timeline-stats">
                <p><strong>Lugares Visitados:</strong> ${locations.length}</p>
                <p><strong>Distancia Recorrida:</strong> ~${totalDistance} km</p>
                <p><strong>Días de Viaje:</strong> ${this.getCurrentDay()}</p>
            </div>
        `;

        timelineContainer.innerHTML = timelineHTML;
        console.log('🌙 [Timeline] Línea de tiempo actualizada con', locations.length, 'ubicaciones');
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
        
        Object.keys(mapeo).forEach(seccionId => {
            const elemento = document.getElementById(seccionId);
            if (elemento && !elemento.classList.contains('hidden')) {
                console.log(`✅ Registrando sección visible: ${seccionId} - ${mapeo[seccionId].nombre}`);
                window.timelineSystem.registrarSeccionVisitada(seccionId);
                registradas++;
            }
        });
        
        console.log(`🎯 [Timeline] Total secciones registradas: ${registradas}`);
        
        // Forzar actualización de timeline
        setTimeout(() => {
            window.timelineSystem.buildDynamicTimeline();
        }, 500);
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