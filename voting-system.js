// Sistema de Votación Interactiva para "El Cazador de Medianoche"
// Maneja las decisiones del lector y la navegación entre ramas narrativas

class VotingSystem {
    constructor() {
        this.decisions = this.loadDecisions();
        this.currentDecision = 1;
        this.init();
    }

    // Cargar decisiones previas del localStorage
    loadDecisions() {
        const saved = localStorage.getItem('cazadorMedianoche_decisions');
        return saved ? JSON.parse(saved) : {};
    }

    // Guardar decisiones en localStorage
    saveDecisions() {
        localStorage.setItem('cazadorMedianoche_decisions', JSON.stringify(this.decisions));
    }

    // Inicializar el sistema
    init() {
        this.createDecisionInterface();
        this.updateProgressIndicator();
        this.addResetButton();
    }

    // Crear la interfaz de votación
    createDecisionInterface() {
        const decisionContainer = document.getElementById('decision-container');
        if (!decisionContainer) return;

        // Para seccion-01.html, necesitamos manejar dos decisiones secuenciales
        const currentPage = window.location.pathname.split('/').pop();
        if (currentPage === 'seccion-01.html') {
            this.createSequentialDecisions();
            return;
        }

        const decisionData = this.getDecisionData();
        if (!decisionData) return;

        decisionContainer.innerHTML = `
            <div class="voting-section">
                <div class="decision-header">
                    <h3>🌙 Decisión ${decisionData.number}</h3>
                    <p class="decision-context">${decisionData.context}</p>
                </div>
                
                <div class="decision-question">
                    <p class="question-text">${decisionData.question}</p>
                </div>

                <div class="decision-options">
                    <button class="option-button option-a" onclick="votingSystem.makeDecision('a')">
                        <span class="option-label">Opción A</span>
                        <span class="option-text">${decisionData.optionA}</span>
                    </button>
                    
                    <button class="option-button option-b" onclick="votingSystem.makeDecision('b')">
                        <span class="option-label">Opción B</span>
                        <span class="option-text">${decisionData.optionB}</span>
                    </button>
                </div>

                <div class="decision-impact">
                    <details>
                        <summary>💡 Ver posible impacto de esta decisión</summary>
                        <p>${decisionData.impact}</p>
                    </details>
                </div>
            </div>
        `;
    }

    // Crear interfaz para decisiones secuenciales (seccion-01.html)
    createSequentialDecisions() {
        const decisionContainer = document.getElementById('decision-container');
        
        if (!this.decisions[1]) {
            // Mostrar decisión 1
            const decision1 = this.getDecisionData(1);
            decisionContainer.innerHTML = `
                <div class="voting-section">
                    <div class="decision-header">
                        <h3>🌙 Decisión ${decision1.number}</h3>
                        <p class="decision-context">${decision1.context}</p>
                    </div>
                    
                    <div class="decision-question">
                        <p class="question-text">${decision1.question}</p>
                    </div>

                    <div class="decision-options">
                        <button class="option-button option-a" onclick="votingSystem.makeSequentialDecision(1, 'a')">
                            <span class="option-label">Opción A</span>
                            <span class="option-text">${decision1.optionA}</span>
                        </button>
                        
                        <button class="option-button option-b" onclick="votingSystem.makeSequentialDecision(1, 'b')">
                            <span class="option-label">Opción B</span>
                            <span class="option-text">${decision1.optionB}</span>
                        </button>
                    </div>

                    <div class="decision-impact">
                        <details>
                            <summary>💡 Ver posible impacto de esta decisión</summary>
                            <p>${decision1.impact}</p>
                        </details>
                    </div>
                </div>
            `;
        } else if (!this.decisions[2]) {
            // Mostrar decisión 2
            const decision2 = this.getDecisionData(2);
            decisionContainer.innerHTML = `
                <div class="voting-section">
                    <div class="decision-header">
                        <h3>🌙 Decisión ${decision2.number}</h3>
                        <p class="decision-context">${decision2.context}</p>
                        <p style="color: #cd853f; font-style: italic;">Decisión previa: ${this.decisions[1] === 'a' ? 'Confianza total' : 'Cautela vigilante'}</p>
                    </div>
                    
                    <div class="decision-question">
                        <p class="question-text">${decision2.question}</p>
                    </div>

                    <div class="decision-options">
                        <button class="option-button option-a" onclick="votingSystem.makeSequentialDecision(2, 'a')">
                            <span class="option-label">Opción A</span>
                            <span class="option-text">${decision2.optionA}</span>
                        </button>
                        
                        <button class="option-button option-b" onclick="votingSystem.makeSequentialDecision(2, 'b')">
                            <span class="option-label">Opción B</span>
                            <span class="option-text">${decision2.optionB}</span>
                        </button>
                    </div>

                    <div class="decision-impact">
                        <details>
                            <summary>💡 Ver posible impacto de esta decisión</summary>
                            <p>${decision2.impact}</p>
                        </details>
                    </div>
                </div>
            `;
        } else {
            // Ambas decisiones tomadas, mostrar resumen y navegar
            this.showSequentialComplete();
        }
    }

    // Manejar decisiones secuenciales
    makeSequentialDecision(decisionNumber, choice) {
        this.decisions[decisionNumber] = choice;
        this.saveDecisions();
        
        if (decisionNumber === 1) {
            // Mostrar decisión 2
            setTimeout(() => {
                this.createSequentialDecisions();
            }, 1000);
        } else if (decisionNumber === 2) {
            // Ambas decisiones completadas, navegar
            setTimeout(() => {
                this.navigateToNextSection();
            }, 2000);
        }
        
        // Mostrar confirmación temporal
        this.showDecisionConfirmation(choice);
    }

    // Mostrar resumen de decisiones secuenciales completadas
    showSequentialComplete() {
        const decisionContainer = document.getElementById('decision-container');
        const route = this.decisions[1] + this.decisions[2];
        const routeDescriptions = {
            'aa': 'Confianza Total + Zorros Plateros',
            'ab': 'Confianza Total + Murciélagos Bibliotecarios',
            'ba': 'Cautela Vigilante + Zorros Plateros', 
            'bb': 'Cautela Vigilante + Murciélagos Bibliotecarios'
        };

        decisionContainer.innerHTML = `
            <div class="decision-confirmation">
                <div class="confirmation-icon">✨</div>
                <h3>Decisiones Completadas</h3>
                <p><strong>Tu camino elegido:</strong> ${routeDescriptions[route]}</p>
                <p>La historia continuará según tus decisiones...</p>
                <div class="loading-indicator">
                    <div class="loading-bar"></div>
                </div>
            </div>
        `;
        
        setTimeout(() => {
            this.navigateToNextSection();
        }, 2000);
    }

    // Obtener datos de la decisión actual
    getDecisionData(decisionNumber = null) {
        const decisionsData = {
            1: {
                number: 1,
                context: "Final del Capítulo 1 - Primer encuentro con Seraphina",
                question: "Axel observa a Seraphina herida. Su instinto le dice que algo no está bien, pero ella parece genuinamente desesperada. ¿Qué debería hacer?",
                optionA: "Confiar y ayudar inmediatamente",
                optionB: "Ayudar pero mantenerse alerta",
                impact: "Esta decisión determina qué tan efectivas son las manipulaciones de Seraphina y cuánta información personal comparte Axel."
            },
            2: {
                number: 2,
                context: "Entre Capítulos 2 y 3 - Camino hacia las Cuevas Brillantes",
                question: "En su camino hacia las Cuevas Brillantes, Axel y Seraphina se topan con dos senderos. ¿Qué ruta elegir?",
                optionA: "Aldea de los Zorros Plateros (neutral pero desconfiados)",
                optionB: "Territorio de los Murciélagos Bibliotecarios (sabios pero exigentes)",
                impact: "Esta decisión afecta las herramientas y conocimientos que Axel obtiene para los desafíos posteriores."
            },
            "2b": {
                number: "2B",
                context: "Entre Capítulos 3 y 4 - Después de obtener las Lágrimas de Cristal",
                question: "En el camino hacia el Bosque de Cuervos, Axel escucha una melodía familiar de flauta que solo su hermano Ember conoce. La música parece venir de un valle lateral. ¿Debería investigar el sonido y desviarse de la ruta, o continuar según el plan?",
                optionA: "Investigar la melodía (Buscar a Ember)",
                optionB: "Continuar la misión (Sin Ember)",
                impact: "Esta decisión determina si Ember se une al grupo, cambiando completamente las dinámicas posteriores y las estrategias contra Seraphina."
            },
            3: {
                number: 3,
                context: "Final del Capítulo 4 - Después de la revelación de Lyra",
                question: "Lyra ha revelado la verdad sobre Seraphina. Axel debe decidir cómo proceder con esta información devastadora.",
                optionA: "Confrontar a Seraphina directamente",
                optionB: "Seguir el juego y espiar sus movimientos",
                impact: "Esta decisión define completamente los Capítulos 5-6, desde batallas inmediatas hasta infiltración."
            },
            4: {
                number: 4,
                context: "Entre Capítulos 6 y 7 - Camino al Laberinto de Tejones",
                question: "El grupo necesita provisiones e información antes del peligroso laberinto. ¿Dónde buscar ayuda?",
                optionA: "Colonia de Arañas Tejedoras del Destino (cobran en secretos)",
                optionB: "Pueblo de los Conejos Herbolarios (pacíficos pero vulnerables)",
                impact: "Determina el nivel de preparación para el enfrentamiento final y las consecuencias morales."
            },
            5: {
                number: 5,
                context: "Capítulo 8 - Momento crucial con las Lágrimas de Luna",
                question: "Axel tiene las Lágrimas de Luna en sus manos. El espíritu de su padre le susurra consejos. ¿Qué elige?",
                optionA: "Usar las Lágrimas para curar a la madre de Seraphina",
                optionB: "Confrontar a Seraphina primero, luego decidir",
                impact: "Determina el tipo de redención (inmediata vs. gradual) y el desarrollo del epílogo."
            }
        };

        return decisionsData[decisionNumber || this.currentDecision];
    }

    // Procesar una decisión del lector
    makeDecision(choice) {
        this.decisions[this.currentDecision] = choice;
        this.saveDecisions();
        
        // Mostrar animación de confirmación
        this.showDecisionConfirmation(choice);
        
        // Navegar a la siguiente sección después de un breve delay
        setTimeout(() => {
            this.navigateToNextSection();
        }, 2000);
    }

    // Mostrar confirmación de decisión
    showDecisionConfirmation(choice) {
        const container = document.getElementById('decision-container');
        const choiceText = choice === 'a' ? 'Opción A' : 'Opción B';
        
        container.innerHTML = `
            <div class="decision-confirmation">
                <div class="confirmation-icon">✨</div>
                <h3>Decisión tomada: ${choiceText}</h3>
                <p>Tu elección ha sido registrada. La historia continuará según tu decisión...</p>
                <div class="loading-indicator">
                    <div class="loading-bar"></div>
                </div>
            </div>
        `;
    }

    // Navegar a la siguiente sección según las decisiones
    navigateToNextSection() {
        const route = this.calculateRoute();
        const nextPage = this.getNextPageUrl(route);
        
        if (nextPage) {
            window.location.href = nextPage;
        }
    }

    // Calcular la ruta basada en las decisiones
    calculateRoute() {
        const d = this.decisions;
        return d; // Retornar todas las decisiones
    }

    // Obtener URL de la siguiente página
    getNextPageUrl(decisions) {
        const currentPage = window.location.pathname.split('/').pop();
        
        // Navegación basada en la página actual y las decisiones tomadas
        switch (currentPage) {
            case 'seccion-01.html':
                // Después de tomar decisiones 1 y 2, navegar a la rama apropiada
                if (decisions[1] && decisions[2]) {
                    const route = decisions[1] + decisions[2];
                    const routeMap = {
                        'aa': 'seccion-01-aa.html',
                        'ab': 'seccion-01-ab.html',
                        'ba': 'seccion-01-ba.html',
                        'bb': 'seccion-01-bb.html'
                    };
                    return routeMap[route];
                }
                break;
                
            case 'seccion-01-aa.html':
            case 'seccion-01-ab.html':
            case 'seccion-01-ba.html':
            case 'seccion-01-bb.html':
                // Navegación a decisión 2B (buscar a Ember)
                if (!decisions["2b"]) {
                    // Mostrar decisión 2B sobre buscar a Ember
                    return null; // Se manejará con setCurrentDecision("2b")
                } else {
                    // Después de decisión 2B, ir a la versión apropiada
                    return decisions["2b"] === 'a' ? 'seccion-02-ember.html' : 'convergencia-cuervos.html';
                }
                
            case 'seccion-02-ember.html':
                // Con Ember, van directamente a convergencia-cuervos
                return 'convergencia-cuervos.html';
                
            case 'convergencia-cuervos.html':
                // Decisión 3: Confrontación vs Espionaje
                if (decisions[3]) {
                    return decisions[3] === 'a' ? 'seccion-02-a.html' : 'seccion-02-b.html';
                }
                break;
                
            case 'seccion-02-a.html':
                // Decisión 4: Arañas vs Conejos
                if (decisions[4]) {
                    // Determinar si Ember está presente para elegir la versión correcta
                    const hasEmber = decisions["2b"] === 'a';
                    if (decisions[4] === 'a') {
                        return hasEmber ? 'seccion-intermedia-ember-a.html' : 'seccion-intermedia-a.html';
                    } else {
                        return hasEmber ? 'seccion-intermedia-ember-b.html' : 'seccion-intermedia-b.html';
                    }
                }
                break;
                
            case 'seccion-02-b.html':
                // Decisión 4: Arañas vs Conejos
                if (decisions[4]) {
                    // Determinar si Ember está presente para elegir la versión correcta
                    const hasEmber = decisions["2b"] === 'a';
                    if (decisions[4] === 'a') {
                        return hasEmber ? 'seccion-intermedia-ember-a.html' : 'seccion-intermedia-a.html';
                    } else {
                        return hasEmber ? 'seccion-intermedia-ember-b.html' : 'seccion-intermedia-b.html';
                    }
                }
                break;
                
            case 'seccion-intermedia-a.html':
            case 'seccion-intermedia-b.html':
                // Sin Ember - van directamente a tejones
                return 'convergencia-tejones.html';
                
            case 'seccion-intermedia-ember-a.html':
            case 'seccion-intermedia-ember-b.html':
                // Con Ember - van a la escena de despedida
                return 'despedida-ember.html';
                
            case 'despedida-ember.html':
                // Después de la despedida, continúan al laberinto
                return 'convergencia-tejones.html';
                
            case 'convergencia-tejones.html':
                // Decisión 5: Final
                if (decisions[5]) {
                    return decisions[5] === 'a' ? 'seccion-03-a.html' : 'seccion-03-b.html';
                }
                break;
                
            case 'seccion-03-a.html':
            case 'seccion-03-b.html':
                // Finales - no hay navegación adicional
                return null;
        }
        
        return null;
    }

    // Actualizar indicador de progreso
    updateProgressIndicator() {
        const progressContainer = document.getElementById('progress-indicator');
        if (!progressContainer) return;

        const totalDecisions = 6; // Ahora incluye la decisión 2B sobre Ember
        const madeDecisions = Object.keys(this.decisions).length;
        const progressPercent = (madeDecisions / totalDecisions) * 100;

        progressContainer.innerHTML = `
            <div class="progress-header">
                <span class="progress-title">Progreso de la Historia</span>
                <span class="progress-count">${madeDecisions}/${totalDecisions} decisiones</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progressPercent}%"></div>
            </div>
            <div class="decisions-summary">
                ${this.getDecisionsSummary()}
            </div>
        `;
    }

    // Obtener resumen de decisiones tomadas con consecuencias
    getDecisionsSummary() {
        const summaryLabels = {
            1: "Confianza inicial",
            2: "Ruta elegida",
            "2b": "Buscar hermano",
            3: "Estrategia revelación",
            4: "Preparación final",
            5: "Uso de Lágrimas"
        };

        const consequenceLabels = {
            1: { a: "Vínculo emocional fuerte", b: "Respeto intelectual" },
            2: { a: "Ventaja en combate directo", b: "Ventaja en revelación" },
            "2b": { a: "Ember se une al grupo", b: "Continúa sin Ember" },
            3: { a: "Dinámicas directas", b: "Conocimiento de red completa" },
            4: { a: "Máxima preparación", b: "Máxima claridad moral" },
            5: { a: "Redención inmediata", b: "Redención gradual" }
        };

        let summary = '';
        const decisionKeys = [1, 2, "2b", 3, 4, 5];
        
        for (const key of decisionKeys) {
            const decision = this.decisions[key];
            const label = summaryLabels[key];
            if (decision) {
                const consequence = consequenceLabels[key][decision];
                summary += `<div class="decision-summary-item">${label}: ✓ ${decision.toUpperCase()} <br><span class="consequence">→ ${consequence}</span></div>`;
            } else {
                summary += `<div class="decision-summary-item">${label}: ⏳ Pendiente</div>`;
            }
        }

        return summary;
    }

    // Agregar botón de reinicio
    addResetButton() {
        const resetContainer = document.getElementById('reset-container');
        if (!resetContainer) return;

        resetContainer.innerHTML = `
            <button class="reset-button" onclick="votingSystem.resetStory()">
                🔄 Reiniciar Historia
            </button>
            <p class="reset-description">
                Explora diferentes decisiones y descubre todos los caminos posibles
            </p>
        `;
    }

    // Reiniciar la historia
    resetStory() {
        const confirmed = confirm('🔄 ¿Estás seguro de que quieres reiniciar tu historia?\n\n' +
                                'Se perderán todas las decisiones tomadas y podrás comenzar una nueva aventura ' +
                                'eligiendo diferentes opciones.\n\n' +
                                '¿Continuar?');
        
        if (confirmed) {
            localStorage.removeItem('cazadorMedianoche_decisions');
            this.decisions = {};
            this.currentDecision = 1;
            
            // Mostrar mensaje de confirmación
            this.showResetConfirmation();
            
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        }
    }
    
    // Mostrar confirmación de reinicio
    showResetConfirmation() {
        const resetContainer = document.getElementById('reset-container');
        if (resetContainer) {
            resetContainer.innerHTML = `
                <div class="reset-confirmation">
                    <div class="confirmation-icon">🔄</div>
                    <h3>Historia Reiniciada</h3>
                    <p>Todas las decisiones han sido borradas. Redirigiendo al inicio para comenzar una nueva aventura...</p>
                    <div class="loading-indicator">
                        <div class="loading-bar"></div>
                    </div>
                </div>
            `;
        }
    }
    
    // Función global para reinicio rápido (sin confirmación)
    quickReset() {
        localStorage.removeItem('cazadorMedianoche_decisions');
        this.decisions = {};
        this.currentDecision = 1;
        window.location.href = 'seccion-01.html';
    }

    // Establecer la decisión actual (llamado desde las páginas)
    setCurrentDecision(decisionNumber) {
        this.currentDecision = decisionNumber;
        this.createDecisionInterface();
    }
}

// Inicializar el sistema cuando se carga la página
const votingSystem = new VotingSystem();

// Función auxiliar para detectar qué decisión mostrar
function initDecisionForPage() {
    const currentPage = window.location.pathname.split('/').pop();
    
    const decisionMap = {
        'seccion-01.html': 1, // Maneja decisiones 1 y 2 secuencialmente
        'seccion-01-aa.html': "2b", // Decisión sobre buscar a Ember
        'seccion-01-ab.html': "2b", 
        'seccion-01-ba.html': "2b",
        'seccion-01-bb.html': "2b",
        'seccion-02-ember.html': null, // Ya no necesita decisiones, navega directamente
        'convergencia-cuervos.html': 3,
        'seccion-02-a.html': 4,
        'seccion-02-b.html': 4,
        'seccion-intermedia-a.html': null, // Ya no necesita decisiones, navega directamente
        'seccion-intermedia-b.html': null,
        'seccion-intermedia-ember-a.html': null,
        'seccion-intermedia-ember-b.html': null,
        'despedida-ember.html': null,
        'convergencia-tejones.html': 5
    };

    const decisionNumber = decisionMap[currentPage];
    if (decisionNumber) {
        votingSystem.setCurrentDecision(decisionNumber);
    }
}

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initDecisionForPage);