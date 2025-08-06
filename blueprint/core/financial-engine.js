/**
 * HOMBRE VIGENTE - FINANCIAL ENGINE
 * Pure Business Logic Module
 * 
 * Extracted from modelofinanciero.html
 * Contains: Customer archetypes, journey matrices, adherence factors, 
 * financial calculations, and scenario configurations
 */

// ===================================================================
// SECTION 1: CUSTOMER ARCHETYPES
// ===================================================================

/**
 * Customer Archetypes Configuration
 * Defines the four main customer segments with their characteristics
 */
const customerArchetypes = {
    carlos: { 
        description: "Rejuvenecedor Premium 35-50", 
        percentage: 0.08, 
        ltv: 32085, 
        cacTarget: 2510, 
        churnRate: 0.25 
    },
    eduardo: { 
        description: "Novato Estético 25-40", 
        percentage: 0.42, 
        ltv: 26300, 
        cacTarget: 750, 
        churnRate: 0.45 
    },
    transaccional: { 
        description: "Cazador Ofertas", 
        percentage: 0.22, 
        ltv: 7980, 
        cacTarget: 400, 
        churnRate: 0.75,
        conversionTo: { archetype: 'mantenimiento', rate: 0.20 }
    },
    mantenimiento: { 
        description: "Grooming Regular", 
        percentage: 0.28, 
        ltv: 32980, 
        cacTarget: 450, 
        churnRate: 0.45 
    }
};

// ===================================================================
// SECTION 2: CUSTOMER JOURNEY MATRICES
// ===================================================================

/**
 * Customer Journey Initial Matrix
 * Adoption rates for each service by archetype during first year
 */
const customerJourneyInitial = {
    carlos: {
        "Ajuste Barba y Cejas": 0.90, "Corte de Pelo": 0.85, "Manicure Natural": 0.70, "Pedicure Natural": 0.40, "Reducción Canas": 0.60, "Tinte Natural": 0.25, "Rebaje de Vello Corporal": 0.30, "Masajes Descontracturantes": 0.20,
        "Limpieza Facial Profunda": 0.45, "Limpieza Ultrasonido": 0.35, "PRP Dermapen": 0.03, "HIFU": 0.15, "RF Microneedling": 0.08, "Láser CO2": 0.02,
        "Botox": 0.45, "Fillers": 0.06, "Sculptra": 0.03,
        "Lifting Hilos PDO": 0.01, "Liposucción Papada": 0.01, "Bichectomía": 0.01, "Blefaroplastia": 0.02, "Lipofilling": 0.01,
        "Limpieza Dental": 0.75, "Blanqueamiento LED": 0.15, "Depilación Láser": 0.60, "Bronceado UVA": 0.08
    },
    eduardo: {
        "Ajuste Barba y Cejas": 0.80, "Corte de Pelo": 0.90, "Manicure Natural": 0.30, "Pedicure Natural": 0.15, "Reducción Canas": 0.15, "Tinte Natural": 0.15, "Rebaje de Vello Corporal": 0.15, "Masajes Descontracturantes": 0.25,
        "Limpieza Facial Profunda": 0.55, "Limpieza Ultrasonido": 0.30, "PRP Dermapen": 0.01, "HIFU": 0.02, "RF Microneedling": 0.02, "Láser CO2": 0.0,
        "Botox": 0.08, "Fillers": 0.0, "Sculptra": 0.0,
        "Lifting Hilos PDO": 0.0, "Liposucción Papada": 0.0, "Bichectomía": 0.0, "Blefaroplastia": 0.0, "Lipofilling": 0.0,
        "Limpieza Dental": 0.35, "Blanqueamiento LED": 0.05, "Depilación Láser": 0.30, "Bronceado UVA": 0.02
    },
    mantenimiento: {
        "Ajuste Barba y Cejas": 1.0, "Corte de Pelo": 1.0, "Manicure Natural": 0.50, "Pedicure Natural": 0.30, "Reducción Canas": 0.30, "Tinte Natural": 0.20, "Rebaje de Vello Corporal": 0.20, "Masajes Descontracturantes": 0.20,
        "Limpieza Facial Profunda": 0.40, "Limpieza Ultrasonido": 0.25, "PRP Dermapen": 0.0, "HIFU": 0.01, "RF Microneedling": 0.0, "Láser CO2": 0.0,
        "Botox": 0.05, "Fillers": 0.0, "Sculptra": 0.0,
        "Lifting Hilos PDO": 0.0, "Liposucción Papada": 0.0, "Bichectomía": 0.0, "Blefaroplastia": 0.0, "Lipofilling": 0.0,
        "Limpieza Dental": 0.50, "Blanqueamiento LED": 0.03, "Depilación Láser": 0.20, "Bronceado UVA": 0.05
    },
    transaccional: {
        "Ajuste Barba y Cejas": 0.70, "Corte de Pelo": 0.80, "Manicure Natural": 0.25, "Pedicure Natural": 0.10, "Reducción Canas": 0.10, "Tinte Natural": 0.05, "Rebaje de Vello Corporal": 0.10, "Masajes Descontracturantes": 0.15,
        "Limpieza Facial Profunda": 0.20, "Limpieza Ultrasonido": 0.20, "PRP Dermapen": 0.0, "HIFU": 0.0, "RF Microneedling": 0.0, "Láser CO2": 0.0,
        "Botox": 0.0, "Fillers": 0.0, "Sculptra": 0.0,
        "Lifting Hilos PDO": 0.0, "Liposucción Papada": 0.0, "Bichectomía": 0.0, "Blefaroplastia": 0.0, "Lipofilling": 0.0,
        "Limpieza Dental": 0.15, "Blanqueamiento LED": 0.0, "Depilación Láser": 0.05, "Bronceado UVA": 0.02
    }
};

/**
 * Customer Journey Mature Matrix
 * Adoption rates for each service by archetype after maturity period (12+ months)
 */
const customerJourneyMature = {
    carlos: { // Premium
        "Ajuste Barba y Cejas": 0.95, "Corte de Pelo": 0.95, "Manicure Natural": 0.70, "Pedicure Natural": 0.40, "Reducción Canas": 0.60, "Tinte Natural": 0.25, "Rebaje de Vello Corporal": 0.30, "Masajes Descontracturantes": 0.30,
        "Limpieza Facial Profunda": 0.70, "Limpieza Ultrasonido": 0.35, "PRP Dermapen": 0.08, "HIFU": 0.25, "RF Microneedling": 0.08, "Láser CO2": 0.02,
        "Botox": 0.60, "Fillers": 0.06, "Sculptra": 0.03,
        "Lifting Hilos PDO": 0.03, "Liposucción Papada": 0.03, "Bichectomía": 0.01, "Blefaroplastia": 0.02, "Lipofilling": 0.01,
        "Limpieza Dental": 0.75, "Blanqueamiento LED": 0.25, "Depilación Láser": 0.80, "Bronceado UVA": 0.08
    },
    eduardo: { // Evolves into "Aspiracional"
        "Ajuste Barba y Cejas": 0.75, "Corte de Pelo": 0.85, "Manicure Natural": 0.30, "Pedicure Natural": 0.15, "Reducción Canas": 0.15, "Tinte Natural": 0.15, "Rebaje de Vello Corporal": 0.15, "Masajes Descontracturantes": 0.20,
        "Limpieza Facial Profunda": 0.55, "Limpieza Ultrasonido": 0.30, "PRP Dermapen": 0.02, "HIFU": 0.08, "RF Microneedling": 0.02, "Láser CO2": 0.0,
        "Botox": 0.12, "Fillers": 0.0, "Sculptra": 0.0,
        "Lifting Hilos PDO": 0.0, "Liposucción Papada": 0.0, "Bichectomía": 0.0, "Blefaroplastia": 0.0, "Lipofilling": 0.0,
        "Limpieza Dental": 0.35, "Blanqueamiento LED": 0.08, "Depilación Láser": 0.40, "Bronceado UVA": 0.02
    },
    mantenimiento: { // Evolves into "Performance"
        "Ajuste Barba y Cejas": 1.0, "Corte de Pelo": 1.0, "Manicure Natural": 0.50, "Pedicure Natural": 0.30, "Reducción Canas": 0.30, "Tinte Natural": 0.20, "Rebaje de Vello Corporal": 0.20, "Masajes Descontracturantes": 0.35,
        "Limpieza Facial Profunda": 0.85, "Limpieza Ultrasonido": 0.25, "PRP Dermapen": 0.15, "HIFU": 0.30, "RF Microneedling": 0.0, "Láser CO2": 0.0,
        "Botox": 0.45, "Fillers": 0.0, "Sculptra": 0.0,
        "Lifting Hilos PDO": 0.01, "Liposucción Papada": 0.02, "Bichectomía": 0.0, "Blefaroplastia": 0.0, "Lipofilling": 0.0,
        "Limpieza Dental": 0.50, "Blanqueamiento LED": 0.25, "Depilación Láser": 0.70, "Bronceado UVA": 0.05
    },
    transaccional: { // Remains the same, as they don't mature, they convert or churn
        "Ajuste Barba y Cejas": 0.70, "Corte de Pelo": 0.80, "Manicure Natural": 0.25, "Pedicure Natural": 0.10, "Reducción Canas": 0.10, "Tinte Natural": 0.05, "Rebaje de Vello Corporal": 0.10, "Masajes Descontracturantes": 0.15,
        "Limpieza Facial Profunda": 0.20, "Limpieza Ultrasonido": 0.20, "PRP Dermapen": 0.0, "HIFU": 0.0, "RF Microneedling": 0.0, "Láser CO2": 0.0,
        "Botox": 0.0, "Fillers": 0.0, "Sculptra": 0.0,
        "Lifting Hilos PDO": 0.0, "Liposucción Papada": 0.0, "Bichectomía": 0.0, "Blefaroplastia": 0.0, "Lipofilling": 0.0,
        "Limpieza Dental": 0.15, "Blanqueamiento LED": 0.0, "Depilación Láser": 0.05, "Bronceado UVA": 0.02
    }
};

// ===================================================================
// SECTION 3: ADHERENCE MATRIX
// ===================================================================

/**
 * Adherence Matrix
 * Service adherence factors by customer archetype and service tier
 */
const adherenceMatrix = {
    carlos: { ultra: 0.90, high: 0.75, premium: 0.60, luxury: 0.40, surgery: 0.95 },
    eduardo: { ultra: 0.85, high: 0.65, premium: 0.35, luxury: 0.15, surgery: 0.95 },
    mantenimiento: { ultra: 0.80, high: 0.50, premium: 0.15, luxury: 0.05, surgery: 0.95 },
    transaccional: { ultra: 0.70, high: 0.30, premium: 0.05, luxury: 0.02, surgery: 0.95 }
};

// ===================================================================
// SECTION 4: SCENARIO CONFIGURATIONS
// ===================================================================

/**
 * Base Model Configuration
 * Default scenario with calibrated assumptions
 */
const baseModelData = {
    general: { 
        currency: "MXN", 
        projectionTimeline: { unit: "months", duration: 60 }, 
        scenario: "base" 
    },
    realismLevers: {
        funnelConversionRate: 0.50
    },
    customerBehavior: {
        realismFactor: 0.85,
        cohortMaturityMonths: 12, 
        adherenceMultipliers: { ultra: 1.0, high: 1.0, premium: 1.0, luxury: 1.0 }
    },
    adherenceMatrix: adherenceMatrix,
    aiDefaults: {
        efficiencyUplift: 1.05,
        CACReduction: 0.10,
        aiPersonalizationUplift: 0.08, 
        crossSellBoost: 0.08
    },
    customerArchetypes: customerArchetypes,
    marketing: {
        launchStrategy: {
            enabled: true,
            durationMonths: 6,
            seedFundingAllocation: 2485000,
            plazaLaunchBudget: 2840000,
            sucursalLaunchBudget: 750000
        },
        sustainBudgetPerLocation: 25000,
        walkInsPerLocationPerMonth: 50 
    },
    marketingChannels: {
        carlosFunnel: { target: "carlos", cac: 1800, wordOfMouthMultiplier: 1.15 },
        eduardoFunnel: { target: "eduardo", cac: 1200, wordOfMouthMultiplier: 1.35 },
        transaccionalFunnel: { target: "transaccional", cac: 0, wordOfMouthMultiplier: 1.05 },
        mantenimientoFunnel: { target: "mantenimiento", cac: 600, wordOfMouthMultiplier: 1.20 }
    },
    pricing: {
        premiumServiceDiscount: 0.0,
        services: [ 
            { name: "HIFU", category: "Rejuvenecimiento y Facial", defaultPrice: 3800, suppliesCost: 140, tier: "premium", adherenceTier: "premium", repurchaseCycleMonths: 12, avgDurationHours: 1.5 },
            { name: "RF Microneedling", category: "Rejuvenecimiento y Facial", defaultPrice: 2800, suppliesCost: 170, tier: "premium", adherenceTier: "premium", repurchaseCycleMonths: 4, avgDurationHours: 1.0 },
            { name: "Láser CO2", category: "Rejuvenecimiento y Facial", defaultPrice: 4700, suppliesCost: 180, tier: "premium", adherenceTier: "luxury", revenueShare: 0.35, repurchaseCycleMonths: 12, avgDurationHours: 1.0 },
            { name: "Limpieza Facial Profunda", category: "Rejuvenecimiento y Facial", defaultPrice: 750, suppliesCost: 75, tier: "mid", adherenceTier: "high", repurchaseCycleMonths: 1.5, avgDurationHours: 1.0 },
            { name: "PRP Dermapen", category: "Rejuvenecimiento y Facial", defaultPrice: 3000, suppliesCost: 110, tier: "mid", adherenceTier: "premium", repurchaseCycleMonths: 2, avgDurationHours: 1.0 },
            { name: "Limpieza Ultrasonido", category: "Rejuvenecimiento y Facial", defaultPrice: 580, suppliesCost: 55, tier: "basic", adherenceTier: "high", repurchaseCycleMonths: 2, avgDurationHours: 0.75 },
            { name: "Botox", category: "Aplicaciones de Precisión", defaultPrice: 4800, suppliesCost: 100, tier: "premium", adherenceTier: "premium", revenueShare: 0.35, repurchaseCycleMonths: 6, avgDurationHours: 0.5 },
            { name: "Fillers", category: "Aplicaciones de Precisión", defaultPrice: 4800, suppliesCost: 140, tier: "premium", adherenceTier: "premium", revenueShare: 0.35, repurchaseCycleMonths: 9, avgDurationHours: 0.75 },
            { name: "Sculptra", category: "Aplicaciones de Precisión", defaultPrice: 11000, suppliesCost: 180, tier: "premium", adherenceTier: "luxury", revenueShare: 0.35, repurchaseCycleMonths: 1.25, avgDurationHours: 1.0 },
            { name: "Lifting Hilos PDO", category: "Procedimientos de Contorno", defaultPrice: 3800, suppliesCost: 140, tier: "premium", adherenceTier: "luxury", revenueShare: 0.35, repurchaseCycleMonths: 18, avgDurationHours: 1.5 },
            { name: "Liposucción Papada", category: "Procedimientos de Contorno", defaultPrice: 16500, suppliesCost: 8250, tier: "surgery", adherenceTier: "surgery", revenueShare: 0.50, repurchaseCycleMonths: 60, avgDurationHours: 3.0 },
            { name: "Bichectomía", category: "Procedimientos de Contorno", defaultPrice: 14000, suppliesCost: 7000, tier: "surgery", adherenceTier: "surgery", revenueShare: 0.50, repurchaseCycleMonths: 60, avgDurationHours: 2.0 },
            { name: "Blefaroplastia", category: "Procedimientos de Contorno", defaultPrice: 23000, suppliesCost: 11500, tier: "surgery", adherenceTier: "surgery", revenueShare: 0.50, repurchaseCycleMonths: 60, avgDurationHours: 2.5 },
            { name: "Lipofilling", category: "Procedimientos de Contorno", defaultPrice: 14000, suppliesCost: 7000, tier: "surgery", adherenceTier: "surgery", revenueShare: 0.50, repurchaseCycleMonths: 60, avgDurationHours: 2.5 },
            { name: "Blanqueamiento LED", category: "Grooming y Wellness", defaultPrice: 3300, suppliesCost: 140, tier: "premium", adherenceTier: "premium", repurchaseCycleMonths: 8, avgDurationHours: 1.0 },
            { name: "Limpieza Dental", category: "Grooming y Wellness", defaultPrice: 1200, suppliesCost: 90, tier: "mid", adherenceTier: "ultra", repurchaseCycleMonths: 6, avgDurationHours: 0.75 },
            { name: "Depilación Láser", category: "Grooming y Wellness", defaultPrice: 2300, suppliesCost: 140, tier: "mid", adherenceTier: "high", repurchaseCycleMonths: 2, avgDurationHours: 1.0 },
            { name: "Masajes Descontracturantes", category: "Grooming y Wellness", defaultPrice: 950, suppliesCost: 75, tier: "basic", adherenceTier: "high", repurchaseCycleMonths: 1, avgDurationHours: 1.0 },
            { name: "Bronceado UVA", category: "Grooming y Wellness", defaultPrice: 480, suppliesCost: 35, tier: "basic", adherenceTier: "luxury", repurchaseCycleMonths: 0.5, avgDurationHours: 0.5 },
            { name: "Corte de Pelo", category: "Grooming y Wellness", defaultPrice: 380, suppliesCost: 28, tier: "basic", adherenceTier: "ultra", repurchaseCycleMonths: 0.75, avgDurationHours: 0.75 },
            { name: "Ajuste Barba y Cejas", category: "Grooming y Wellness", defaultPrice: 280, suppliesCost: 18, tier: "basic", adherenceTier: "ultra", repurchaseCycleMonths: 0.5, avgDurationHours: 0.5 },
            { name: "Manicure Natural", category: "Grooming y Wellness", defaultPrice: 380, suppliesCost: 28, tier: "basic", adherenceTier: "ultra", repurchaseCycleMonths: 0.75, avgDurationHours: 0.5 },
            { name: "Pedicure Natural", category: "Grooming y Wellness", defaultPrice: 480, suppliesCost: 38, tier: "basic", adherenceTier: "high", repurchaseCycleMonths: 1, avgDurationHours: 0.75 }
        ]
    },
    fxRates: { MXN: 1, USD: 20, COP: 3999, EUR: 22 },
    taxSettings: { isrMexico: 0.31, isrColombia: 0.35 }
};

/**
 * Scenario Configurations
 * Pessimistic, Base, and Optimistic scenarios
 */
const scenarios = {
    pessimistic: {
        realismLevers: { funnelConversionRate: 0.40 },
        customerArchetypes: { 
            carlos: { churnRate: baseModelData.customerArchetypes.carlos.churnRate * 1.1 }, 
            eduardo: { churnRate: baseModelData.customerArchetypes.eduardo.churnRate * 1.1 },
            mantenimiento: { churnRate: baseModelData.customerArchetypes.mantenimiento.churnRate * 1.1 },
            transaccional: { churnRate: baseModelData.customerArchetypes.transaccional.churnRate * 1.1 }
        },
        capacity: { targetUtilization: 0.50 }
    },
    base: {}, // Base is reset to calibrated baseModelData
    optimistic: {
        realismLevers: { funnelConversionRate: 0.70 },
        customerArchetypes: { 
            carlos: { churnRate: baseModelData.customerArchetypes.carlos.churnRate * 0.9 }, 
            eduardo: { churnRate: baseModelData.customerArchetypes.eduardo.churnRate * 0.9 },
            mantenimiento: { churnRate: baseModelData.customerArchetypes.mantenimiento.churnRate * 0.9 },
            transaccional: { churnRate: baseModelData.customerArchetypes.transaccional.churnRate * 0.9 }
        },
        capacity: { targetUtilization: 0.70 }
    }
};

// ===================================================================
// SECTION 5: CALCULATION FUNCTIONS
// ===================================================================

/**
 * Dynamic Churn Calculation
 * Calculates churn rate based on customer archetype and cohort age
 */
function getDynamicChurn(archetype, cohortAgeMonths) {
    const baseChurn = baseModelData.customerArchetypes[archetype].churnRate;
    let ageMultiplier;
    
    if (cohortAgeMonths < 3) {
        ageMultiplier = 1.5; // 50% más churn en primeros 3 meses
    } else if (cohortAgeMonths < 12) {
        ageMultiplier = 1.0; // Churn normal durante primer año
    } else {
        ageMultiplier = 0.7; // 30% menos churn después del año (lealtad)
    }
    
    return Math.min(baseChurn * ageMultiplier, 0.95); // Cap máximo 95%
}

/**
 * Average Hours Per New Customer Calculation
 * Calculates expected service hours consumption for new customers
 */
function getAvgHoursPerNewCustomer(modelData) {
    let totalHours = 0;
    let totalPercentage = 0;
    const { customerArchetypes, pricing, adherenceMatrix, customerBehavior } = modelData;
    const realismFactor = customerBehavior?.realismFactor || 1.0;
    
    for (const archetype in customerArchetypes) {
        if (archetype === 'transaccional') continue; // Exclude walk-ins from paid acquisition calc
        const archData = customerArchetypes[archetype];
        const journey = customerJourneyInitial[archetype]; // Use initial journey for new customers
        let hoursForArchetype = 0;
        
        for (const serviceName in journey) {
            const adoptionRate = journey[serviceName] * realismFactor;
            const service = pricing.services.find(s => s.name === serviceName);
            if (adoptionRate > 0 && service && service.repurchaseCycleMonths > 0) {
                const adherenceTier = service.adherenceTier || 'high'; // fallback
                const adherenceFactor = adherenceMatrix[archetype]?.[adherenceTier] || 0.75; // fallback
                const monthlyFrequency = (1 / service.repurchaseCycleMonths) * adherenceFactor;
                hoursForArchetype += adoptionRate * monthlyFrequency * service.avgDurationHours;
            }
        }
        totalHours += hoursForArchetype * archData.percentage;
        totalPercentage += archData.percentage;
    }
    
    return totalPercentage > 0 ? totalHours / totalPercentage : 0.5; // Return weighted average, or a default of 0.5 hours
}

/**
 * Intelligent Budget Allocation
 * Allocates marketing budget across customer archetypes based on strategic focus
 */
function calculateIntelligentBudgetAllocation(modelData, month, totalBudget) {
    const strategicFocus = modelData.marketingVigente?.strategicFocus || 0.3; 
    let allocations = { carlos: 0, eduardo: 0, mantenimiento: 0, transaccional: 0 };
    const profitabilityBudget = totalBudget * strategicFocus;
    const acquisitionBudget = totalBudget * (1 - strategicFocus);
    
    allocations.carlos = profitabilityBudget;
    const eduardoWeight = modelData.customerArchetypes.eduardo.percentage;
    const mantenimientoWeight = modelData.customerArchetypes.mantenimiento.percentage;
    const totalAcquisitionWeight = eduardoWeight + mantenimientoWeight;
    
    if (totalAcquisitionWeight > 0) {
        allocations.eduardo = acquisitionBudget * (eduardoWeight / totalAcquisitionWeight);
        allocations.mantenimiento = acquisitionBudget * (mantenimientoWeight / totalAcquisitionWeight);
    } else {
        allocations.eduardo = acquisitionBudget / 2;
        allocations.mantenimiento = acquisitionBudget / 2;
    }
    
    return allocations;
}

/**
 * Gross Margin Per Customer Calculation
 * Calculates gross margin for a specific customer archetype
 */
function calculateGrossMarginPerCustomer(modelData, archetypeKey) {
    const journey = customerJourneyInitial[archetypeKey]; // Use initial for this calculation
    if (!journey) return 0;
    
    let annualRevenue = 0;
    let annualCogs = 0;
    const realismFactor = modelData.customerBehavior?.realismFactor || 1.0;
    
    for (const service of modelData.pricing.services) {
        const adoptionRate = (journey[service.name] || 0) * realismFactor;
        if (adoptionRate > 0 && service.repurchaseCycleMonths > 0) {
            const adherenceTier = service.adherenceTier || 'high';
            const adherenceFactor = modelData.adherenceMatrix[archetypeKey]?.[adherenceTier] || 0.75;
            const annualFrequency = (12 / service.repurchaseCycleMonths) * adherenceFactor;
            annualRevenue += adoptionRate * annualFrequency * service.defaultPrice;
            annualCogs += adoptionRate * annualFrequency * service.suppliesCost;
        }
    }
    
    return annualRevenue - annualCogs;
}

/**
 * Blended LTV/CAC Calculation
 * Calculates blended Lifetime Value and Customer Acquisition Cost metrics
 */
function calculateBlendedLtvCac(modelData, yearMonthsData) {
    let totalWeightedGrossMargin = 0;
    let totalWeightedChurn = 0;
    const paidArchetypes = ['carlos', 'eduardo', 'mantenimiento'];
    const totalPaidPercentage = paidArchetypes.reduce((sum, arch) => sum + (modelData.customerArchetypes[arch].percentage || 0), 0);
    
    paidArchetypes.forEach(archetypeKey => {
        const archetypeData = modelData.customerArchetypes[archetypeKey];
        const grossMargin = calculateGrossMarginPerCustomer(modelData, archetypeKey);
        const reweightedPercentage = archetypeData.percentage / totalPaidPercentage;
        totalWeightedGrossMargin += grossMargin * reweightedPercentage;
        totalWeightedChurn += archetypeData.churnRate * reweightedPercentage;
    });
    
    const blendedLTV = totalWeightedChurn > 0 ? totalWeightedGrossMargin / totalWeightedChurn : 0;
    
    const totalMarketingSpend = yearMonthsData.reduce((sum, m) => sum + (m.pnl.marketingSpend || 0), 0);
    const totalNewPaidCustomers = yearMonthsData.reduce((sum, m) => {
        let monthlyPaidOnly = 0;
        paidArchetypes.forEach(archetype => {
            monthlyPaidOnly += m.newCustomersPaid?.[archetype] || 0;
        });
        return sum + monthlyPaidOnly;
    }, 0);
    
    const blendedCAC = totalNewPaidCustomers > 0 ? totalMarketingSpend / totalNewPaidCustomers : 0;
    const ratio = blendedCAC > 0 ? blendedLTV / blendedCAC : 0;
    
    const breakdown = `LTV Ponderado (Pagados): ${formatCurrency(blendedLTV)}\n` +
        `  - Margen Bruto Anual Ponderado: ${formatCurrency(totalWeightedGrossMargin)}\n` +
        `  - Tasa de Churn Anual Ponderada: ${(totalWeightedChurn * 100).toFixed(1)}%\n` +
        `CAC Real (Pagados): ${formatCurrency(blendedCAC)}`;
    
    return { ratio, breakdown, ltv: blendedLTV, cac: blendedCAC };
}

/**
 * IRR Calculation
 * Calculates Internal Rate of Return using Newton-Raphson method
 */
function calculateIRR(cashFlows, maxIterations = 100, tolerance = 1e-6) {
    let guess = 0.1;
    for (let i = 0; i < maxIterations; i++) {
        let npv = 0.0;
        let dNpv = 0.0;
        for (let t = 0; t < cashFlows.length; t++) {
            npv += cashFlows[t] / Math.pow(1 + guess, t);
            dNpv -= t * cashFlows[t] / Math.pow(1 + guess, t + 1);
        }
        if (Math.abs(npv) < tolerance) {
            return guess * 100;
        }
        if (dNpv === 0) break;
        guess -= npv / dNpv;
    }
    return 0; // Failed to converge
}

/**
 * TIR for Multiple Calculation
 * Calculates TIR (Tasa Interna de Retorno) for a given multiple
 */
function calculateTIRForMultiple(multiple, results) {
    const equityInvested = baseModelData.capitalStructure?.equityRounds?.reduce((s, r) => s + r.amount, 0) || 0;
    if (equityInvested === 0 || !results || !results.cf || results.cf.length < 5) return 0;
    
    const cashFlows = [ -equityInvested ];
    for (let i = 0; i < 4; i++) {
        cashFlows.push(results.cf[i].cfo);
    }
    
    const terminalValue = results.pl[4].ebitda * multiple;
    const debtRemaining = results.bs ? results.bs[4].debt.total : 0;
    const equityValue = Math.max(0, terminalValue - debtRemaining);
    
    cashFlows[cashFlows.length - 1] += equityValue;
    
    return calculateIRR(cashFlows);
}

/**
 * Unit Economics Calculations
 * Various unit economics and pricing algorithms
 */
const unitEconomics = {
    /**
     * Calculate CAGR (Compound Annual Growth Rate)
     */
    calculateCAGR: (beginningValue, endingValue, periods) => {
        if (beginningValue <= 0 || endingValue <= 0 || periods <= 0) return 0;
        return (Math.pow(endingValue / beginningValue, 1 / periods) - 1) * 100;
    },

    /**
     * Calculate Payback Period
     */
    calculatePaybackPeriod: (results) => {
        if (!results || !results.cf) return 0;
        let cumulativeCF = 0;
        for (let i = 0; i < results.cf.length; i++) {
            cumulativeCF += results.cf[i].cfo;
            if (cumulativeCF > 0) {
                return i + 1;
            }
        }
        return results.cf.length; // If never positive, return max period
    },

    /**
     * Calculate Money Multiple
     */
    calculateMoneyMultiple: (results) => {
        const equityInvested = baseModelData.capitalStructure?.equityRounds?.reduce((s, r) => s + r.amount, 0) || 0;
        if (equityInvested === 0 || !results || !results.pl || results.pl.length === 0) return 0;
        
        const terminalValue = results.pl[results.pl.length - 1].ebitda * 15; // 15x multiple
        const debtRemaining = results.bs ? results.bs[results.bs.length - 1].debt.total : 0;
        const equityValue = Math.max(0, terminalValue - debtRemaining);
        
        return equityValue / equityInvested;
    }
};

/**
 * Currency Formatting Utility
 */
function formatCurrency(value, abbreviated = false) {
    if (typeof value !== 'number' || isNaN(value)) return '$0';
    
    if (abbreviated && Math.abs(value) >= 1000000) {
        return `$${(value / 1000000).toFixed(1)}M`;
    } else if (abbreviated && Math.abs(value) >= 1000) {
        return `$${(value / 1000).toFixed(0)}K`;
    }
    
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

/**
 * Deep Merge Utility
 * Recursively merges objects for scenario configuration
 */
function mergeDeep(target, source) {
    const result = { ...target };
    
    for (const key in source) {
        if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
            result[key] = mergeDeep(result[key] || {}, source[key]);
        } else {
            result[key] = source[key];
        }
    }
    
    return result;
}

// ===================================================================
// SECTION 6: EXPORTS
// ===================================================================

// Export all business logic components
module.exports = {
    // Data Objects
    customerArchetypes,
    customerJourneyInitial,
    customerJourneyMature,
    adherenceMatrix,
    baseModelData,
    scenarios,
    
    // Calculation Functions
    getDynamicChurn,
    getAvgHoursPerNewCustomer,
    calculateIntelligentBudgetAllocation,
    calculateGrossMarginPerCustomer,
    calculateBlendedLtvCac,
    calculateIRR,
    calculateTIRForMultiple,
    unitEconomics,
    
    // Utility Functions
    formatCurrency,
    mergeDeep
};

// For CommonJS compatibility
if (typeof exports !== 'undefined') {
    Object.assign(exports, module.exports);
}

// For ES6 module compatibility
if (typeof window !== 'undefined') {
    window.FinancialEngine = module.exports;
}