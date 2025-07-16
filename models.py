from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class User:
    user_id: str
    username: str
    points: int
    badges: List[str]
    workouts_completed: int
    calories_burned: int
    time_active: int
    daily_usage: int
    last_activity: str
    activities: List[Dict[str, Any]]
    age: int
    weight: float
    fitness_goal: str
    diet_plan: List[Dict[str, Any]]

@dataclass
class Activity:
    activity_id: str
    user_id: str
    activity_type: str
    duration: int
    points_earned: int
    timestamp: str
    details: Dict[str, Any]

@dataclass
class Badge:
    badge_id: str
    name: str
    description: str
    icon: str
    requirement: str

# Badge definitions
BADGES = {
    'first_workout': Badge('first_workout', 'First Steps', 'Completed your first workout!', 'fa-trophy', 'Complete 1 workout'),
    'workout_streak': Badge('workout_streak', 'Streak Master', 'Completed 7 workouts in a row!', 'fa-fire', 'Complete 7 workouts'),
    'calorie_burner': Badge('calorie_burner', 'Calorie Crusher', 'Burned 1000 calories total!', 'fa-burn', 'Burn 1000 calories'),
    'time_warrior': Badge('time_warrior', 'Time Warrior', 'Active for 60 minutes total!', 'fa-clock', 'Be active for 60 minutes'),
    'game_master': Badge('game_master', 'Game Master', 'Played 10 fitness games!', 'fa-gamepad', 'Play 10 games'),
    'points_collector': Badge('points_collector', 'Points Collector', 'Earned 500 points!', 'fa-star', 'Earn 500 points')
}

# Diet recommendations
DIET_RECOMMENDATIONS = {
    'weight_loss': {
        'breakfast': ['Oatmeal with fruits', 'Greek yogurt with berries', 'Scrambled eggs with vegetables'],
        'lunch': ['Grilled chicken salad', 'Vegetable soup', 'Quinoa bowl with vegetables'],
        'dinner': ['Baked fish with vegetables', 'Lean protein with steamed broccoli', 'Vegetable stir-fry'],
        'snacks': ['Apple slices', 'Carrot sticks', 'Handful of nuts']
    },
    'muscle_gain': {
        'breakfast': ['Protein smoothie', 'Eggs with whole grain toast', 'Greek yogurt with granola'],
        'lunch': ['Grilled chicken with rice', 'Protein-rich sandwich', 'Quinoa salad with beans'],
        'dinner': ['Lean beef with sweet potato', 'Salmon with brown rice', 'Chicken with pasta'],
        'snacks': ['Protein bar', 'Cottage cheese', 'Mixed nuts']
    },
    'maintenance': {
        'breakfast': ['Balanced cereal with milk', 'Toast with avocado', 'Fruit smoothie'],
        'lunch': ['Balanced meal with protein and carbs', 'Chicken wrap', 'Soup with bread'],
        'dinner': ['Balanced dinner plate', 'Pasta with vegetables', 'Rice bowl with protein'],
        'snacks': ['Fruits', 'Yogurt', 'Crackers']
    }
}
