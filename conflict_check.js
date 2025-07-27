const fs = require('fs');

console.log('🔍 VERIFICACIÓN DE CONFLICTOS - geminidiagnostico.html\n');

// Leer el archivo
const content = fs.readFileSync('geminidiagnostico.html', 'utf8');

// Buscar marcadores de conflicto reales
const conflictMarkers = [
    '<<<<<<< HEAD',
    '<<<<<<< ',
    '=======',
    '>>>>>>> ',
    '>>>>>>> main',
    '>>>>>>> hombrevigente'
];

let conflictsFound = 0;
const lines = content.split('\n');

conflictMarkers.forEach(marker => {
    lines.forEach((line, index) => {
        if (line.trim() === marker || line.includes(marker)) {
            // Verificar que no sea un comentario decorativo
            if (!line.includes('//') || marker.includes('<<<<') || marker.includes('>>>>')) {
                console.log(`❌ CONFLICTO encontrado en línea ${index + 1}: ${line.trim()}`);
                conflictsFound++;
            }
        }
    });
});

// Verificar optimizaciones móviles
const mobileOptimizations = [
    { name: 'Container responsivo', pattern: /height: 60vh/ },
    { name: 'Grid mobile-first', pattern: /\.demo-grid/ },
    { name: 'Touch events', pattern: /touchstart/ },
    { name: 'Media queries móvil', pattern: /@media \(max-width: 768px\)/ },
    { name: 'Variables let (no const)', pattern: /let scene, camera, renderer/ }
];

console.log('\n✅ VERIFICACIÓN DE OPTIMIZACIONES MÓVILES:');
mobileOptimizations.forEach(opt => {
    const found = opt.pattern.test(content);
    console.log(`${found ? '✅' : '❌'} ${opt.name}: ${found ? 'PRESENTE' : 'FALTANTE'}`);
});

console.log(`\n📊 RESUMEN:`);
console.log(`• Conflictos encontrados: ${conflictsFound}`);
console.log(`• Archivo total líneas: ${lines.length}`);
console.log(`• Optimizaciones móviles: ${mobileOptimizations.filter(opt => opt.pattern.test(content)).length}/${mobileOptimizations.length}`);

if (conflictsFound === 0) {
    console.log('\n🎉 NO HAY CONFLICTOS - El archivo está listo para commit');
} else {
    console.log('\n⚠️  HAY CONFLICTOS QUE NECESITAN RESOLUCIÓN MANUAL');
}