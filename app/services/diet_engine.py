"""
HemoVision AI – Diet Intelligence Engine
==========================================
Generates personalized iron-rich diet plans based on
anemia severity, pregnancy status, and budget mode.
"""

# ─── Iron Intake Targets (mg/day) per WHO ────────────────────────────────────
IRON_TARGETS = {
    'Normal': {'male': 8, 'female': 18, 'pregnant': 27},
    'Mild Anemia': {'male': 15, 'female': 25, 'pregnant': 35},
    'Moderate Anemia': {'male': 25, 'female': 35, 'pregnant': 45},
    'Severe Anemia': {'male': 35, 'female': 45, 'pregnant': 60}
}

# ─── Standard Meal Plans ─────────────────────────────────────────────────────
MEAL_PLANS = {
    'Mild Anemia': {
        'breakfast': [
            {'name': 'Fortified Oatmeal with Raisins & Pumpkin Seeds', 'iron_mg': 4.5, 'icon': '🥣'},
            {'name': 'Spinach & Mushroom Omelette', 'iron_mg': 3.2, 'icon': '🥚'},
            {'name': 'Whole Grain Toast with Almond Butter', 'iron_mg': 2.8, 'icon': '🍞'},
            {'name': 'Beetroot & Berry Smoothie', 'iron_mg': 2.5, 'icon': '🥤'},
            {'name': 'Iron-Fortified Cereal with Strawberries', 'iron_mg': 5.0, 'icon': '🥗'},
            {'name': 'Quinoa Porridge with Dates', 'iron_mg': 3.5, 'icon': '🍚'},
            {'name': 'Multigrain Pancakes with Molasses', 'iron_mg': 3.0, 'icon': '🥞'}
        ],
        'lunch': [
            {'name': 'Lentil Soup with Whole Wheat Bread', 'iron_mg': 5.5, 'icon': '🍲'},
            {'name': 'Grilled Chicken Salad with Kale', 'iron_mg': 4.0, 'icon': '🥗'},
            {'name': 'Chickpea & Spinach Curry with Rice', 'iron_mg': 6.0, 'icon': '🍛'},
            {'name': 'Turkey & Bean Wrap', 'iron_mg': 4.5, 'icon': '🌯'},
            {'name': 'Tofu Stir-Fry with Broccoli', 'iron_mg': 5.0, 'icon': '🥦'},
            {'name': 'Black Bean Tacos with Guacamole', 'iron_mg': 4.8, 'icon': '🌮'},
            {'name': 'Salmon & Quinoa Bowl', 'iron_mg': 3.5, 'icon': '🐟'}
        ],
        'dinner': [
            {'name': 'Lean Beef Steak with Sweet Potato', 'iron_mg': 5.5, 'icon': '🥩'},
            {'name': 'Baked Salmon with Asparagus', 'iron_mg': 3.5, 'icon': '🐟'},
            {'name': 'Lamb Chops with Roasted Vegetables', 'iron_mg': 4.5, 'icon': '🍖'},
            {'name': 'Bean & Vegetable Stew', 'iron_mg': 5.0, 'icon': '🍲'},
            {'name': 'Grilled Chicken with Spinach Rice', 'iron_mg': 4.0, 'icon': '🍗'},
            {'name': 'Shrimp Pasta with Sun-dried Tomatoes', 'iron_mg': 3.8, 'icon': '🍝'},
            {'name': 'Pork Tenderloin with Lentils', 'iron_mg': 5.5, 'icon': '🥘'}
        ],
        'snacks': [
            {'name': 'Trail Mix (Nuts, Raisins, Dark Chocolate)', 'iron_mg': 2.5, 'icon': '🥜'},
            {'name': 'Dried Apricots (6 pieces)', 'iron_mg': 1.8, 'icon': '🍑'},
            {'name': 'Pumpkin Seeds (1/4 cup)', 'iron_mg': 2.5, 'icon': '🎃'},
            {'name': 'Dark Chocolate (70%+ cocoa, 1 oz)', 'iron_mg': 3.4, 'icon': '🍫'},
            {'name': 'Roasted Chickpeas', 'iron_mg': 2.0, 'icon': '🫘'},
            {'name': 'Hummus with Carrot Sticks', 'iron_mg': 1.5, 'icon': '🥕'},
            {'name': 'Edamame (1/2 cup)', 'iron_mg': 1.8, 'icon': '🫛'}
        ]
    },
    'Moderate Anemia': {
        'breakfast': [
            {'name': 'Iron-Fortified Cereal with Prune Juice', 'iron_mg': 8.0, 'icon': '🥣'},
            {'name': 'Liver Pâté on Whole Grain Toast', 'iron_mg': 6.5, 'icon': '🍞'},
            {'name': 'Spinach & Red Pepper Scramble', 'iron_mg': 4.5, 'icon': '🥚'},
            {'name': 'Blackstrap Molasses Smoothie', 'iron_mg': 5.0, 'icon': '🥤'},
            {'name': 'Amaranth Porridge with Pomegranate', 'iron_mg': 5.5, 'icon': '🍚'},
            {'name': 'Beetroot Pancakes with Honey', 'iron_mg': 4.0, 'icon': '🥞'},
            {'name': 'Muesli with Dried Figs & Seeds', 'iron_mg': 4.5, 'icon': '🥗'}
        ],
        'lunch': [
            {'name': 'Beef & Bean Chili', 'iron_mg': 8.5, 'icon': '🍲'},
            {'name': 'Oyster & Spinach Risotto', 'iron_mg': 9.0, 'icon': '🦪'},
            {'name': 'Double Lentil Stew with Brown Rice', 'iron_mg': 7.5, 'icon': '🍛'},
            {'name': 'Iron-Rich Buddha Bowl', 'iron_mg': 6.5, 'icon': '🥗'},
            {'name': 'Liver & Onion with Mashed Potatoes', 'iron_mg': 10.0, 'icon': '🥘'},
            {'name': 'Clam Chowder with Crusty Bread', 'iron_mg': 7.0, 'icon': '🍜'},
            {'name': 'Dark Meat Turkey Leg with Quinoa', 'iron_mg': 6.0, 'icon': '🍗'}
        ],
        'dinner': [
            {'name': 'Grilled Organ Meat (Liver) with Vegetables', 'iron_mg': 12.0, 'icon': '🥩'},
            {'name': 'Mussels in White Wine Sauce', 'iron_mg': 7.5, 'icon': '🦪'},
            {'name': 'Lamb Shank with White Beans', 'iron_mg': 8.0, 'icon': '🍖'},
            {'name': 'Venison Stew with Root Vegetables', 'iron_mg': 7.0, 'icon': '🍲'},
            {'name': 'Beef Stir-Fry with Bok Choy', 'iron_mg': 6.5, 'icon': '🥘'},
            {'name': 'Tofu & Tempeh Curry (Double Portion)', 'iron_mg': 8.0, 'icon': '🍛'},
            {'name': 'Duck Breast with Spinach Salad', 'iron_mg': 6.0, 'icon': '🦆'}
        ],
        'snacks': [
            {'name': 'Fortified Energy Bar', 'iron_mg': 4.5, 'icon': '🍫'},
            {'name': 'Tahini & Date Balls', 'iron_mg': 3.0, 'icon': '🥜'},
            {'name': 'Pumpkin Seed Brittle', 'iron_mg': 4.0, 'icon': '🎃'},
            {'name': 'Dried Mulberries (1/4 cup)', 'iron_mg': 2.5, 'icon': '🫐'},
            {'name': 'Cashew & Dark Chocolate Mix', 'iron_mg': 3.5, 'icon': '🍫'},
            {'name': 'Black Bean Brownie', 'iron_mg': 3.0, 'icon': '🧁'},
            {'name': 'Spirulina Smoothie Shot', 'iron_mg': 5.0, 'icon': '🥤'}
        ]
    },
    'Severe Anemia': {
        'breakfast': [
            {'name': 'Double-Fortified Cereal with Prune Juice & Seeds', 'iron_mg': 12.0, 'icon': '🥣'},
            {'name': 'Chicken Liver Scramble with Spinach Toast', 'iron_mg': 10.0, 'icon': '🥚'},
            {'name': 'Iron Warrior Smoothie (Beetroot, Spinach, Molasses)', 'iron_mg': 8.0, 'icon': '🥤'},
            {'name': 'Amaranth & Quinoa Bowl with Pomegranate Seeds', 'iron_mg': 7.5, 'icon': '🍚'},
            {'name': 'Blood Builder Juice (Beetroot, Carrot, Orange)', 'iron_mg': 5.0, 'icon': '🧃'},
            {'name': 'Organ Meat Breakfast Hash', 'iron_mg': 11.0, 'icon': '🥘'},
            {'name': 'Moringa & Spirulina Power Oats', 'iron_mg': 9.0, 'icon': '🥣'}
        ],
        'lunch': [
            {'name': 'Beef Liver & Caramelized Onion with Sweet Potato', 'iron_mg': 15.0, 'icon': '🥩'},
            {'name': 'Triple Bean Power Chili', 'iron_mg': 12.0, 'icon': '🍲'},
            {'name': 'Oysters & Clam Platter with Lemon', 'iron_mg': 14.0, 'icon': '🦪'},
            {'name': 'Iron-Max Buddha Bowl (Tofu, Tempeh, Spinach, Quinoa)', 'iron_mg': 10.0, 'icon': '🥗'},
            {'name': 'Lamb & Lentil Ragu with Whole Wheat Pasta', 'iron_mg': 11.0, 'icon': '🍝'},
            {'name': 'Blood Sausage with Sauerkraut', 'iron_mg': 13.0, 'icon': '🌭'},
            {'name': 'Beef & Organ Meat Stew', 'iron_mg': 14.0, 'icon': '🍖'}
        ],
        'dinner': [
            {'name': 'Grilled Beef Liver with Roasted Vegetables', 'iron_mg': 15.0, 'icon': '🥩'},
            {'name': 'Mussel & Clam Bouillabaisse', 'iron_mg': 12.0, 'icon': '🦪'},
            {'name': 'Venison Steak with Spinach & Lentil Side', 'iron_mg': 11.0, 'icon': '🍖'},
            {'name': 'Lamb Liver Kebabs with Hummus', 'iron_mg': 13.0, 'icon': '🥘'},
            {'name': 'Beef Heart Stir-Fry with Dark Greens', 'iron_mg': 10.0, 'icon': '🥦'},
            {'name': 'Duck Confit with Red Cabbage', 'iron_mg': 8.0, 'icon': '🦆'},
            {'name': 'Fortified Tofu & Tempeh Feast (Vegan Option)', 'iron_mg': 12.0, 'icon': '🍛'}
        ],
        'snacks': [
            {'name': 'Liver Pâté Crackers', 'iron_mg': 5.0, 'icon': '🍪'},
            {'name': 'Iron-Fortified Protein Shake', 'iron_mg': 8.0, 'icon': '🥤'},
            {'name': 'Spirulina & Pumpkin Seed Energy Balls', 'iron_mg': 6.0, 'icon': '🥜'},
            {'name': 'Dark Chocolate (85%+ cocoa, 2 oz)', 'iron_mg': 7.0, 'icon': '🍫'},
            {'name': 'Dried Black Mission Figs', 'iron_mg': 4.0, 'icon': '🫐'},
            {'name': 'Moringa Leaf Tea', 'iron_mg': 3.5, 'icon': '🍵'},
            {'name': 'Beetroot Chips', 'iron_mg': 3.0, 'icon': '🍠'}
        ]
    }
}

# ─── Maternal Mode Additions ─────────────────────────────────────────────────
MATERNAL_ADDITIONS = {
    'extra_snacks': [
        {'name': 'Prenatal Iron Supplement (as prescribed)', 'iron_mg': 27, 'icon': '💊'},
        {'name': 'Folate-Rich Orange Juice', 'iron_mg': 1.0, 'icon': '🍊'},
        {'name': 'Prenatal Smoothie (Spinach, Banana, Flaxseed)', 'iron_mg': 3.5, 'icon': '🥤'}
    ],
    'tips': [
        'Take prenatal iron supplements with vitamin C (not with dairy).',
        'Avoid tea/coffee 1 hour before and after iron-rich meals.',
        'Small, frequent meals help manage nausea while maintaining iron intake.',
        'Include folate-rich foods like leafy greens, citrus, and fortified grains.',
        'Consult your OB-GYN about IV iron if oral supplements cause severe GI distress.'
    ]
}

# ─── Budget Rural Mode ────────────────────────────────────────────────────────
BUDGET_MEALS = {
    'breakfast': [
        {'name': 'Jaggery & Sesame Seed Balls', 'iron_mg': 4.0, 'icon': '🍬', 'cost': 'Very Low'},
        {'name': 'Ragi (Finger Millet) Porridge', 'iron_mg': 3.5, 'icon': '🍚', 'cost': 'Very Low'},
        {'name': 'Moringa Leaf & Onion Omelette', 'iron_mg': 3.0, 'icon': '🥚', 'cost': 'Low'},
        {'name': 'Bajra (Pearl Millet) Roti with Jaggery', 'iron_mg': 4.5, 'icon': '🫓', 'cost': 'Very Low'}
    ],
    'lunch': [
        {'name': 'Rajma (Kidney Bean) Curry with Rice', 'iron_mg': 5.5, 'icon': '🍛', 'cost': 'Low'},
        {'name': 'Palak Dal (Spinach Lentils)', 'iron_mg': 6.0, 'icon': '🍲', 'cost': 'Very Low'},
        {'name': 'Chana (Chickpea) Masala with Roti', 'iron_mg': 5.0, 'icon': '🫓', 'cost': 'Low'},
        {'name': 'Black-Eyed Pea Stew', 'iron_mg': 4.5, 'icon': '🥘', 'cost': 'Low'}
    ],
    'dinner': [
        {'name': 'Amaranth Leaves Stir-Fry with Rice', 'iron_mg': 5.0, 'icon': '🥦', 'cost': 'Very Low'},
        {'name': 'Egg Curry with Drumstick Leaves', 'iron_mg': 4.5, 'icon': '🥚', 'cost': 'Low'},
        {'name': 'Beetroot & Potato Curry', 'iron_mg': 3.5, 'icon': '🍠', 'cost': 'Very Low'},
        {'name': 'Garden Cress Seed (Halim) Ladoo', 'iron_mg': 5.5, 'icon': '🍬', 'cost': 'Very Low'}
    ],
    'snacks': [
        {'name': 'Peanut & Jaggery Chikki', 'iron_mg': 2.5, 'icon': '🥜', 'cost': 'Very Low'},
        {'name': 'Roasted Bengal Gram', 'iron_mg': 2.0, 'icon': '🫘', 'cost': 'Very Low'},
        {'name': 'Amla (Indian Gooseberry) – 2 pieces', 'iron_mg': 1.2, 'icon': '🍈', 'cost': 'Very Low'},
        {'name': 'Dates (3 pieces)', 'iron_mg': 1.5, 'icon': '🌴', 'cost': 'Very Low'}
    ]
}

# ─── Foods to Avoid ──────────────────────────────────────────────────────────
FOODS_TO_AVOID = [
    {'name': 'Tea & Coffee (with meals)', 'reason': 'Tannins inhibit iron absorption by 60-70%', 'icon': '☕'},
    {'name': 'Calcium-rich foods (with iron meals)', 'reason': 'Calcium competes with iron for absorption', 'icon': '🥛'},
    {'name': 'Whole grains in excess', 'reason': 'Phytic acid in bran can bind to iron', 'icon': '🌾'},
    {'name': 'Soy products (with iron meals)', 'reason': 'Phytates in soy reduce iron bioavailability', 'icon': '🫘'},
    {'name': 'Antacids', 'reason': 'Reduce stomach acid needed for iron absorption', 'icon': '💊'},
    {'name': 'Red wine', 'reason': 'Polyphenols can inhibit non-heme iron absorption', 'icon': '🍷'},
    {'name': 'Processed foods', 'reason': 'Low nutritional value, may displace iron-rich foods', 'icon': '🍔'}
]

# ─── Iron Absorption Tips ────────────────────────────────────────────────────
ABSORPTION_TIPS = [
    {'tip': 'Pair iron-rich foods with Vitamin C sources (citrus, bell peppers, tomatoes)', 'icon': '🍊'},
    {'tip': 'Cook in cast iron cookware to increase iron content of food', 'icon': '🍳'},
    {'tip': 'Separate calcium supplements from iron-rich meals by 2 hours', 'icon': '⏰'},
    {'tip': 'Soak, sprout, or ferment grains and legumes to reduce phytic acid', 'icon': '🌱'},
    {'tip': 'Include heme iron (meat sources) which is 2-3x more bioavailable', 'icon': '🥩'},
    {'tip': 'Avoid tea/coffee 1 hour before and after iron-rich meals', 'icon': '☕'},
    {'tip': 'Take iron supplements on empty stomach for best absorption', 'icon': '💊'},
    {'tip': 'Include beta-carotene foods (sweet potato, carrots) to enhance absorption', 'icon': '🥕'}
]


def get_iron_target(severity, gender, pregnant):
    """Get recommended daily iron intake in mg."""
    targets = IRON_TARGETS.get(severity, IRON_TARGETS['Normal'])
    if pregnant:
        return targets['pregnant']
    elif gender == 0:
        return targets['male']
    else:
        return targets['female']


def get_diet_plan(severity, gender, pregnant, budget_mode=False):
    """
    Generate a complete personalized diet plan.

    Args:
        severity: str – 'Normal', 'Mild Anemia', 'Moderate Anemia', 'Severe Anemia'
        gender: int – 0=Male, 1=Female
        pregnant: int – 0=No, 1=Yes
        budget_mode: bool – Use budget-friendly options

    Returns:
        Complete diet plan dict
    """
    iron_target = get_iron_target(severity, gender, pregnant)

    # Get meal plan for severity (fallback to Mild for Normal)
    if severity == 'Normal':
        meals = MEAL_PLANS['Mild Anemia']
    else:
        meals = MEAL_PLANS.get(severity, MEAL_PLANS['Mild Anemia'])

    # Override with budget meals if requested
    if budget_mode:
        meals = BUDGET_MEALS

    plan = {
        'severity': severity,
        'iron_target_mg': iron_target,
        'hemoglobin_goal': _get_hb_goal(severity, gender, pregnant),
        'meals': meals,
        'foods_to_avoid': FOODS_TO_AVOID,
        'absorption_tips': ABSORPTION_TIPS,
        'is_maternal': bool(pregnant),
        'is_budget': budget_mode,
        'maternal_additions': MATERNAL_ADDITIONS if pregnant else None,
        'daily_iron_summary': _calculate_daily_iron(meals),
        'weekly_plan': _build_weekly_plan(meals)
    }

    return plan


def _get_hb_goal(severity, gender, pregnant):
    """Get target hemoglobin improvement goal."""
    goals = {
        'Normal': {'target': 'Maintain current levels', 'timeline': 'Ongoing'},
        'Mild Anemia': {'target': '+1-2 g/dL improvement', 'timeline': '4-6 weeks'},
        'Moderate Anemia': {'target': '+2-4 g/dL improvement', 'timeline': '8-12 weeks'},
        'Severe Anemia': {'target': '+4-6 g/dL improvement', 'timeline': '12-16 weeks (with medical supervision)'}
    }
    return goals.get(severity, goals['Normal'])


def _calculate_daily_iron(meals):
    """Calculate average daily iron intake from meal plan."""
    total = 0
    for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
        if meal_type in meals:
            avg = sum(m['iron_mg'] for m in meals[meal_type]) / len(meals[meal_type])
            total += avg
    return round(total, 1)


def _build_weekly_plan(meals):
    """Build a 7-day rotation from the meal options."""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly = []

    for i, day in enumerate(days):
        day_plan = {}
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
            if meal_type in meals:
                items = meals[meal_type]
                day_plan[meal_type] = items[i % len(items)]
        weekly.append({'day': day, 'meals': day_plan})

    return weekly
