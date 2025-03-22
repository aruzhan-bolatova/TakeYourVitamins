// supplements.ts : Contains the mock data and search functions

import type { Supplement } from "@/lib/types"

// Mock database of supplements
const supplementsData: Supplement[] = [
  {
    id: "vitamin-d",
    name: "Vitamin D",
    aliases: ["Cholecalciferol", "Vitamin D3", "Calciferol"],
    category: "Vitamin",
    description:
      "Vitamin D is a fat-soluble vitamin that helps your body absorb calcium and phosphorus. It is essential for bone health and immune function.",
    intakePractices: {
      dosage:
        "The recommended daily allowance (RDA) for adults is 600-800 IU (15-20 mcg) per day. Higher doses may be recommended for those with deficiency.",
      timing: "Best taken with a meal containing fats to enhance absorption, particularly during breakfast or lunch.",
      specialInstructions:
        "Vitamin D supplements come in two forms: D2 (ergocalciferol) and D3 (cholecalciferol). D3 is generally considered more effective at raising blood levels of vitamin D.",
    },
    supplementInteractions: [
      {
        supplementName: "Calcium",
        severity: "low",
        effect: "Vitamin D enhances calcium absorption, making them beneficial to take together.",
        recommendation: "These supplements complement each other and can be taken together.",
      },
      {
        supplementName: "Magnesium",
        severity: "low",
        effect: "Magnesium helps activate vitamin D in the body.",
        recommendation: "These supplements work well together and can enhance each other's effectiveness.",
      },
    ],
    foodInteractions: [
      {
        foodName: "Fatty fish",
        effect: "enhances absorption",
        description:
          "Fatty fish like salmon, mackerel, and tuna are natural sources of vitamin D and can enhance overall vitamin D status.",
        recommendation: "Consider including fatty fish in your diet 2-3 times per week.",
      },
      {
        foodName: "High-fiber foods",
        effect: "reduces absorption",
        description: "High-fiber foods may slightly reduce vitamin D absorption if taken at the same time.",
        recommendation: "Consider taking vitamin D supplements a few hours apart from high-fiber meals.",
      },
    ],
  },
  {
    id: "magnesium",
    name: "Magnesium",
    aliases: ["Magnesium citrate", "Magnesium glycinate", "Magnesium oxide"],
    category: "Mineral",
    description:
      "Magnesium is an essential mineral involved in over 300 enzymatic reactions in the body. It supports muscle and nerve function, energy production, and helps maintain heart rhythm.",
    intakePractices: {
      dosage: "The RDA for adults is 310-420 mg per day. Different forms have different absorption rates and effects.",
      timing:
        "Can be taken with or without food. If taking higher doses, splitting into two doses (morning and evening) may reduce digestive side effects.",
      specialInstructions:
        "Magnesium citrate and glycinate are generally better absorbed than magnesium oxide. Magnesium citrate may have a mild laxative effect.",
    },
    supplementInteractions: [
      {
        supplementName: "Calcium",
        severity: "medium",
        effect: "Calcium and magnesium compete for absorption when taken at the same time in high doses.",
        recommendation: "If taking more than 250mg of either mineral, consider taking them at different times.",
      },
      {
        supplementName: "Vitamin D",
        severity: "low",
        effect: "Magnesium is required for vitamin D metabolism and activation.",
        recommendation: "These supplements complement each other well.",
      },
      {
        supplementName: "Zinc",
        severity: "medium",
        effect: "High doses of zinc can reduce magnesium absorption and vice versa.",
        recommendation: "Take these supplements at different times if possible.",
      },
    ],
    foodInteractions: [
      {
        foodName: "High-fiber foods",
        effect: "reduces absorption",
        description: "Phytates in high-fiber foods can bind to magnesium and reduce its absorption.",
        recommendation: "Consider taking magnesium supplements 1-2 hours away from high-fiber meals.",
      },
      {
        foodName: "Dairy products",
        effect: "affects absorption",
        description: "The calcium in dairy may compete with magnesium for absorption pathways.",
        recommendation: "Consider taking magnesium supplements separate from calcium-rich meals.",
      },
    ],
  },
  {
    id: "omega-3",
    name: "Omega-3 Fatty Acids",
    aliases: ["Fish oil", "EPA", "DHA", "Alpha-linolenic acid"],
    category: "Fatty Acid",
    description:
      "Omega-3 fatty acids are essential fats that play important roles in heart health, brain function, and reducing inflammation. The three main types are ALA, EPA, and DHA.",
    intakePractices: {
      dosage:
        "General recommendations range from 250-1000 mg combined EPA and DHA per day for general health. Higher doses may be recommended for specific conditions.",
      timing:
        "Best taken with meals, especially those containing fat, to enhance absorption and reduce the chance of fishy aftertaste.",
      specialInstructions:
        "Fish oil supplements should be stored in a cool, dark place to prevent oxidation. Enteric-coated capsules can reduce fishy burps.",
    },
    supplementInteractions: [
      {
        supplementName: "Vitamin E",
        severity: "low",
        effect: "Vitamin E can enhance the stability of omega-3 fatty acids and prevent oxidation.",
        recommendation: "These supplements can be beneficial when taken together.",
      },
      {
        supplementName: "Blood thinners (like aspirin)",
        severity: "high",
        effect:
          "Omega-3s have a mild blood-thinning effect that can be amplified when combined with other blood thinners.",
        recommendation: "Consult with a healthcare provider before combining these supplements.",
      },
    ],
    foodInteractions: [
      {
        foodName: "High-fat meals",
        effect: "enhances absorption",
        description: "Taking omega-3 supplements with a meal containing fat can enhance absorption.",
        recommendation: "Take with breakfast or dinner that contains some healthy fats.",
      },
      {
        foodName: "Alcohol",
        effect: "reduces effectiveness",
        description:
          "Regular alcohol consumption may reduce the beneficial effects of omega-3 fatty acids on triglycerides and heart health.",
        recommendation: "Limit alcohol consumption when taking omega-3 supplements for heart health.",
      },
    ],
  },
  {
    id: "iron",
    name: "Iron",
    aliases: ["Ferrous sulfate", "Ferrous gluconate", "Ferrous fumarate"],
    category: "Mineral",
    description:
      "Iron is an essential mineral that plays a key role in the production of hemoglobin, a protein in red blood cells that carries oxygen from the lungs to the rest of the body.",
    intakePractices: {
      dosage:
        "The RDA for adults is 8-18 mg per day, with higher needs for menstruating women. Iron supplements typically contain 45-60 mg of elemental iron.",
      timing:
        "Best taken on an empty stomach, but can be taken with food if it causes stomach upset. Taking with vitamin C enhances absorption.",
      specialInstructions:
        "Iron supplements can cause constipation and stomach upset. Starting with a lower dose and gradually increasing can help minimize side effects.",
    },
    supplementInteractions: [
      {
        supplementName: "Calcium",
        severity: "high",
        effect: "Calcium significantly reduces iron absorption when taken at the same time.",
        recommendation: "Take iron and calcium supplements at least 2 hours apart.",
      },
      {
        supplementName: "Vitamin C",
        severity: "low",
        effect: "Vitamin C enhances iron absorption, particularly non-heme (plant-based) iron.",
        recommendation: "Taking vitamin C with iron supplements can increase absorption by up to 3 times.",
      },
      {
        supplementName: "Zinc",
        severity: "medium",
        effect: "Iron and zinc compete for absorption when taken together in supplement form.",
        recommendation: "Take these supplements at different times of the day.",
      },
    ],
    foodInteractions: [
      {
        foodName: "Tea and coffee",
        effect: "reduces absorption",
        description: "Tannins in tea and coffee can bind to iron and significantly reduce its absorption.",
        recommendation: "Avoid consuming tea or coffee within 1-2 hours of taking iron supplements.",
      },
      {
        foodName: "Dairy products",
        effect: "reduces absorption",
        description: "Calcium in dairy products can inhibit iron absorption.",
        recommendation: "Take iron supplements 2 hours before or after consuming dairy products.",
      },
      {
        foodName: "Citrus fruits",
        effect: "enhances absorption",
        description: "Vitamin C in citrus fruits enhances iron absorption.",
        recommendation: "Consider taking iron supplements with orange juice or other vitamin C-rich foods.",
      },
    ],
  },
  {
    id: "zinc",
    name: "Zinc",
    aliases: ["Zinc gluconate", "Zinc picolinate", "Zinc acetate"],
    category: "Mineral",
    description:
      "Zinc is an essential trace mineral that plays vital roles in immune function, protein synthesis, wound healing, DNA synthesis, and cell division.",
    intakePractices: {
      dosage: "The RDA for adults is 8-11 mg per day. Zinc supplements typically contain 15-30 mg of elemental zinc.",
      timing: "Best taken 1-2 hours before or after meals, but can be taken with food if it causes stomach upset.",
      specialInstructions:
        "Long-term use of high-dose zinc supplements (>40 mg/day) should be monitored by a healthcare provider as it may lead to copper deficiency.",
    },
    supplementInteractions: [
      {
        supplementName: "Copper",
        severity: "medium",
        effect: "High doses of zinc can reduce copper absorption and potentially lead to copper deficiency.",
        recommendation:
          "If taking zinc supplements long-term, consider a multivitamin with copper or periodic copper status monitoring.",
      },
      {
        supplementName: "Iron",
        severity: "medium",
        effect: "Zinc and iron compete for absorption when taken together in supplement form.",
        recommendation: "Take these supplements at different times of the day.",
      },
      {
        supplementName: "Calcium",
        severity: "low",
        effect: "Calcium may slightly reduce zinc absorption when taken together.",
        recommendation: "Consider taking these supplements at different times if possible.",
      },
    ],
    foodInteractions: [
      {
        foodName: "High-phytate foods",
        effect: "reduces absorption",
        description: "Phytates in whole grains, legumes, and nuts can bind to zinc and reduce its absorption.",
        recommendation: "Take zinc supplements 1-2 hours away from high-phytate meals.",
      },
      {
        foodName: "Dairy products",
        effect: "enhances absorption",
        description: "The protein in dairy products can enhance zinc absorption.",
        recommendation: "Consider taking zinc supplements with a small amount of dairy if tolerated.",
      },
    ],
  },
]

// Function to search supplements by name or aliases
export async function searchSupplements(query: string): Promise<Supplement[]> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  const normalizedQuery = query.toLowerCase().trim()

  return supplementsData.filter(
    (supplement) =>
      supplement.name.toLowerCase().includes(normalizedQuery) ||
      supplement.aliases.some((alias) => alias.toLowerCase().includes(normalizedQuery)),
  )
}

// Function to get a supplement by ID
export async function getSupplementById(id: string): Promise<Supplement | undefined> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 300))

  return supplementsData.find((supplement) => supplement.id === id)
}

// Function to get auto complete suggestions based on input
export async function getSuggestions(query: string): Promise<string[]> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 200))

  const normalizedQuery = query.toLowerCase().trim()

  if (!normalizedQuery) return []

  // Get unique suggestions from supplement names and aliases
  const suggestions = new Set<string>()

  supplementsData.forEach((supplement) => {
    if (supplement.name.toLowerCase().includes(normalizedQuery)) {
      suggestions.add(supplement.name)
    }

    supplement.aliases.forEach((alias) => {
      if (alias.toLowerCase().includes(normalizedQuery)) {
        suggestions.add(alias)
      }
    })
  })

  // Convert Set to Array and limit to 10 suggestions
  return Array.from(suggestions).slice(0, 10)
}

