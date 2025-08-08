/**
 * Sistema de Decisiones Dinámico para "El Cazador de Medianoche"
 * Maneja todas las decisiones interactivas y contenido condicional
 */

class DecisionSystem {
    constructor() {
        // Intentar recuperar de localStorage primero, luego sessionStorage como respaldo
        this.decisiones = JSON.parse(localStorage.getItem('el-cazador-decisiones')) || 
                         JSON.parse(sessionStorage.getItem('el-cazador-decisiones')) || [];
        this.currentChapter = parseInt(localStorage.getItem('el-cazador-chapter')) || 1;
        
        // Si se recuperó de sessionStorage, guardarlo en localStorage
        if (this.decisiones.length > 0 && !localStorage.getItem('el-cazador-decisiones')) {
            localStorage.setItem('el-cazador-decisiones', JSON.stringify(this.decisiones));
        }
        
        this.init();
    }

    init() {
        this.restaurarEstado();
        this.mostrarContenidoSegunDecisiones();
        this.crearInterfazProgreso();
        this.setupEventListeners();
        
        // Inicializar sistema de timeline
        this.timelineSystem = new TimelineSystem(this);
    }

    // ===================== RESTAURAR ESTADO AL RECARGAR =====================
    restaurarEstado() {
        const decisiones = this.decisiones;
        console.log('Restaurando estado con decisiones:', decisiones);
        
        if (decisiones.length === 0) {
            // No hay decisiones guardadas, mostrar estado inicial
            return;
        }

        // Ocultar todas las decisiones tomadas y mostrar contenido relevante
        for (let i = 0; i < decisiones.length; i++) {
            const numeroDecision = i + 1;
            this.ocultarElemento(`decision-${numeroDecision}`);
        }

        // Mostrar secciones que deberían estar visibles según el progreso
        this.mostrarSeccionesSegunProgreso();
        
        // Mostrar la siguiente decisión pendiente si existe
        const siguienteDecision = decisiones.length + 1;
        if (siguienteDecision <= 7) {
            this.mostrarSiguienteDecision(decisiones.length);
        } else {
            // Historia completa - solo mostrar historia completa, no las opciones automáticamente
            this.mostrarElemento('historia-completa');
        }
    }

    mostrarSeccionesSegunProgreso() {
        const numDecisiones = this.decisiones.length;
        
        console.log('🔄 Restaurando estado, no registrando ubicaciones en línea de tiempo');
        
        // Siempre mostrar introducción (sin registrar para evitar spam en timeline)
        this.mostrarElemento('introduccion', true);
        
        if (numDecisiones >= 1) {
            this.mostrarElemento('desarrollo-inicial', true);
            this.mostrarElemento('viaje-valle', true);
            this.mostrarElemento('encuentro-mapaches', true);
            this.mostrarElemento('encuentro-cabras', true);
            this.mostrarElemento('encuentro-avalancha', true);
            this.mostrarElemento('refugio-conejos', true);
        }
        
        if (numDecisiones >= 2) {
            this.mostrarElemento('viaje-aliados', true);
            this.mostrarElemento('camino-cuervos', true);
        }
        
        if (numDecisiones >= 3) {
            this.mostrarElemento('llegada-cuervos', true);
            this.mostrarElemento('revelacion-lyra', true);
        }
        
        if (numDecisiones >= 4) {
            this.mostrarElemento('post-revelacion', true);
            this.mostrarElemento('viaje-post-revelacion', true);
        }
        
        if (numDecisiones >= 5) {
            this.mostrarElemento('preparacion-final', true);
        }
        
        if (numDecisiones >= 6) {
            this.mostrarElemento('viaje-aliados-finales', true);
            this.mostrarElemento('entrada-templo', true);
        }
        
        if (numDecisiones >= 7) {
            this.mostrarElemento('viaje-laberinto', true);
            this.mostrarElemento('resolucion-final', true);
            setTimeout(() => {
                this.mostrarElemento('historia-completa', true);
                // Solo mostrar opciones si la historia se completó normalmente, no al recargar
                if (this.decisiones.length === 7) {
                    setTimeout(() => this.mostrarElemento('opciones-finales', true), 2000);
                }
            }, 1000);
        }
        
        // Después de restaurar, cargar las ubicaciones guardadas para la timeline
        setTimeout(() => {
            if (this.timelineSystem) {
                this.timelineSystem.cargarUbicacionesGuardadas();
            }
        }, 500);
    }

    mostrarSiguienteDecision(numDecisionesTomadas) {
        const siguienteDecision = numDecisionesTomadas + 1;
        
        setTimeout(() => {
            switch(siguienteDecision) {
                case 1:
                    // Primera decisión siempre visible
                    break;
                case 2:
                    this.mostrarElemento('decision-2');
                    break;
                case 3:
                    this.mostrarElemento('decision-3');
                    break;
                case 4:
                    this.mostrarElemento('decision-4');
                    break;
                case 5:
                    // Mostrar la decisión 5 completa
                    this.mostrarElemento('decision-5');
                    // Decidir qué contenido específico mostrar dentro de la decisión
                    const tieneEmber = this.decisiones[2] === 'A';
                    if (tieneEmber) {
                        this.mostrarElemento('ember-presente-decision');
                        this.ocultarElemento('ember-ausente-decision');
                    } else {
                        this.mostrarElemento('ember-ausente-decision');
                        this.ocultarElemento('ember-presente-decision');
                    }
                    break;
                case 6:
                    this.mostrarElemento('decision-6');
                    break;
                case 7:
                    this.mostrarElemento('decision-7');
                    break;
            }
        }, 500);
    }

    // ===================== TOMAR DECISIONES =====================
    tomarDecision(numeroDecision, opcion) {
        // Guardar decisión
        this.decisiones[numeroDecision - 1] = opcion;
        localStorage.setItem('el-cazador-decisiones', JSON.stringify(this.decisiones));
        
        // Ocultar botones de decisión actual
        this.ocultarElemento(`decision-${numeroDecision}`);
        
        // Mostrar contenido según nueva decisión
        this.mostrarContenidoSegunDecisiones();
        
        // Revelar siguiente sección con efecto
        this.revelarSiguienteSeccion(numeroDecision);
        
        // Actualizar progreso
        this.actualizarProgreso();
        
        // Guardar progreso completo inmediatamente
        this.guardarProgreso();
        this.mostrarIndicadorAutoSave();
        
        // Guardar también en sessionStorage como respaldo
        sessionStorage.setItem('el-cazador-decisiones', JSON.stringify(this.decisiones));
        
        // Log para debug
        console.log(`Decisión ${numeroDecision}: ${opcion}. Ruta actual: ${this.getRutaCompleta()}`);
    }

    // ===================== MOSTRAR CONTENIDO CONDICIONAL =====================
    mostrarContenidoSegunDecisiones() {
        const ruta = this.getRutaCompleta();
        
        // Decisión 1: Confianza vs Cautela
        this.evaluarDecision1();
        
        // Decisión 2: Zorros vs Murciélagos  
        this.evaluarDecision2();
        
        // Decisión 3: Con Ember vs Sin Ember
        this.evaluarDecision3();
        
        // Decisión 4: Confrontación vs Espionaje
        this.evaluarDecision4();
        
        // Decisión 5: Ember se queda vs se va
        this.evaluarDecision5();
        
        // Decisión 6: Arañas vs Conejos
        this.evaluarDecision6();
        
        // Decisión 7: Redención vs Confrontación final
        this.evaluarDecision7();
        
        // Combinaciones complejas
        this.evaluarCombinaciones(ruta);
    }

    evaluarDecision1() {
        if (this.decisiones[0] === 'A') {
            // Mostrar contenido de confianza
            this.mostrarElemento('encuentro-confianza');
            this.ocultarElemento('encuentro-cautela');
        } else if (this.decisiones[0] === 'B') {
            // Mostrar contenido de cautela
            this.mostrarElemento('encuentro-cautela');
            this.ocultarElemento('encuentro-confianza');
        }
        
        // Mostrar desarrollo inicial siempre después de la decisión 1
        if (this.decisiones[0]) {
            this.mostrarElemento('desarrollo-inicial');
            this.mostrarElemento('viaje-valle');
            this.mostrarElemento('encuentro-mapaches');
            
            // Mostrar la resolución correcta de mapaches según la decisión
            if (this.decisiones[0] === 'A') {
                this.mostrarElemento('resolucion-mapaches-confianza');
                this.ocultarElemento('resolucion-mapaches-cautela');
            } else {
                this.mostrarElemento('resolucion-mapaches-cautela');
                this.ocultarElemento('resolucion-mapaches-confianza');
            }
            
            // Continuar con los encuentros menores
            this.mostrarElemento('encuentro-cabras');
            this.mostrarElemento('encuentro-avalancha');
            this.mostrarElemento('refugio-conejos');
        }
    }

    evaluarDecision2() {
        const d1 = this.decisiones[0];
        const d2 = this.decisiones[1];
        
        if (d1 && d2) {
            if (d1 === 'A' && d2 === 'A') {
                this.mostrarElemento('zorros-confianza');
                this.mostrarElemento('ruta-zorros');
                this.ocultarElemento('ruta-murcielagos');
            } else if (d1 === 'A' && d2 === 'B') {
                this.mostrarElemento('murcielagos-confianza');
                this.mostrarElemento('ruta-murcielagos');
                this.ocultarElemento('ruta-zorros');
            } else if (d1 === 'B' && d2 === 'A') {
                this.mostrarElemento('zorros-cautela');
                this.mostrarElemento('ruta-zorros');
                this.ocultarElemento('ruta-murcielagos');
            } else if (d1 === 'B' && d2 === 'B') {
                this.mostrarElemento('murcielagos-cautela');
                this.mostrarElemento('ruta-murcielagos');
                this.ocultarElemento('ruta-zorros');
            }
        }
    }

    evaluarDecision3() {
        if (this.decisiones[2] === 'A') {
            this.mostrarElemento('melodia-ember');
            this.mostrarElemento('encuentro-hermanos');
            this.mostrarElemento('dialogo-ember');
        } else if (this.decisiones[2] === 'B') {
            this.mostrarElemento('continuar-solo');
            this.ocultarElemento('encuentro-hermanos');
        }
    }

    evaluarDecision4() {
        if (this.decisiones[3] === 'A') {
            this.mostrarElemento('confrontacion-directa');
            this.ocultarElemento('estrategia-espionaje');
        } else if (this.decisiones[3] === 'B') {
            this.mostrarElemento('estrategia-espionaje');
            this.ocultarElemento('confrontacion-directa');
        }
    }

    evaluarDecision5() {
        const tieneEmber = this.decisiones[2] === 'A';
        
        if (tieneEmber) {
            // Con Ember presente - dilema familiar
            this.mostrarElemento('ember-presente-decision');
            this.ocultarElemento('ember-ausente-decision');
            
            if (this.decisiones[4] === 'A') {
                this.mostrarElemento('ember-se-va');
                this.mostrarElemento('despedida-ember');
            } else if (this.decisiones[4] === 'B') {
                this.mostrarElemento('ember-se-queda');
                this.mostrarElemento('ember-continua');
            }
        } else {
            // Sin Ember - decisión sobre aliados/templo
            this.mostrarElemento('ember-ausente-decision');
            this.ocultarElemento('ember-presente-decision');
            
            if (this.decisiones[4] === 'A') {
                this.mostrarElemento('buscar-aliados-extra');
            } else if (this.decisiones[4] === 'B') {
                this.mostrarElemento('directo-al-templo');
            }
        }
    }

    evaluarDecision6() {
        if (this.decisiones[5] === 'A') {
            this.mostrarElemento('encuentro-arañas');
            this.mostrarElemento('mapas-detallados');
            this.mostrarElemento('ruta-arañas');
            this.ocultarElemento('ruta-conejos-herbolarios');
        } else if (this.decisiones[5] === 'B') {
            this.mostrarElemento('encuentro-conejos');
            this.mostrarElemento('hierbas-proteccion');
            this.mostrarElemento('ruta-conejos-herbolarios');
            this.ocultarElemento('ruta-arañas');
        }
    }

    evaluarDecision7() {
        if (this.decisiones[6] === 'A') {
            this.mostrarElemento('final-redencion');
            this.mostrarElemento('epilogo-compasivo');
        } else if (this.decisiones[6] === 'B') {
            this.mostrarElemento('final-confrontacion');
            this.mostrarElemento('epilogo-justicia');
        }
    }

    evaluarCombinaciones(ruta) {
        // Combinaciones específicas importantes
        
        // El Redentor Perfecto - AAAAAAA
        if (ruta === 'AAAAAAA') {
            this.mostrarElemento('final-heroe-perfecto');
        }
        
        // El Estratega Solitario - BABBABB
        if (ruta === 'BABBABB') {
            this.mostrarElemento('final-estratega-solitario');
        }
        
        // El Diplomático Familiar - AABBBAA
        if (ruta === 'AABBBAA') {
            this.mostrarElemento('final-diplomatico-familiar');
        }
        
        // Ember presente en final
        const emberPresente = this.decisiones[2] === 'A' && this.decisiones[4] === 'B';
        if (emberPresente && this.decisiones[6]) {
            this.mostrarElemento('final-con-ember');
        }
        
        // Con flechas especiales
        if (this.decisiones[1] === 'A') { // Zorros
            this.mostrarElemento('flechas-plata');
        } else if (this.decisiones[1] === 'B') { // Murciélagos
            this.mostrarElemento('flechas-antiengano');
        }
    }

    // ===================== REVELACIÓN DE SECCIONES =====================
    revelarSiguienteSeccion(numeroDecision) {
        const delay = 1500; // 1.5 segundos para efecto dramático
        
        setTimeout(() => {
            switch(numeroDecision) {
                case 1:
                    this.mostrarElemento('desarrollo-inicial');
                    this.mostrarElemento('viaje-valle');
                    this.mostrarElemento('encuentro-mapaches');
                    this.mostrarElemento('encuentro-cabras');
                    this.mostrarElemento('encuentro-avalancha');
                    this.mostrarElemento('refugio-conejos');
                    this.revelarDecision(2);
                    break;
                case 2:
                    this.mostrarElemento('viaje-aliados');
                    this.mostrarElemento('camino-cuervos');
                    this.revelarDecision(3);
                    break;
                case 3:
                    this.mostrarElemento('llegada-cuervos');
                    this.mostrarElemento('revelacion-lyra');
                    this.revelarDecision(4);
                    break;
                case 4:
                    this.mostrarElemento('post-revelacion');
                    this.mostrarElemento('viaje-post-revelacion');
                    this.revelarDecision(5);
                    break;
                case 5:
                    this.mostrarElemento('preparacion-final');
                    this.revelarDecision(6);
                    break;
                case 6:
                    this.mostrarElemento('viaje-aliados-finales');
                    this.mostrarElemento('entrada-templo');
                    this.revelarDecision(7);
                    break;
                case 7:
                    this.mostrarElemento('viaje-laberinto');
                    this.mostrarElemento('resolucion-final');
                    this.completarHistoria();
                    break;
            }
        }, delay);
    }

    revelarDecision(numero) {
        setTimeout(() => {
            this.mostrarElemento(`decision-${numero}`);
        }, 500);
    }

    completarHistoria() {
        setTimeout(() => {
            this.mostrarElemento('historia-completa');
            this.mostrarElemento('opciones-finales');
        }, 2000);
    }

    // ===================== UTILIDADES DOM =====================
    mostrarElemento(id, noRegistrar = false) {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.classList.remove('hidden');
            elemento.classList.add('reveal');
            
            // Debug: log que sección se está mostrando
            console.log('📍 [DecisionSystem] Mostrando sección:', id, noRegistrar ? '(sin registrar)' : '(registrando)');
            
            // Registrar la sección como visitada para la línea de tiempo
            // Solo si no estamos en modo restauración
            if (!noRegistrar) {
                this.registrarSeccionVisitada(id);
            }
        } else {
            console.warn('⚠️ [DecisionSystem] Elemento no encontrado:', id);
        }
    }

    ocultarElemento(id) {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.classList.add('hidden');
            elemento.classList.remove('reveal');
        }
    }

    ocultarTodoElContenido() {
        // Lista de todos los elementos que pueden estar visibles
        const elementos = [
            // Secciones principales
            'introduccion', 'desarrollo-inicial', 'camino-cuervos', 
            'llegada-cuervos', 'revelacion-lyra', 'post-revelacion',
            'preparacion-final', 'entrada-templo', 'resolucion-final',
            'historia-completa', 'opciones-finales',
            // Decisiones
            'decision-1', 'decision-2', 'decision-3', 'decision-4',
            'decision-5', 'decision-6', 'decision-7',
            // Contenido condicional principal
            'encuentro-confianza', 'encuentro-cautela',
            'zorros-confianza', 'zorros-cautela',
            'murcielagos-confianza', 'murcielagos-cautela',
            'melodia-ember', 'encuentro-hermanos', 'dialogo-ember', 'continuar-solo',
            'confrontacion-directa', 'estrategia-espionaje',
            // Encuentros menores y viajes
            'viaje-valle', 'encuentro-mapaches', 
            'resolucion-mapaches-confianza', 'resolucion-mapaches-cautela',
            'encuentro-cabras', 'encuentro-avalancha', 'refugio-conejos',
            'viaje-aliados', 'viaje-post-revelacion', 'viaje-aliados-finales', 'viaje-laberinto',
            // Secciones de Ember
            'ember-se-va', 'ember-se-queda', 'despedida-ember', 'ember-continua',
            // Aliados finales
            'encuentro-arañas', 'encuentro-conejos',
            'mapas-detallados', 'hierbas-proteccion',
            // Finales y epílogos
            'final-redencion', 'final-confrontacion',
            'epilogo-compasivo', 'epilogo-justicia', 'final-heroe-perfecto'
        ];
        
        // Ocultar todos los elementos
        elementos.forEach(id => this.ocultarElemento(id));
    }

    // ===================== INTERFAZ DE PROGRESO =====================
    crearInterfazProgreso() {
        const progreso = document.getElementById('progreso-decisiones');
        if (progreso) {
            progreso.innerHTML = `
                <div class="progreso-header">
                    <h3>Tu Historia Personalizada</h3>
                    <button onclick="decisionSystem.reiniciarHistoria()" class="btn-reiniciar">
                        Comenzar Nueva Historia
                    </button>
                </div>
                <div class="progreso-decisiones" id="lista-decisiones">
                    ${this.generarListaDecisiones()}
                </div>
                <div class="progreso-barra">
                    <div class="barra-fondo">
                        <div class="barra-progreso" style="width: ${this.calcularProgreso()}%"></div>
                    </div>
                    <span class="progreso-texto">${this.decisiones.length}/7 decisiones tomadas</span>
                </div>
            `;
        }
    }

    generarListaDecisiones() {
        const nombres = [
            'Primera Impresión',
            'Aliados Iniciales', 
            'Buscar a Ember',
            'Estrategia con Seraphina',
            'Dilema de Ember',
            'Aliados Finales',
            'Momento Final'
        ];

        let html = '';
        for (let i = 0; i < 7; i++) {
            const decision = this.decisiones[i];
            const clase = decision ? 'decision-tomada' : 'decision-pendiente';
            const texto = decision ? this.getTextoDecision(i + 1, decision) : 'Pendiente';
            
            html += `
                <div class="decision-item ${clase}">
                    <span class="decision-numero">${i + 1}</span>
                    <span class="decision-nombre">${nombres[i]}</span>
                    <span class="decision-resultado">${texto}</span>
                </div>
            `;
        }
        return html;
    }

    getTextoDecision(numero, opcion) {
        const textos = {
            1: { A: 'Confianza Total', B: 'Cautela Prudente' },
            2: { A: 'Zorros Plateros', B: 'Murciélagos Bibliotecarios' },
            3: { A: 'Buscar a Ember', B: 'Continuar Solo' },
            4: { A: 'Confrontación', B: 'Espionaje' },
            5: this.getTextoDecision5(opcion),
            6: { A: 'Arañas Tejedoras', B: 'Conejos Herbolarios' },
            7: { A: 'Redención Inmediata', B: 'Confrontación Final' }
        };
        
        return textos[numero] ? textos[numero][opcion] : opcion;
    }

    getTextoDecision5(opcion) {
        const tieneEmber = this.decisiones[2] === 'A';
        if (tieneEmber) {
            // Versión con Ember: dilema familiar
            return { A: 'Ember Regresa', B: 'Ember Continúa' }[opcion];
        } else {
            // Versión sin Ember: estrategia final
            return { A: 'Buscar Aliados', B: 'Directo al Templo' }[opcion];
        }
    }

    calcularProgreso() {
        return (this.decisiones.length / 7) * 100;
    }

    actualizarProgreso() {
        this.crearInterfazProgreso();
    }

    // ===================== UTILIDADES GENERALES =====================
    getRutaCompleta() {
        return this.decisiones.join('');
    }

    reiniciarHistoria() {
        if (confirm('¿Estás seguro de que quieres comenzar una nueva historia? Se perderán todas tus decisiones actuales.')) {
            // Limpiar localStorage
            localStorage.removeItem('el-cazador-decisiones');
            localStorage.removeItem('el-cazador-chapter');
            localStorage.removeItem('el-cazador-progreso');
            
            // Reinicializar el sistema
            this.decisiones = [];
            this.currentChapter = 1;
            
            // Limpiar timeline
            if (this.timelineSystem) {
                this.timelineSystem.limpiarTimeline();
            }
            
            // Ocultar todo el contenido
            this.ocultarTodoElContenido();
            
            // Mostrar solo la introducción y primera decisión
            this.mostrarElemento('introduccion');
            this.mostrarElemento('decision-1');
            
            // No es necesario reconstruir timeline aquí, se hace automáticamente
            
            // Actualizar interfaz
            this.crearInterfazProgreso();
            
            console.log('Historia reiniciada - comenzando desde el principio');
        }
    }

    guardarProgreso() {
        const progreso = {
            decisiones: this.decisiones,
            chapter: this.currentChapter,
            timestamp: Date.now(),
            elementosVisibles: this.obtenerElementosVisibles()
        };
        localStorage.setItem('el-cazador-progreso', JSON.stringify(progreso));
        
        // También guardar las decisiones por separado para fácil acceso
        localStorage.setItem('el-cazador-decisiones', JSON.stringify(this.decisiones));
    }

    obtenerElementosVisibles() {
        const elementos = [
            'introduccion', 'desarrollo-inicial', 'camino-cuervos', 
            'llegada-cuervos', 'revelacion-lyra', 'post-revelacion',
            'preparacion-final', 'entrada-templo', 'resolucion-final',
            'historia-completa', 'opciones-finales'
        ];
        
        return elementos.filter(id => {
            const elemento = document.getElementById(id);
            return elemento && !elemento.classList.contains('hidden');
        });
    }

    // ===================== TIMELINE SYSTEM INTEGRATION =====================

    // Método original tomarDecision modificado para incluir timeline
    tomarDecisionOriginal(numero, opcion) {
        // Guardar la decisión
        this.decisiones[numero - 1] = opcion;
        
        // Guardar en localStorage
        localStorage.setItem('el-cazador-decisiones', JSON.stringify(this.decisiones));
        
        // Ocultar la decisión actual
        this.ocultarElemento(`decision-${numero}`);
        
        // Mostrar contenido basado en la decisión
        this.mostrarContenidoSegunDecisiones();
        
        // Mostrar contenido siguiente en secuencia
        this.mostrarContenidoSiguiente(numero);
        
        // Actualizar interfaz de progreso
        this.crearInterfazProgreso();
        
        // La línea de tiempo se actualiza automáticamente cuando se registran las secciones
        // Comentado para evitar conflicto con el sistema progresivo
        // setTimeout(() => {
        //     this.updateTimelineProgress();
        // }, 500);
        
        // Scroll suave al siguiente contenido
        setTimeout(() => {
            this.scrollToNextContent(numero);
        }, 1000);
    }
    
    mostrarContenidoSiguiente(numeroDecision) {
        // Mostrar la siguiente decisión después de un delay
        setTimeout(() => {
            if (numeroDecision === 1) {
                this.mostrarElemento('decision-2');
            } else if (numeroDecision === 2) {
                this.mostrarElemento('decision-3');  
            } else if (numeroDecision === 3) {
                this.mostrarElemento('decision-4');
            } else if (numeroDecision === 4) {
                this.mostrarElemento('decision-5');
            } else if (numeroDecision === 5) {
                this.mostrarElemento('decision-6');
            } else if (numeroDecision === 6) {
                this.mostrarElemento('decision-7');
            } else if (numeroDecision === 7) {
                this.completarHistoria();
            }
        }, 1500); // Delay para permitir que se muestre el contenido anterior
    }
    
    // Método delegado al TimelineSystem
    registrarSeccionVisitada(seccionId) {
        if (this.timelineSystem) {
            this.timelineSystem.registrarSeccionVisitada(seccionId);
        } else {
            console.warn('⚠️ [DecisionSystem] TimelineSystem no disponible para registrar:', seccionId);
        }
    }
    
    scrollToNextContent(numeroDecision) {
        // Hacer scroll suave al contenido que acaba de aparecer
        let targetElement;
        
        if (numeroDecision === 1) {
            targetElement = document.getElementById('desarrollo-inicial');
        } else if (numeroDecision === 2) {
            targetElement = document.getElementById('decision-3');
        } else if (numeroDecision === 3) {
            targetElement = document.getElementById('decision-4');
        } else if (numeroDecision === 4) {
            targetElement = document.getElementById('decision-5');
        } else if (numeroDecision === 5) {
            targetElement = document.getElementById('decision-6');
        } else if (numeroDecision === 6) {
            targetElement = document.getElementById('decision-7');
        } else if (numeroDecision === 7) {
            targetElement = document.getElementById('historia-completa');
        }
        
        if (targetElement) {
            targetElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
    }

    setupEventListeners() {
        // Crear indicador de auto-guardado
        this.crearIndicadorAutoSave();
        
        // Guardar progreso automáticamente cada 10 segundos
        setInterval(() => {
            this.guardarProgreso();
            this.mostrarIndicadorAutoSave();
        }, 10000);

        // Guardar progreso antes de cerrar la página
        window.addEventListener('beforeunload', (event) => {
            this.guardarProgreso();
            // Guardar también en sessionStorage
            sessionStorage.setItem('el-cazador-decisiones', JSON.stringify(this.decisiones));
        });

        // Manejar navegación entre capítulos
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' && e.ctrlKey) {
                e.preventDefault();
                this.reiniciarHistoria();
            }
        });

        // Mostrar indicador si se restauró progreso
        if (this.decisiones.length > 0) {
            this.mostrarIndicadorProgreso();
        }
    }

    mostrarIndicadorProgreso() {
        // Crear y mostrar un indicador temporal
        const indicador = document.createElement('div');
        indicador.className = 'indicador-progreso-restaurado';
        indicador.innerHTML = `
            <div class="indicador-contenido">
                <span>📖</span>
                <p>Progreso restaurado: ${this.decisiones.length}/7 decisiones</p>
            </div>
        `;
        
        document.body.appendChild(indicador);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            indicador.classList.add('fadeout');
            setTimeout(() => {
                if (document.body.contains(indicador)) {
                    document.body.removeChild(indicador);
                }
            }, 500);
        }, 3000);
    }

    crearIndicadorAutoSave() {
        const indicador = document.createElement('div');
        indicador.id = 'auto-save-indicator';
        indicador.className = 'auto-save-indicator';
        indicador.innerHTML = '💾 Progreso guardado';
        document.body.appendChild(indicador);
    }

    mostrarIndicadorAutoSave() {
        const indicador = document.getElementById('auto-save-indicator');
        if (indicador) {
            indicador.classList.add('visible');
            setTimeout(() => {
                indicador.classList.remove('visible');
            }, 2000);
        }
    }

    // Método para debug - mostrar todas las decisiones
    debug() {
        console.log('=== ESTADO ACTUAL DEL SISTEMA ===');
        console.log('Decisiones tomadas:', this.decisiones);
        console.log('Ruta completa:', this.getRutaCompleta());
        console.log('Progreso:', `${this.decisiones.length}/7`);
        console.log('Capítulo actual:', this.currentChapter);
    }
}

// ===================== FUNCIONES GLOBALES =====================
function tomarDecision(numero, opcion) {
    window.decisionSystem.tomarDecisionOriginal(numero, opcion);
}

function reiniciarHistoria() {
    if (window.decisionSystem) {
        window.decisionSystem.reiniciarHistoria();
    }
}

// ===================== FUNCIONES PARA LÍNEA DE TIEMPO =====================
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

function mostrarDebug() {
    window.decisionSystem.debug();
}

// ===================== INICIALIZACIÓN =====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando Sistema de Decisiones de El Cazador de Medianoche...');
    window.decisionSystem = new DecisionSystem();
    
    // Hacer disponible para debug en consola
    window.debug = mostrarDebug;
});

// ===================== EFECTOS VISUALES ADICIONALES =====================
function efectoEscritura(elementId, texto, velocidad = 50) {
    const elemento = document.getElementById(elementId);
    if (!elemento) return;
    
    elemento.innerHTML = '';
    elemento.classList.remove('hidden');
    
    let i = 0;
    const timer = setInterval(() => {
        if (i < texto.length) {
            elemento.innerHTML += texto.charAt(i);
            i++;
        } else {
            clearInterval(timer);
        }
    }, velocidad);
}

// Export para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DecisionSystem;
}