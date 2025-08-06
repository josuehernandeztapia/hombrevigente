/**
 * DiagnósticoVigente™ - Simplified Demo Component
 * Optimized Three.js visualization for investor pitch
 * Duration: 30-60 seconds
 */

class DiagnosticDemo {
    constructor(containerId) {
        this.containerId = containerId;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.animationId = null;
        this.isRunning = false;
        
        // Simplified archetypos (3 instead of 5)
        this.archetypos = [
            {
                name: 'Ejecutivo Estresado',
                color: 0xff4444,
                riskLevel: 0.8,
                symptoms: ['fatiga', 'ansiedad', 'hipertensión'],
                position: { x: -3, y: 0, z: 0 }
            },
            {
                name: 'Atleta Optimizado',
                color: 0x44ff44,
                riskLevel: 0.2,
                symptoms: ['rendimiento', 'recuperación'],
                position: { x: 0, y: 0, z: 0 }
            },
            {
                name: 'Senior Preventivo',
                color: 0xffaa44,
                riskLevel: 0.6,
                symptoms: ['metabolismo', 'cognición'],
                position: { x: 3, y: 0, z: 0 }
            }
        ];
        
        this.vigentIndex = 0;
        this.audioContext = null;
        this.init();
    }

    init() {
        this.createScene();
        this.createLights();
        this.createArchetypos();
        this.createUI();
        this.setupAudio();
        this.animate();
    }

    createScene() {
        const container = document.getElementById(this.containerId);
        
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a);
        
        // Camera setup
        this.camera = new THREE.PerspectiveCamera(
            75,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(0, 2, 8);
        
        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true 
        });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        container.appendChild(this.renderer.domElement);
        
        // Responsive resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    createLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
        this.scene.add(ambientLight);
        
        // Main spotlight
        const spotlight = new THREE.SpotLight(0x04D9FF, 1.5);
        spotlight.position.set(0, 10, 5);
        spotlight.castShadow = true;
        spotlight.shadow.mapSize.width = 1024;
        spotlight.shadow.mapSize.height = 1024;
        this.scene.add(spotlight);
        
        // Accent lights for each archetype
        this.archetypos.forEach((archetype, index) => {
            const light = new THREE.PointLight(archetype.color, 0.8, 10);
            light.position.copy(archetype.position);
            light.position.y += 3;
            this.scene.add(light);
        });
    }

    createArchetypos() {
        this.archetypeObjects = [];
        
        this.archetypos.forEach((archetype, index) => {
            const group = new THREE.Group();
            
            // Main sphere (representing the person)
            const geometry = new THREE.SphereGeometry(0.8, 32, 32);
            const material = new THREE.MeshPhongMaterial({
                color: archetype.color,
                transparent: true,
                opacity: 0.8,
                shininess: 100
            });
            
            const sphere = new THREE.Mesh(geometry, material);
            sphere.castShadow = true;
            sphere.receiveShadow = true;
            group.add(sphere);
            
            // Risk indicator ring
            const ringGeometry = new THREE.RingGeometry(1.2, 1.5, 32);
            const ringMaterial = new THREE.MeshBasicMaterial({
                color: this.getRiskColor(archetype.riskLevel),
                transparent: true,
                opacity: 0.6,
                side: THREE.DoubleSide
            });
            
            const ring = new THREE.Mesh(ringGeometry, ringMaterial);
            ring.rotation.x = Math.PI / 2;
            group.add(ring);
            
            // Data particles
            this.createDataParticles(group, archetype);
            
            group.position.copy(archetype.position);
            this.scene.add(group);
            this.archetypeObjects.push(group);
        });
    }

    createDataParticles(parent, archetype) {
        const particleCount = 20;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 4;
            positions[i + 1] = (Math.random() - 0.5) * 4;
            positions[i + 2] = (Math.random() - 0.5) * 4;
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.PointsMaterial({
            color: archetype.color,
            size: 0.05,
            transparent: true,
            opacity: 0.7
        });
        
        const particles = new THREE.Points(geometry, material);
        parent.add(particles);
        
        // Store reference for animation
        particles.userData = { archetype, originalPositions: positions.slice() };
    }

    getRiskColor(riskLevel) {
        if (riskLevel > 0.7) return 0xff4444;
        if (riskLevel > 0.4) return 0xffaa44;
        return 0x44ff44;
    }

    createUI() {
        const container = document.getElementById(this.containerId);
        
        // UI Overlay
        const ui = document.createElement('div');
        ui.className = 'diagnostic-ui';
        ui.innerHTML = `
            <div class="ui-header">
                <h2>DiagnósticoVigente™</h2>
                <div class="vigent-index">
                    <span>Índice Vigente™</span>
                    <div class="index-value">${this.vigentIndex}</div>
                </div>
            </div>
            
            <div class="archetypos-panel">
                ${this.archetypos.map((arch, i) => `
                    <div class="archetype-card" data-index="${i}">
                        <div class="archetype-name">${arch.name}</div>
                        <div class="risk-meter">
                            <div class="risk-bar" style="width: ${arch.riskLevel * 100}%; background-color: ${this.getRiskColorHex(arch.riskLevel)}"></div>
                        </div>
                        <div class="symptoms">${arch.symptoms.join(', ')}</div>
                    </div>
                `).join('')}
            </div>
            
            <div class="controls">
                <button id="startDemo" class="demo-btn">Iniciar Análisis</button>
                <button id="pauseDemo" class="demo-btn secondary">Pausar</button>
            </div>
            
            <div class="status-bar">
                <div class="processing">Procesando biomarcadores...</div>
                <div class="progress-bar">
                    <div class="progress" id="demoProgress"></div>
                </div>
            </div>
        `;
        
        container.appendChild(ui);
        this.setupUIEvents();
    }

    getRiskColorHex(riskLevel) {
        if (riskLevel > 0.7) return '#ff4444';
        if (riskLevel > 0.4) return '#ffaa44';
        return '#44ff44';
    }

    setupUIEvents() {
        document.getElementById('startDemo').addEventListener('click', () => this.startDemo());
        document.getElementById('pauseDemo').addEventListener('click', () => this.pauseDemo());
        
        // Archetype hover effects
        document.querySelectorAll('.archetype-card').forEach((card, index) => {
            card.addEventListener('mouseenter', () => this.highlightArchetype(index));
            card.addEventListener('mouseleave', () => this.unhighlightArchetype(index));
        });
    }

    setupAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.log('Audio context not available');
        }
    }

    playTone(frequency, duration = 0.1) {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.1, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }

    startDemo() {
        this.isRunning = true;
        this.demoStartTime = Date.now();
        this.playTone(440); // A4 note for start
        
        // Animate Vigent Index
        this.animateVigentIndex();
        
        // Start archetype analysis sequence
        this.runAnalysisSequence();
    }

    pauseDemo() {
        this.isRunning = false;
        this.playTone(220); // Lower tone for pause
    }

    animateVigentIndex() {
        if (!this.isRunning) return;
        
        const targetIndex = Math.floor(Math.random() * 100) + 50;
        const indexElement = document.querySelector('.index-value');
        let currentIndex = parseInt(indexElement.textContent) || 0;
        
        const animate = () => {
            if (!this.isRunning) return;
            
            if (Math.abs(currentIndex - targetIndex) > 1) {
                currentIndex += (targetIndex - currentIndex) * 0.1;
                indexElement.textContent = Math.floor(currentIndex);
                requestAnimationFrame(animate);
            } else {
                indexElement.textContent = targetIndex;
                setTimeout(() => this.animateVigentIndex(), 2000);
            }
        };
        
        animate();
    }

    runAnalysisSequence() {
        if (!this.isRunning) return;
        
        const sequence = [
            () => this.highlightArchetype(0),
            () => this.analyzeArchetype(0),
            () => this.highlightArchetype(1),
            () => this.analyzeArchetype(1),
            () => this.highlightArchetype(2),
            () => this.analyzeArchetype(2),
            () => this.showResults()
        ];
        
        let step = 0;
        const runStep = () => {
            if (!this.isRunning || step >= sequence.length) return;
            
            sequence[step]();
            step++;
            
            setTimeout(runStep, 3000); // 3 seconds per step
        };
        
        runStep();
    }

    highlightArchetype(index) {
        if (this.archetypeObjects[index]) {
            const obj = this.archetypeObjects[index];
            const sphere = obj.children[0];
            
            // Scale up animation
            gsap.to(sphere.scale, {
                duration: 0.5,
                x: 1.2,
                y: 1.2,
                z: 1.2,
                ease: "power2.out"
            });
            
            // Glow effect
            sphere.material.emissive.setHex(0x222222);
        }
        
        // UI highlight
        document.querySelectorAll('.archetype-card').forEach((card, i) => {
            card.classList.toggle('active', i === index);
        });
        
        this.playTone(330 + index * 110, 0.2);
    }

    unhighlightArchetype(index) {
        if (this.archetypeObjects[index]) {
            const obj = this.archetypeObjects[index];
            const sphere = obj.children[0];
            
            // Scale down animation
            gsap.to(sphere.scale, {
                duration: 0.5,
                x: 1,
                y: 1,
                z: 1,
                ease: "power2.out"
            });
            
            sphere.material.emissive.setHex(0x000000);
        }
    }

    analyzeArchetype(index) {
        const archetype = this.archetypos[index];
        const obj = this.archetypeObjects[index];
        
        // Particle animation
        const particles = obj.children.find(child => child.type === 'Points');
        if (particles) {
            const positions = particles.geometry.attributes.position.array;
            const originalPositions = particles.userData.originalPositions;
            
            for (let i = 0; i < positions.length; i += 3) {
                gsap.to(positions, {
                    duration: 2,
                    [i]: originalPositions[i] + (Math.random() - 0.5) * 2,
                    [i + 1]: originalPositions[i + 1] + (Math.random() - 0.5) * 2,
                    [i + 2]: originalPositions[i + 2] + (Math.random() - 0.5) * 2,
                    onUpdate: () => {
                        particles.geometry.attributes.position.needsUpdate = true;
                    }
                });
            }
        }
        
        // Update progress
        const progress = ((index + 1) / this.archetypos.length) * 100;
        document.getElementById('demoProgress').style.width = `${progress}%`;
    }

    showResults() {
        const resultsOverlay = document.createElement('div');
        resultsOverlay.className = 'results-overlay';
        resultsOverlay.innerHTML = `
            <div class="results-content">
                <h3>Análisis Completado</h3>
                <div class="key-insights">
                    <div class="insight">
                        <span class="metric">85%</span>
                        <span class="label">Precisión Diagnóstica</span>
                    </div>
                    <div class="insight">
                        <span class="metric">2.3s</span>
                        <span class="label">Tiempo de Análisis</span>
                    </div>
                    <div class="insight">
                        <span class="metric">47</span>
                        <span class="label">Biomarcadores</span>
                    </div>
                </div>
                <button id="closeResults" class="demo-btn">Cerrar</button>
            </div>
        `;
        
        document.getElementById(this.containerId).appendChild(resultsOverlay);
        
        document.getElementById('closeResults').addEventListener('click', () => {
            resultsOverlay.remove();
            this.isRunning = false;
        });
        
        this.playTone(523, 0.5); // C5 note for completion
    }

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        // Rotate archetypos slowly
        this.archetypeObjects.forEach((obj, index) => {
            obj.rotation.y += 0.005 * (index + 1);
            
            // Floating animation
            obj.position.y = this.archetypos[index].position.y + Math.sin(Date.now() * 0.001 + index) * 0.2;
        });
        
        // Camera orbit
        if (this.isRunning) {
            const time = Date.now() * 0.0005;
            this.camera.position.x = Math.cos(time) * 8;
            this.camera.position.z = Math.sin(time) * 8;
            this.camera.lookAt(0, 0, 0);
        }
        
        this.renderer.render(this.scene, this.camera);
    }

    onWindowResize() {
        const container = document.getElementById(this.containerId);
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        if (this.audioContext) {
            this.audioContext.close();
        }
        
        this.isRunning = false;
    }
}

// CSS Styles for the component
const diagnosticStyles = `
<style>
.diagnostic-ui {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    font-family: 'Inter', sans-serif;
    color: #fff;
}

.diagnostic-ui > * {
    pointer-events: auto;
}

.ui-header {
    position: absolute;
    top: 20px;
    left: 20px;
    right: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0, 0, 0, 0.8);
    padding: 15px 25px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(4, 217, 255, 0.3);
}

.ui-header h2 {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, #04D9FF, #00AEEF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.vigent-index {
    text-align: right;
}

.vigent-index span {
    display: block;
    font-size: 12px;
    color: #9CA3AF;
    margin-bottom: 4px;
}

.index-value {
    font-size: 32px;
    font-weight: 800;
    color: #04D9FF;
    text-shadow: 0 0 20px rgba(4, 217, 255, 0.5);
}

.archetypos-panel {
    position: absolute;
    bottom: 120px;
    left: 20px;
    right: 20px;
    display: flex;
    gap: 15px;
    justify-content: center;
}

.archetype-card {
    background: rgba(0, 0, 0, 0.8);
    padding: 15px;
    border-radius: 10px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    cursor: pointer;
    min-width: 200px;
}

.archetype-card:hover,
.archetype-card.active {
    border-color: #04D9FF;
    box-shadow: 0 0 20px rgba(4, 217, 255, 0.3);
    transform: translateY(-5px);
}

.archetype-name {
    font-weight: 600;
    margin-bottom: 8px;
    font-size: 14px;
}

.risk-meter {
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 8px;
}

.risk-bar {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}

.symptoms {
    font-size: 11px;
    color: #9CA3AF;
}

.controls {
    position: absolute;
    bottom: 60px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 12px;
}

.demo-btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
}

.demo-btn:not(.secondary) {
    background: linear-gradient(135deg, #04D9FF, #00AEEF);
    color: #000;
}

.demo-btn.secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.demo-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(4, 217, 255, 0.3);
}

.status-bar {
    position: absolute;
    bottom: 20px;
    left: 20px;
    right: 20px;
    background: rgba(0, 0, 0, 0.8);
    padding: 12px 20px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.processing {
    font-size: 12px;
    color: #9CA3AF;
    margin-bottom: 8px;
}

.progress-bar {
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
}

.progress {
    height: 100%;
    background: linear-gradient(90deg, #04D9FF, #00AEEF);
    border-radius: 2px;
    transition: width 0.5s ease;
    width: 0%;
}

.results-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(10px);
}

.results-content {
    background: rgba(17, 24, 39, 0.95);
    padding: 40px;
    border-radius: 20px;
    border: 1px solid rgba(4, 217, 255, 0.3);
    text-align: center;
    max-width: 400px;
}

.results-content h3 {
    margin: 0 0 30px 0;
    font-size: 28px;
    font-weight: 700;
    color: #04D9FF;
}

.key-insights {
    display: flex;
    justify-content: space-around;
    margin-bottom: 30px;
}

.insight {
    text-align: center;
}

.insight .metric {
    display: block;
    font-size: 32px;
    font-weight: 800;
    color: #04D9FF;
    margin-bottom: 5px;
}

.insight .label {
    font-size: 12px;
    color: #9CA3AF;
}

@media (max-width: 768px) {
    .archetypos-panel {
        flex-direction: column;
        bottom: 140px;
    }
    
    .archetype-card {
        min-width: auto;
    }
    
    .key-insights {
        flex-direction: column;
        gap: 20px;
    }
}
</style>
`;

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DiagnosticDemo, diagnosticStyles };
} else {
    window.DiagnosticDemo = DiagnosticDemo;
    window.diagnosticStyles = diagnosticStyles;
}