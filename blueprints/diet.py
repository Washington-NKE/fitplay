from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from models import DIET_RECOMMENDATIONS
import random

diet_bp = Blueprint('diet', __name__)

@diet_bp.route('/')
def diet():
    current_plan = get_personalized_diet_plan()
    return render_template('diet.html', diet_plan=current_plan)

@diet_bp.route('/update_goals', methods=['POST'])
def update_goals():
    age = int(request.form.get('age', session.get('age', 18)))
    weight = float(request.form.get('weight', session.get('weight', 70)))
    fitness_goal = request.form.get('fitness_goal', session.get('fitness_goal', 'weight_loss'))
    
    session['age'] = age
    session['weight'] = weight
    session['fitness_goal'] = fitness_goal
    
    # Generate new diet plan
    new_plan = get_personalized_diet_plan()
    session['diet_plan'] = new_plan
    
    flash('Diet plan updated successfully!', 'success')
    return redirect(url_for('diet.diet'))

@diet_bp.route('/generate_plan')
def generate_plan():
    """Generate a new personalized diet plan"""
    plan = get_personalized_diet_plan()
    session['diet_plan'] = plan
    return jsonify(plan)

def get_personalized_diet_plan():
    """Generate personalized diet recommendations based on user profile"""
    age = session.get('age', 18)
    weight = session.get('weight', 70)
    fitness_goal = session.get('fitness_goal', 'weight_loss')
    
    # Get base recommendations
    base_recommendations = DIET_RECOMMENDATIONS.get(fitness_goal, DIET_RECOMMENDATIONS['maintenance'])
    
    # Calculate daily calorie needs (simplified formula)
    if age < 25:
        bmr = 1800 if fitness_goal == 'muscle_gain' else 1500
    else:
        bmr = 1700 if fitness_goal == 'muscle_gain' else 1400
    
    # Adjust for weight
    calorie_adjustment = (weight - 70) * 10
    daily_calories = bmr + calorie_adjustment
    
    # Adjust for fitness goal
    if fitness_goal == 'weight_loss':
        daily_calories -= 200
    elif fitness_goal == 'muscle_gain':
        daily_calories += 300
    
    # Generate personalized plan
    plan = {
        'daily_calories': int(daily_calories),
        'goal': fitness_goal.replace('_', ' ').title(),
        'meals': {
            'breakfast': {
                'options': base_recommendations['breakfast'],
                'selected': random.choice(base_recommendations['breakfast']),
                'calories': int(daily_calories * 0.25)
            },
            'lunch': {
                'options': base_recommendations['lunch'],
                'selected': random.choice(base_recommendations['lunch']),
                'calories': int(daily_calories * 0.35)
            },
            'dinner': {
                'options': base_recommendations['dinner'],
                'selected': random.choice(base_recommendations['dinner']),
                'calories': int(daily_calories * 0.30)
            },
            'snacks': {
                'options': base_recommendations['snacks'],
                'selected': random.choice(base_recommendations['snacks']),
                'calories': int(daily_calories * 0.10)
            }
        },
        'tips': get_diet_tips(fitness_goal, age),
        'water_intake': calculate_water_intake(weight),
        'meal_timing': get_meal_timing_suggestions()
    }
    
    return plan

def get_diet_tips(fitness_goal, age):
    """Get personalized diet tips"""
    tips = []
    
    if fitness_goal == 'weight_loss':
        tips.extend([
            "Eat smaller, more frequent meals",
            "Drink water before meals",
            "Include protein in every meal",
            "Avoid sugary drinks",
            "Choose whole grains over refined carbs"
        ])
    elif fitness_goal == 'muscle_gain':
        tips.extend([
            "Consume protein within 30 minutes after workout",
            "Include complex carbohydrates for energy",
            "Eat every 3-4 hours",
            "Don't skip breakfast",
            "Stay hydrated throughout the day"
        ])
    else:  # maintenance
        tips.extend([
            "Maintain balanced portions",
            "Include variety in your diet",
            "Listen to your hunger cues",
            "Stay consistent with meal times",
            "Enjoy treats in moderation"
        ])
    
    if age < 25:
        tips.append("Focus on nutrient-dense foods for growth and development")
    
    return tips[:5]  # Return top 5 tips

def calculate_water_intake(weight):
    """Calculate recommended daily water intake"""
    return round(weight * 0.033, 1)  # 33ml per kg body weight

def get_meal_timing_suggestions():
    """Get meal timing suggestions"""
    return {
        'breakfast': '7:00 AM - 8:00 AM',
        'lunch': '12:00 PM - 1:00 PM',
        'dinner': '6:00 PM - 7:00 PM',
        'snacks': '10:00 AM, 3:00 PM'
    }
