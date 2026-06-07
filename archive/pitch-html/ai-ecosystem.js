/**
 * HOMBRE VIGENTE AI ECOSYSTEM - BLUEPRINT COMPLETO
 * =================================================
 * 
 * Extracción completa de TODA la riqueza técnica identificada en el análisis de Cursor
 * Fuentes: vision-board.html, playbook.html, ecosistema.html, mvtech.html, SSOTtech.html
 * 
 * Este archivo contiene la arquitectura completa del ecosistema de IA,
 * datos de configuración, stack tecnológico, y toda la lógica de negocio
 * extraída de los 5 archivos HTML analizados.
 */

// ========================================
// VISION BOARD - DATA FLYWHEEL INTERACTIVO
// ========================================

const DATA_FLYWHEEL_CONFIG = {
    // Grid 5x4 con centro SSOT BigQuery (extraído de vision-board.html)
    grid: {
        columns: 5,
        rows: 4,
        centerPosition: { column: '2 / 5', row: '2 / 4' }
    },
    
    // Centro del flywheel - SSOT
    center: {
        id: 'flywheel-ssot',
        name: 'SSOT',
        description: 'BigQuery',
        fullName: 'Single Source of Truth',
        details: 'Nuestra Única Fuente de Verdad (Single Source of Truth) en BigQuery. Centraliza todos los datos procesados y enriquecidos, sirviendo como el núcleo para todos los agentes de IA.'
    },

    // Componentes externos (fuentes de datos)
    externalSources: [
        {
            id: 'flywheel-booksy',
            name: 'Booksy',
            type: 'Externa',
            position: { column: '1 / 2', row: '1 / 2' },
            borderColor: 'border-blue-500',
            description: 'Sistema de reservas que genera eventos de citas, cancelaciones y no-shows. Es una fuente primaria de datos de demanda del cliente.'
        },
        {
            id: 'flywheel-quickbooks',
            name: 'QuickBooks',
            type: 'Externa', 
            position: { column: '2 / 3', row: '1 / 2' },
            borderColor: 'border-blue-500',
            description: 'Plataforma contable que emite webhooks de transacciones financieras, alimentando a RiskGuard AI para el análisis de salud financiera en tiempo real.'
        },
        {
            id: 'flywheel-stripe',
            name: 'Stripe',
            type: 'Externa',
            position: { column: '3 / 4', row: '1 / 2' },
            borderColor: 'border-blue-500',
            description: 'Pasarela de pagos que procesa transacciones y genera eventos de pago, esenciales para el seguimiento de ingresos y la gestión de suscripciones.'
        },
        {
            id: 'flywheel-fotofinder',
            name: 'FotoFinder',
            type: 'Externa',
            position: { column: '4 / 5', row: '1 / 2' },
            borderColor: 'border-blue-500',
            description: 'Dispositivo de diagnóstico 3D y térmico. Provee los datos crudos para que DiagnósticoVigente AI genere el Índice de Vigencia.'
        }
    ],

    // Event Bus
    eventBus: {
        id: 'flywheel-bus',
        name: 'Event Bus',
        type: 'Externa',
        position: { column: '5 / 6', row: '1 / 5' },
        borderColor: 'border-gray-500',
        description: 'Bus de mensajería (Kafka/Pub-Sub) que recibe todos los eventos de las fuentes externas y los distribuye a los consumidores internos de forma desacoplada y escalable.'
    },

    // Agentes de IA internos
    internalAgents: [
        {
            id: 'flywheel-optivigente',
            name: 'OptiVigente',
            type: 'Interna',
            position: { column: '1 / 2', row: '2 / 3' },
            borderColor: 'border-green-500',
            description: 'Agente de optimización. Consume datos de demanda para ajustar precios dinámicamente, optimizar la agenda y gestionar la utilización de recursos.'
        },
        {
            id: 'flywheel-riskguard',
            name: 'RiskGuard',
            type: 'Interna',
            position: { column: '1 / 2', row: '3 / 4' },
            borderColor: 'border-green-500',
            description: 'Agente de supervisión financiera. Analiza datos de QuickBooks y Stripe para simular riesgos, calcular el Z-Score y emitir alertas, protegiendo la rentabilidad.'
        },
        {
            id: 'flywheel-personavigente',
            name: 'PersonaVigente',
            type: 'Interna',
            position: { column: '5 / 6', row: '2 / 3' },
            borderColor: 'border-green-500',
            description: 'Agente de hiperpersonalización. Utiliza datos de diagnóstico y comportamiento para segmentar clientes, calcular propensión al churn y personalizar ofertas.'
        },
        {
            id: 'flywheel-chatvigente',
            name: 'ChatVigente',
            type: 'Interna',
            position: { column: '5 / 6', row: '3 / 4' },
            borderColor: 'border-green-500',
            description: 'Agente conversacional que interactúa con los clientes para reservas, soporte y campañas de retención, utilizando la inteligencia de otros agentes.'
        }
    ],

    // Outputs del sistema
    outputs: [
        {
            id: 'flywheel-bi',
            name: 'BI / Dashboards',
            type: 'Externa',
            position: { column: '2 / 3', row: '4 / 5' },
            borderColor: 'border-purple-500',
            description: 'Herramientas como Looker o Tableau que se conectan a la SSOT para generar visualizaciones y reportes para la toma de decisiones humana.'
        },
        {
            id: 'flywheel-app',
            name: 'App Cliente',
            type: 'Externa',
            position: { column: '3 / 4', row: '4 / 5' },
            borderColor: 'border-purple-500',
            description: 'La aplicación móvil o web para el cliente, que presenta ofertas personalizadas, permite agendar y muestra resultados, cerrando el ciclo del flywheel.'
        }
    ]
};

// CSS Animations para el flywheel
const FLYWHEEL_ANIMATIONS = {
    spin: `
        @keyframes spin {
            from { transform: rotate(0deg) translateX(150px) rotate(0deg); }
            to { transform: rotate(360deg) translateX(150px) rotate(-360deg); }
        }
        @keyframes spin-reverse {
            from { transform: rotate(0deg); }
            to { transform: rotate(-360deg); }
        }
    `,
    delays: ['-4s', '-8s', '-12s', '-16s', '-20s']
};

// ========================================
// DASHBOARD NORTH STAR - KPIs EN TIEMPO REAL
// ========================================

const NORTH_STAR_DASHBOARD = {
    kpis: [
        {
            name: 'Ventas',
            value: '$4.1M',
            unit: 'MXN',
            period: 'Mes Actual',
            icon: '📈',
            status: 'good'
        },
        {
            name: 'Visitas',
            value: '425',
            unit: 'Clientes/mes',
            location: 'CDMX',
            icon: '👥',
            status: 'good'
        },
        {
            name: 'Valor Cliente (LTV)',
            value: '$71.5k',
            archetype: 'Pedro',
            icon: '💎',
            status: 'excellent'
        },
        {
            name: 'Vitalidad Financiera',
            value: '49%',
            metric: 'EBITDA %',
            location: 'CDMX',
            icon: '💪',
            status: 'excellent'
        }
    ],

    // RiskGuard AI Semáforo interactivo
    riskGuard: {
        states: {
            verde: {
                status: 'Normal',
                color: 'bg-green-500',
                description: 'Altman Z-Score > 2.9. El negocio opera dentro de los parámetros de seguridad. Crecimiento y optimización activados.',
                probability: 0.05,
                score: 2.9
            },
            amarillo: {
                status: 'Alerta',
                color: 'bg-yellow-500',
                description: 'Altman Z-Score 1.8-2.9. Desviación moderada. Se limitan descuentos agresivos.',
                probability: 0.15,
                score: 2.1
            },
            rojo: {
                status: 'Crítico',
                color: 'bg-red-500',
                description: 'Altman Z-Score < 1.8. Riesgo significativo. Se bloquean descuentos.',
                probability: 0.25,
                score: 1.5
            }
        },
        currentState: 'verde'
    }
};

// ========================================
// CUSTOMER ARCHETYPES - PERSONAVIGENTE AI
// ========================================

const CUSTOMER_ARCHETYPES = [
    {
        tipo: 'Carlos (Rejuvenecedor)',
        ticket: 23400,
        ltv: 43000,
        ltv_cac: 17.2,
        ageRange: '30-40',
        profile: 'Profesional joven enfocado en prevención y mantenimiento'
    },
    {
        tipo: 'Pedro (Definido)',
        ticket: 59100,
        ltv: 71500,
        ltv_cac: 23.8,
        ageRange: '41-50',
        profile: 'Ejecutivo maduro con alto poder adquisitivo, busca resultados visibles'
    },
    {
        tipo: 'Luis (Renovado)',
        ticket: 12400,
        ltv: 21800,
        ltv_cac: 12.1,
        ageRange: '51-60',
        profile: 'Profesional senior, enfoque en bienestar y comunidad'
    }
];

// ========================================
// STACK TECNOLÓGICO COMPLETO
// ========================================

const TECH_STACK = [
    // Agentes IA Internos
    {
        name: 'DiagnósticoVigente AI',
        type: 'Interna',
        domain: 'Diagnóstico & Personalización',
        description: 'Análisis 3D+térmico, cálculo del Índice de Vigencia, propuesta de plan.',
        tech: ['CNN', 'XGBoost', 'Computer Vision'],
        dependencies: ['FotoFinder', 'SSOT BigQuery']
    },
    {
        name: 'PersonaVigente AI',
        type: 'Interna',
        domain: 'Diagnóstico & Personalización',
        description: 'Recomendaciones hiperpersonalizadas, motor de perfiles y propensión a comprar.',
        tech: ['LightFM', 'Qdrant (Vector DB)', 'Feast (Feature Store)', 'GPT-4o'],
        dependencies: ['SSOT BigQuery', 'Customer Events']
    },
    {
        name: 'OptiVigente AI',
        type: 'Interna',
        domain: 'Operaciones & Scheduling',
        description: 'Predicción de demanda, optimización de turnos y pricing dinámico.',
        tech: ['TensorFlow', 'Prophet', 'OR-Tools', 'MILP'],
        dependencies: ['Booksy', 'SSOT BigQuery']
    },
    {
        name: 'RiskGuard AI',
        type: 'Interna',
        domain: 'Finanzas & Riesgo',
        description: 'Simulaciones Monte Carlo, Altman Z-Score, alertas de desviación y quiebra.',
        tech: ['Python', 'NumPy', 'SciPy', 'Altman Z-Score'],
        dependencies: ['QuickBooks', 'Stripe', 'SSOT BigQuery']
    },
    {
        name: 'ChatVigente AI (LLM)',
        type: 'Interna',
        domain: 'Atención al Cliente',
        description: 'Chatbot multicanal (WhatsApp, web), reservas, FAQs y soporte automatizado.',
        tech: ['LLM (GPT-4o mini)', 'RAG', 'Dialogflow CX', 'Twilio API'],
        dependencies: ['PersonaVigente AI', 'OptiVigente AI']
    },
    {
        name: 'AssetVigente Predictive Mx',
        type: 'Interna',
        domain: 'Mantenimiento',
        description: 'Agente de mantenimiento predictivo. Usa datos de sensores IoT para predecir fallos en equipos críticos.',
        tech: ['Series Temporales', 'InfluxDB', 'IoT Sensors'],
        dependencies: ['Equipment Sensors', 'SSOT BigQuery']
    },
    {
        name: 'Virtual Try-On GAN',
        type: 'Interna',
        domain: 'Visualización',
        description: 'Crea simulaciones "antes y después" con GANs para gestionar expectativas y aumentar la conversión.',
        tech: ['GANs', 'Computer Vision', 'StyleGAN'],
        dependencies: ['FotoFinder', 'DiagnósticoVigente AI']
    },

    // Herramientas Externas
    {
        name: 'Kafka / Pub-Sub',
        type: 'Externa',
        domain: 'Operaciones & Scheduling',
        description: 'Bus de eventos para trigger de recalculos en tiempo real.',
        tech: ['Apache Kafka', 'Google Pub/Sub'],
        dependencies: []
    },
    {
        name: 'Google Dataflow / Flink',
        type: 'Externa',
        domain: 'Operaciones & Scheduling',
        description: 'Procesamiento streaming de eventos de reservas y transacciones.',
        tech: ['Apache Flink', 'Google Dataflow'],
        dependencies: ['Kafka/Pub-Sub']
    },
    {
        name: 'QuickBooks AI',
        type: 'Externa',
        domain: 'Finanzas & Riesgo',
        description: 'Reportes automáticos P&L y flujo de caja.',
        tech: ['QuickBooks API', 'Webhooks'],
        dependencies: []
    },
    {
        name: 'Dialogflow CX / ManyChat',
        type: 'Externa',
        domain: 'Atención al Cliente',
        description: 'Framework de chatbots para WhatsApp, Instagram, Facebook.',
        tech: ['Dialogflow CX', 'ManyChat', 'Twilio'],
        dependencies: []
    },
    {
        name: 'MLflow',
        type: 'Externa',
        domain: 'MLOps & Gobernanza',
        description: 'Tracking, versionado y despliegue de modelos.',
        tech: ['MLflow', 'Model Registry', 'Experiment Tracking'],
        dependencies: []
    },
    {
        name: 'BigQuery / Snowflake',
        type: 'Externa',
        domain: 'Almacenamiento & BI',
        description: 'Data lakehouse único (SSOT) financiero y operativo.',
        tech: ['Google BigQuery', 'Snowflake'],
        dependencies: []
    },
    {
        name: 'Looker / Tableau',
        type: 'Externa',
        domain: 'Almacenamiento & BI',
        description: 'Dashboards interactivos y reportes analíticos.',
        tech: ['Looker', 'Tableau', 'Data Studio'],
        dependencies: ['BigQuery']
    },
    {
        name: 'Stripe México',
        type: 'Externa',
        domain: 'Pasarelas de Pago',
        description: 'Cobros locales e internacionales y gestión de suscripciones.',
        tech: ['Stripe API', 'Webhooks', 'Payment Processing'],
        dependencies: []
    }
];

// ========================================
// PLAYBOOKS DE ORQUESTACIÓN AUTOMATIZADA
// ========================================

const ORCHESTRATION_PLAYBOOKS = [
    {
        id: 'low-occupancy',
        title: "Gestión de Baja Ocupación (<80%)",
        description: "Flujo automatizado para estimular demanda cuando la utilización cae por debajo del 80%",
        steps: [
            {
                step: 1,
                name: "Detectar Caída",
                actor: "OptiVigente AI",
                type: "Interna",
                action: "Detecta utilización < 80% y calcula un descuento dinámico",
                technical: "Monitor de métricas en tiempo real desde SSOT BigQuery"
            },
            {
                step: 2,
                name: "Calcular Descuento Dinámico",
                actor: "OptiVigente AI",
                type: "Interna", 
                action: "Calcula descuento óptimo basado en elasticidad de precios y ocupación",
                technical: "Algoritmo de optimización con restricciones de margen mínimo"
            },
            {
                step: 3,
                name: "Validar Riesgo",
                actor: "RiskGuard AI",
                type: "Interna",
                action: "Valida que el descuento no comprometa márgenes críticos",
                technical: "Simulación Monte Carlo de impacto en P&L"
            },
            {
                step: 4,
                name: "Segmentar Clientes",
                actor: "PersonaVigente AI", 
                type: "Interna",
                action: "Selecciona clientes con mayor propensión a aceptar ofertas",
                technical: "Scoring de propensión basado en historial y comportamiento"
            },
            {
                step: 5,
                name: "Enviar Oferta Flash",
                actor: "ChatVigente AI",
                type: "Interna",
                action: "Construye mensaje personalizado y envía vía WhatsApp",
                technical: "Integración con Twilio API para envío masivo"
            },
            {
                step: 6,
                name: "Cliente Reserva",
                actor: "Booksy",
                type: "Externa",
                action: "Cliente realiza reserva que actualiza disponibilidad",
                technical: "Webhook de Booksy actualiza SSOT en tiempo real"
            },
            {
                step: 7,
                name: "Ocupación Recuperada",
                actor: "Sistema",
                type: "Outcome",
                action: "Utilización vuelve a niveles óptimos (≥80%)",
                technical: "Métricas actualizadas en dashboard North Star"
            }
        ],
        estimatedDuration: "15-30 minutos",
        successRate: "85%",
        avgOccupancyIncrease: "12-18%"
    },
    {
        id: 'churn-management',
        title: "Gestión de Riesgo de Churn (>0.6 CPS)",
        description: "Intervención automática para retener clientes con alto riesgo de abandono",
        steps: [
            {
                step: 1,
                name: "Calcular CPS",
                actor: "PersonaVigente AI",
                type: "Interna",
                action: "Detecta cliente con Churn Propensity Score > 0.60",
                technical: "Modelo de ML entrenado con datos históricos de comportamiento"
            },
            {
                step: 2,
                name: "Generar Oferta Personalizada",
                actor: "PersonaVigente AI",
                type: "Interna",
                action: "Crea oferta de retención basada en arquetipo del cliente",
                technical: "Sistema de recomendaciones con filtrado colaborativo"
            },
            {
                step: 3,
                name: "Optimizar Descuento",
                actor: "OptiVigente AI",
                type: "Interna",
                action: "Ajusta descuento óptimo basado en ocupación actual",
                technical: "Algoritmo de pricing dinámico con restricciones de margen"
            },
            {
                step: 4,
                name: "Enviar Oferta Retención",
                actor: "ChatVigente AI",
                type: "Interna",
                action: "Envía oferta personalizada por WhatsApp con CTA claro",
                technical: "Template engine con personalización dinámica"
            },
            {
                step: 5,
                name: "Actualizar Proyecciones",
                actor: "RiskGuard AI",
                type: "Interna",
                action: "Recalcula LTV proyectado y ajusta métricas financieras",
                technical: "Actualización de modelos de forecasting de ingresos"
            },
            {
                step: 6,
                name: "Riesgo Mitigado",
                actor: "Sistema",
                type: "Outcome",
                action: "CPS del cliente reducido, retención asegurada",
                technical: "Métricas de retención actualizadas en BI dashboards"
            }
        ],
        estimatedDuration: "5-10 minutos",
        successRate: "72%",
        avgChurnReduction: "45%"
    },
    {
        id: 'financial-integration',
        title: "Integración Financiera en Tiempo Real",
        description: "Pipeline automatizado para procesar transacciones financieras",
        steps: [
            {
                step: 1,
                name: "Factura Creada",
                actor: "QuickBooks",
                type: "Externa",
                action: "Nueva factura generada emite webhook automático",
                technical: "QuickBooks API webhook con payload JSON estructurado"
            },
            {
                step: 2,
                name: "Webhook a Event Bus",
                actor: "Pub/Sub",
                type: "Externa",
                action: "Evento capturado y distribuido a consumidores",
                technical: "Google Pub/Sub topic con múltiples suscriptores"
            },
            {
                step: 3,
                name: "Procesar y Cargar a SSOT",
                actor: "Dataflow",
                type: "Externa",
                action: "Procesamiento streaming hacia BigQuery",
                technical: "Apache Beam pipeline con transformaciones ETL"
            },
            {
                step: 4,
                name: "Recalcular Z-Score",
                actor: "RiskGuard AI",
                type: "Interna",
                action: "Actualiza métricas de salud financiera en tiempo real",
                technical: "Altman Z-Score recalculado con nuevos datos financieros"
            },
            {
                step: 5,
                name: "Actualizar Dashboard",
                actor: "Looker",
                type: "Externa",
                action: "Dashboards financieros reflejan estado actual",
                technical: "Queries automáticas a BigQuery con refresh en tiempo real"
            }
        ],
        estimatedDuration: "2-5 minutos",
        successRate: "99.5%",
        dataLatency: "< 30 segundos"
    }
];

// ========================================
// JOURNEY DEL CLIENTE EN 6 ETAPAS
// ========================================

const CUSTOMER_JOURNEY = [
    {
        stage: 1,
        title: "Descubrimiento Digital",
        description: "El primer contacto ocurre a través de contenido en redes sociales con un CTA para agendar un diagnóstico 3D gratuito.",
        icon: "🔍",
        aiAgent: "Contenido IA",
        touchpoints: ["Instagram", "LinkedIn", "Google Ads"],
        duration: "1-3 días",
        conversionRate: "12%",
        details: "Cliente impactado por contenido en redes (Reel 'antes/después'). CTA a 'Diagnóstico 3D Gratuito'."
    },
    {
        stage: 2,
        title: "Check-in & Escaneo 3D",
        description: "A su llegada, el cliente realiza un check-in rápido y se somete a un escaneo. Input para DiagnósticoVigente AI.",
        icon: "📱",
        aiAgent: "DiagnósticoVigente AI",
        touchpoints: ["FotoFinder", "Check-in Digital"],
        duration: "15 minutos",
        conversionRate: "95%",
        details: "Cliente llega, realiza check-in digital y pasa a escaneo 3D y térmico con FotoFinder (10 min)."
    },
    {
        stage: 3,
        title: "Plan PersonaVigente",
        description: "Inmediatamente, PersonaVigente AI genera un plan hiperpersonalizado que es presentado al cliente.",
        icon: "✨",
        aiAgent: "PersonaVigente AI",
        touchpoints: ["Plan Personalizado", "Simulación Visual"],
        duration: "10 minutos",
        conversionRate: "78%",
        details: "Recibe en 5 min un plan generado por PersonaVigente AI, basado en su 'Índice de Vigencia' objetivo."
    },
    {
        stage: 4,
        title: "Ejecución Tratamiento",
        description: "El cliente procede al tratamiento en una cabina asignada dinámicamente por OptiVigente AI.",
        icon: "💉",
        aiAgent: "OptiVigente AI",
        touchpoints: ["Cabina Asignada", "Tratamiento Clínico"],
        duration: "45-90 minutos",
        conversionRate: "100%",
        details: "La cita se ejecuta en una cabina asignada dinámicamente por OptiVigente AI para máxima eficiencia."
    },
    {
        stage: 5,
        title: "Seguimiento",
        description: "Se guía al cliente en su recuperación y se agenda la siguiente cita, a menudo de forma automática vía ChatVigente AI.",
        icon: "📅",
        aiAgent: "ChatVigente AI",
        touchpoints: ["WhatsApp", "Seguimiento Post-Tratamiento"],
        duration: "7-14 días",
        conversionRate: "85%",
        details: "Recibe instrucciones post-procedimiento y seguimiento por WhatsApp, gestionado por ChatVigente AI."
    },
    {
        stage: 6,
        title: "Comunidad",
        description: "Se invita al cliente a eventos educativos exclusivos para fomentar la lealtad y el engagement.",
        icon: "🤝",
        aiAgent: "PersonaVigente AI",
        touchpoints: ["CLUB Membership", "Eventos Exclusivos"],
        duration: "Ongoing",
        conversionRate: "65%",
        details: "Invitado a unirse al 'CLUB'. PersonaVigente AI envía ofertas de renovación en el momento oportuno."
    }
];

// ========================================
// PLAYBOOK TÉCNICO - DESARROLLO Y DATOS
// ========================================

const DEVELOPMENT_SPECIFICATIONS = {
    // Cuantificación específica de horas de desarrollo
    development: {
        NUM_CUSTOMERS: 5000,
        estimatedHours: {
            min: 40,
            max: 60,
            riskGuardMonteCarlo: {
                min: 80,
                max: 120,
                includesTesting: true
            }
        }
    },

    // Generador de datos sintéticos
    dataGenerator: {
        language: "Python",
        libraries: ["pandas", "numpy", "faker", "sdv", "uuid"],
        customerCount: 5000,
        locale: "es_MX",
        ageDistribution: {
            "30-40": 0.45,
            "41-50": 0.40,
            "51-60": 0.15
        },
        incomeDistribution: {
            mean: "np.log(800000)",
            sigma: 0.5,
            currency: "MXN"
        }
    },

    // Contrato de datos FotoFinderScanEvent_v1
    dataContracts: {
        FotoFinderScanEvent_v1: {
            schema: "http://json-schema.org/draft-07/schema#",
            title: "FotoFinderScanEvent_v1",
            type: "object",
            properties: {
                patient_id: { type: "string" },
                scan_id: { type: "string", format: "uuid" },
                scan_type: { enum: ["meesma-2", "skeen"] },
                timestamp: { type: "string", format: "date-time" },
                scan_data: { type: "object" },
                vigencia_index: { type: "number", minimum: 0, maximum: 100 }
            },
            required: ["patient_id", "scan_id", "timestamp"]
        },

        // Tabla de hechos central
        fact_event: {
            columns: [
                "event_id (UUID, PK)",
                "customer_id (UUID, FK)",
                "event_type (VARCHAR)",
                "event_timestamp (TIMESTAMP)",
                "source_system (VARCHAR)",
                "payload (JSONB)",
                "schema_version (VARCHAR)",
                "event_value (NUMERIC)"
            ]
        },

        // Webhook Payload Stripe completo
        stripeWebhook: {
            id: "evt_1P8x...",
            object: "event",
            type: "charge.succeeded",
            data: {
                object: {
                    id: "ch_3P8x...",
                    amount: 400000,
                    currency: "mxn",
                    customer: "cus_Q7i...",
                    metadata: {
                        appointment_id: "appt_456",
                        service_type: "hifu_facial",
                        clinic_location: "cdmx_centro"
                    }
                }
            }
        }
    },

    // Plantilla Dockerfile para despliegue por agente
    dockerTemplate: `
        # Usar una imagen base ligera de Python
        FROM python:3.10-slim

        # Establecer el directorio de trabajo
        WORKDIR /app

        # Copiar dependencias e instalarlas
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        # Copiar el código de la aplicación
        COPY . .

        # Exponer el puerto y ejecutar la aplicación
        EXPOSE 8000
        CMD ["python", "app.py"]
    `,

    // Reglas de calidad de datos (Great Expectations)
    dataQualityRules: {
        booksy_appointments_suite: {
            name: "booksy_appointments_suite",
            expectations: [
                {
                    expectation_type: "expect_column_to_exist",
                    kwargs: { column: "service_id" },
                    meta: { notes: "CRITICAL: 'service_id' es esencial para OptiVigente." }
                },
                {
                    expectation_type: "expect_column_values_to_not_be_null",
                    kwargs: { column: "customer_id" },
                    meta: { notes: "CRITICAL: Citas sin 'customer_id' rompen los modelos LTV." }
                },
                {
                    expectation_type: "expect_column_values_to_be_in_set",
                    kwargs: {
                        column: "status",
                        value_set: ["completed", "cancelled", "no-show"]
                    }
                }
            ]
        }
    }
};

// ========================================
// ROADMAP TÉCNICO POR FASES
// ========================================

const TECHNICAL_ROADMAP = {
    phase1: {
        period: "2025-2027",
        title: "Validación y Perfeccionamiento",
        market: "CDMX, Guadalajara",
        objectives: [
            "Validar P&L y Data Flywheel",
            "Perfeccionar agentes de IA",
            "Establecer SSOT en BigQuery",
            "Implementar RiskGuard AI completo"
        ],
        technicalMilestones: [
            "Implementación completa del Data Flywheel",
            "7 agentes de IA operacionales",
            "Integración completa con Booksy, Stripe, QuickBooks",
            "Dashboard North Star en tiempo real",
            "Simulaciones Monte Carlo operativas"
        ],
        regulatoryGate: "COFEPRIS",
        estimatedInvestment: "$2.5M USD"
    },
    phase2: {
        period: "2027-2028",
        title: "Expansión EE.UU.",
        market: "Miami, Los Angeles",
        objectives: [
            "Adaptar a regulación FDA",
            "Captar comunidad latina",
            "Escalar infraestructura cloud",
            "Optimizar para ticket más alto"
        ],
        technicalMilestones: [
            "Compliance FDA 510(k)",
            "Multi-region deployment",
            "Localización de agentes de IA",
            "Integración con sistemas de salud US"
        ],
        regulatoryGate: "FDA 510(k)",
        estimatedInvestment: "$5M USD"
    },
    phase3: {
        period: "2029-2030",
        title: "Licenciamiento Europa",
        market: "Madrid, Londres",
        objectives: [
            "Licenciar 'Clinic-in-a-Box' como SaaS",
            "Cumplir con MDR de la UE",
            "Modelo de franquicia tecnológica",
            "Revenue streams recurrentes"
        ],
        technicalMilestones: [
            "Plataforma SaaS completa",
            "API ecosystem para partners",
            "Compliance GDPR y MDR",
            "White-label solutions"
        ],
        regulatoryGate: "MDR (EU)",
        estimatedInvestment: "$8M USD"
    }
};

// ========================================
// ECOSISTEMA COMPLETO - 7 AGENTES IA
// ========================================

const AI_AGENTS_ECOSYSTEM = [
    {
        name: 'DiagnósticoVigente AI',
        icon: '👁️',
        category: 'Clinical Intelligence',
        description: 'Analiza escaneos 3D/térmicos, calcula el "Índice de Vigencia" y propone un plan de tratamiento inicial.',
        technicalStack: {
            core: ['CNN', 'XGBoost', 'Computer Vision'],
            frameworks: ['TensorFlow', 'OpenCV', 'Scikit-learn'],
            infrastructure: ['Google Cloud AI Platform', 'Vertex AI']
        },
        inputs: ['FotoFinder 3D scans', 'Thermal imaging', 'Patient history'],
        outputs: ['Vigencia Index (0-100)', 'Treatment recommendations', 'Risk assessment'],
        performance: {
            accuracy: '94%',
            processingTime: '< 30 seconds',
            uptime: '99.9%'
        }
    },
    {
        name: 'PersonaVigente AI',
        icon: '👤',
        category: 'Customer Intelligence',
        description: 'Motor de hiperpersonalización. Segmenta clientes, calcula propensión a compra y riesgo de churn (CPS).',
        technicalStack: {
            core: ['LightFM', 'Collaborative Filtering', 'GPT-4o'],
            frameworks: ['Qdrant (Vector DB)', 'Feast (Feature Store)'],
            infrastructure: ['BigQuery ML', 'Vertex AI Matching Engine']
        },
        inputs: ['Customer behavior', 'Transaction history', 'Treatment outcomes'],
        outputs: ['Churn Propensity Score', 'Personalized offers', 'Customer segments'],
        performance: {
            churnPredictionAccuracy: '87%',
            personalizationLift: '+23%',
            responseTime: '< 100ms'
        }
    },
    {
        name: 'OptiVigente AI',
        icon: '⚙️',
        category: 'Operations Intelligence',
        description: 'Cerebro operativo. Maximiza utilización de recursos (≥80%) con predicción de demanda y pricing dinámico.',
        technicalStack: {
            core: ['Prophet', 'OR-Tools', 'MILP'],
            frameworks: ['TensorFlow', 'Apache Beam'],
            infrastructure: ['Google Cloud Scheduler', 'Cloud Functions']
        },
        inputs: ['Booking patterns', 'Resource availability', 'Market demand'],
        outputs: ['Dynamic pricing', 'Optimal scheduling', 'Resource allocation'],
        performance: {
            utilizationTarget: '≥80%',
            pricingAccuracy: '91%',
            scheduleOptimization: '+15% efficiency'
        }
    },
    {
        name: 'RiskGuard AI',
        icon: '🛡️',
        category: 'Financial Intelligence',
        description: 'Guardián financiero. Simula escenarios, calcula el Altman Z-Score y actúa como "freno" para mitigar riesgos.',
        technicalStack: {
            core: ['Monte Carlo Simulation', 'Altman Z-Score', 'NumPy'],
            frameworks: ['SciPy', 'Pandas', 'Statsmodels'],
            infrastructure: ['Cloud Functions', 'BigQuery', 'Pub/Sub']
        },
        inputs: ['Financial data', 'Cash flow', 'P&L statements'],
        outputs: ['Risk alerts', 'Z-Score', 'Scenario simulations'],
        performance: {
            riskDetectionAccuracy: '96%',
            falsePositiveRate: '< 3%',
            simulationSpeed: '10,000 scenarios/min'
        }
    },
    {
        name: 'ChatVigente AI',
        icon: '💬',
        category: 'Conversational Intelligence',
        description: 'Interfaz conversacional multicanal. Gestiona reservas, flujos de retención y comunicación de ofertas.',
        technicalStack: {
            core: ['GPT-4o mini', 'RAG', 'NLU'],
            frameworks: ['Dialogflow CX', 'Langchain'],
            infrastructure: ['Twilio API', 'WhatsApp Business API']
        },
        inputs: ['Customer queries', 'Booking requests', 'Support tickets'],
        outputs: ['Automated responses', 'Booking confirmations', 'Retention campaigns'],
        performance: {
            responseAccuracy: '92%',
            bookingConversion: '+18%',
            customerSatisfaction: '4.6/5'
        }
    },
    {
        name: 'AssetVigente Predictive Mx',
        icon: '🔧',
        category: 'Asset Intelligence',
        description: 'Agente de mantenimiento predictivo. Usa datos de sensores IoT para predecir fallos en equipos críticos.',
        technicalStack: {
            core: ['Time Series Analysis', 'Anomaly Detection'],
            frameworks: ['InfluxDB', 'Grafana', 'Apache Kafka'],
            infrastructure: ['IoT Core', 'Cloud IoT', 'Edge Computing']
        },
        inputs: ['Sensor data', 'Equipment logs', 'Maintenance history'],
        outputs: ['Failure predictions', 'Maintenance schedules', 'Cost optimization'],
        performance: {
            predictionAccuracy: '89%',
            downtimeReduction: '-35%',
            maintenanceCostSaving: '-22%'
        }
    },
    {
        name: 'Virtual Try-On GAN',
        icon: '✨',
        category: 'Visual Intelligence',
        description: 'Crea simulaciones "antes y después" con GANs para gestionar expectativas y aumentar la conversión.',
        technicalStack: {
            core: ['StyleGAN', 'Computer Vision', 'Deep Learning'],
            frameworks: ['PyTorch', 'OpenCV', 'CUDA'],
            infrastructure: ['GPU clusters', 'Vertex AI', 'Cloud Storage']
        },
        inputs: ['3D scans', 'Treatment parameters', 'Historical outcomes'],
        outputs: ['Before/after simulations', 'Realistic previews', 'Expectation management'],
        performance: {
            visualAccuracy: '93%',
            conversionIncrease: '+28%',
            customerSatisfaction: '4.8/5'
        }
    }
];

// ========================================
// CLINIC LAYOUT OPTIMIZADO (250 m²)
// ========================================

const CLINIC_LAYOUT_DATA = [
    {
        area: 'Rejuvenecimiento Facial',
        span: 'col-span-1 row-span-1',
        percentage: '20%',
        size: '50 m²',
        equipment: ['HIFU Ultraformer III', 'Botox station', 'Consultation area']
    },
    {
        area: 'Cirugía Ambulatoria',
        span: 'col-span-1 row-span-1',
        percentage: '15%',
        size: '37.5 m²',
        equipment: ['Surgical suite', 'Recovery area', 'Sterilization']
    },
    {
        area: 'Dental',
        span: 'col-span-1 row-span-1',
        percentage: '12%',
        size: '30 m²',
        equipment: ['Dental chair', 'X-ray', 'Sterilization unit']
    },
    {
        area: 'Sala "CLUB"',
        span: 'col-span-2 row-span-1',
        percentage: '20%',
        size: '50 m²',
        equipment: ['Meeting space', 'Educational area', 'Networking zone']
    },
    {
        area: 'Depilación y Corporal',
        span: 'col-span-1 row-span-1',
        percentage: '15%',
        size: '37.5 m²',
        equipment: ['Laser hair removal', 'Body treatments', 'Changing rooms']
    },
    {
        area: 'Grooming Básico',
        span: 'col-span-1 row-span-1',
        percentage: '12%',
        size: '30 m²',
        equipment: ['Barber stations', 'Skincare area', 'Product display']
    },
    {
        area: 'Soporte y Almacén',
        span: 'col-span-2 row-span-1',
        percentage: '6%',
        size: '15 m²',
        equipment: ['Storage', 'Staff area', 'Utilities']
    }
];

// ========================================
// STAFFING DATA - ESTRUCTURA ORGANIZACIONAL LEAN
// ========================================

const STAFFING_DATA = [
    {
        role: 'COO / Médico Responsable',
        fte: 1,
        responsibilities: ['Operations oversight', 'Medical supervision', 'Regulatory compliance'],
        aiAugmentation: ['RiskGuard alerts', 'OptiVigente insights', 'Performance dashboards']
    },
    {
        role: 'Coordinador de Comunidad',
        fte: 1,
        responsibilities: ['CLUB management', 'Customer engagement', 'Event coordination'],
        aiAugmentation: ['PersonaVigente insights', 'ChatVigente automation', 'Customer journey optimization']
    },
    {
        role: 'Técnicos Estéticos',
        fte: 3,
        responsibilities: ['Treatment delivery', 'Equipment operation', 'Patient care'],
        aiAugmentation: ['DiagnósticoVigente guidance', 'AssetVigente maintenance alerts', 'Virtual Try-On demonstrations']
    },
    {
        role: 'Dentista',
        fte: 0.5,
        responsibilities: ['Dental treatments', 'Oral health assessments', 'Treatment planning'],
        aiAugmentation: ['DiagnósticoVigente integration', 'OptiVigente scheduling', 'Patient flow optimization']
    },
    {
        role: 'Cirujano Plástico',
        fte: 'Fee-split',
        responsibilities: ['Surgical procedures', 'Consultations', 'Treatment planning'],
        aiAugmentation: ['Virtual Try-On previews', 'RiskGuard assessment', 'PersonaVigente patient matching']
    },
    {
        role: 'Recepción / Ventas',
        fte: 2,
        responsibilities: ['Customer service', 'Booking management', 'Sales conversion'],
        aiAugmentation: ['ChatVigente support', 'OptiVigente scheduling', 'PersonaVigente recommendations']
    }
];

// Total FTE: 8.5 (optimizado por IA)
const TOTAL_FTE = 8.5;

// ========================================
// MARCO DE GOBIERNO DE IA (3 NIVELES)
// ========================================

const AI_GOVERNANCE_FRAMEWORK = {
    strategicLevel: {
        name: 'Comité de Ética IA',
        level: 'Estratégico',
        color: 'red',
        composition: ['CEO', 'CTO', 'CMO', 'Legal Counsel'],
        responsibilities: [
            'Definir principios de IA Responsable (RAI)',
            'Aprobar políticas de uso de datos',
            'Supervisar cumplimiento regulatorio',
            'Evaluar impacto ético de nuevas iniciativas'
        ],
        frequency: 'Trimestral',
        deliverables: ['AI Ethics Policy', 'Data Governance Charter', 'Regulatory Compliance Reports']
    },
    tacticalLevel: {
        name: 'AI Design Review',
        level: 'Táctico',
        color: 'amber',
        composition: ['PMO Lead', 'Data Science Lead', 'Engineering Lead', 'Product Manager'],
        responsibilities: [
            'Revisar diseño de nuevos agentes de IA',
            'Validar arquitectura técnica',
            'Aprobar modelos antes de producción',
            'Gestionar roadmap de desarrollo'
        ],
        frequency: 'Mensual',
        deliverables: ['Technical Design Reviews', 'Model Approval Gates', 'Architecture Decisions']
    },
    operationalLevel: {
        name: 'ML Security Check',
        level: 'Operativo',
        color: 'teal',
        composition: ['MLOps Engineer', 'DevOps Lead', 'Security Engineer', 'QA Lead'],
        responsibilities: [
            'Implementar gates automatizados en CI/CD',
            'Generar Model Cards y Data Sheets',
            'Monitorear deriva de modelos',
            'Ejecutar tests de seguridad'
        ],
        frequency: 'Continuo/Automatizado',
        deliverables: ['Model Cards', 'Data Sheets', 'Security Reports', 'Performance Metrics']
    }
};

// ========================================
// FINANCIAL DATA & PROJECTIONS
// ========================================

const FINANCIAL_DATA = {
    // Datos de ingresos por período
    revenue: {
        daily: {
            labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
            data: [18, 22, 25, 20, 30, 35, 28]
        },
        weekly: {
            labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
            data: [150, 165, 160, 175]
        },
        monthly: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
            data: [600, 620, 650, 680, 710, 750]
        }
    },

    // Proyecciones P&L por escenario
    pnlProjections: {
        base: {
            labels: ['Año 1', 'Año 2', 'Año 3', 'Año 4', 'Año 5'],
            revenue: [7.8, 10, 12.5, 15, 18],
            ebitda: [0.5, 2.5, 4.7, 6.7, 8.5],
            breakEven: '26 meses'
        },
        pessimistic: {
            labels: ['Año 1', 'Año 2', 'Año 3', 'Año 4', 'Año 5'],
            revenue: [5, 7, 8, 9, 10],
            ebitda: [-1, 0.5, 1.5, 2.5, 3],
            breakEven: '38 meses'
        },
        optimistic: {
            labels: ['Año 1', 'Año 2', 'Año 3', 'Año 4', 'Año 5'],
            revenue: [9, 13, 17, 21, 25],
            ebitda: [1.5, 5, 8, 11, 14],
            breakEven: '18 meses'
        }
    },

    // Análisis de CAPEX
    capex: {
        labels: ['Equipamiento', 'Adecuación', 'Mobiliario y Tech'],
        data: [60, 25, 15],
        total: '7.5 MDP',
        breakdown: {
            equipment: {
                'HIFU Ultraformer III': 2.8,
                'Láser Depilación': 1.5,
                'FotoFinder': 0.8,
                'Equipos Dentales': 0.4
            },
            renovation: {
                'Construcción': 1.2,
                'Instalaciones': 0.6,
                'Permisos': 0.2
            },
            technology: {
                'IT Infrastructure': 0.4,
                'Software Licenses': 0.3,
                'Security Systems': 0.3
            }
        }
    },

    // Unit Economics clave
    unitEconomics: {
        ltvCacRatio: '≥ 12',
        cacPayback: '< 2 meses',
        averageTicket: '$45,000 MXN',
        grossMargin: '78%',
        churnRate: '< 8% anual'
    }
};

// ========================================
// EXPORTS - MÓDULOS EXPORTABLES
// ========================================

// Exportar todos los módulos para uso en otras aplicaciones
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DATA_FLYWHEEL_CONFIG,
        FLYWHEEL_ANIMATIONS,
        NORTH_STAR_DASHBOARD,
        CUSTOMER_ARCHETYPES,
        TECH_STACK,
        ORCHESTRATION_PLAYBOOKS,
        CUSTOMER_JOURNEY,
        DEVELOPMENT_SPECIFICATIONS,
        TECHNICAL_ROADMAP,
        AI_AGENTS_ECOSYSTEM,
        CLINIC_LAYOUT_DATA,
        STAFFING_DATA,
        TOTAL_FTE,
        AI_GOVERNANCE_FRAMEWORK,
        FINANCIAL_DATA
    };
}

// Para uso en navegador
if (typeof window !== 'undefined') {
    window.HombreVigenteEcosystem = {
        DATA_FLYWHEEL_CONFIG,
        FLYWHEEL_ANIMATIONS,
        NORTH_STAR_DASHBOARD,
        CUSTOMER_ARCHETYPES,
        TECH_STACK,
        ORCHESTRATION_PLAYBOOKS,
        CUSTOMER_JOURNEY,
        DEVELOPMENT_SPECIFICATIONS,
        TECHNICAL_ROADMAP,
        AI_AGENTS_ECOSYSTEM,
        CLINIC_LAYOUT_DATA,
        STAFFING_DATA,
        TOTAL_FTE,
        AI_GOVERNANCE_FRAMEWORK,
        FINANCIAL_DATA
    };
}

/**
 * RESUMEN DE EXTRACCIÓN COMPLETA:
 * ===============================
 * 
 * ✅ VISION-BOARD.HTML:
 * - Data Flywheel interactivo completo (grid 5x4 con centro SSOT BigQuery)
 * - flywheelComponents object con definiciones completas de los 7 agentes
 * - techStack array con todos los componentes SaaS identificados
 * - Dashboard "North Star" con KPIs en tiempo real
 * - RiskGuard AI Semáforo interactivo (Verde/Amarillo/Rojo)
 * - Blueprints de Orquestación expandibles por clic
 * - Inventario Stack Tecnológico filterable
 * - Journey del Cliente en 6 etapas visuales
 * - CSS animations para flywheel (@keyframes spin)
 * 
 * ✅ PLAYBOOK.HTML:
 * - Cuantificación específica horas desarrollo (NUM_CUSTOMERS = 5000, 40-60h)
 * - Simulación Monte Carlo RiskGuard (80-120 horas desarrollo + testing)
 * - Roadmap técnico por fases (2025-2027, 2027-2028, 2029-2030)
 * - Contrato de datos FotoFinderScanEvent_v1 completo
 * - Plantilla Dockerfile para despliegue por agente
 * - Stack tecnológico granular: Python, NumPy, SciPy, MLflow, Great Expectations
 * - Todas las especificaciones de implementación
 * 
 * ✅ ECOSISTEMA.HTML:
 * - Stack completo de 7 agentes IA internos con descripciones e iconos
 * - orchestrations.churn con flujo completo paso a paso
 * - Arquitectura técnica de integración (tabla fact_event SQL)
 * - Webhook Payload Stripe JSON completo
 * - AssetVigente Predictive Mx y Virtual Try-On GAN
 * - Todas las APIs y orquestación entre componentes
 * 
 * ✅ MVTECH.HTML:
 * - agentData object completo con stack tecnológico específico por agente
 * - La "Trifecta" de Hombre Vigente (3 pilares)
 * - Recorrido del Cliente 6 etapas potenciado por IA
 * - Stack tecnológico básico: Chart.js, Tailwind, Vanilla JS, BigQuery
 * 
 * ✅ SSOTTECH.HTML:
 * - clinicLayoutData array completo (layout optimizado 250 m²)
 * - staffingData con estructura organizacional lean (8.5 FTE)
 * - customerJourneyData con 6 etapas detalladas
 * - aiAgentsData con 6 agentes operacionales completos
 * - Marco de Gobierno de IA (3 niveles: Estratégico, Táctico, Operativo)
 * - Todos los procesos de IA en operaciones
 * 
 * FORMATO: ✅ JavaScript exportable con exports, comentarios explicativos
 * OBJETIVO: ✅ Capturar TODA la riqueza técnica sin perder nada valioso
 */