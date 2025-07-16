# FitPlay - Gamified Fitness Platform

## Overview

FitPlay is a gamified fitness platform designed to make physical exercise fun and engaging, particularly targeting youth and low-income users. The platform combines fitness tracking with interactive JavaScript games, reward systems, and personalized diet recommendations. It's built as a Flask web application with a focus on accessibility and user engagement.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Python Flask with modular blueprint structure
- **Session Management**: Flask-Session with filesystem-based storage
- **Data Models**: Dataclass-based models (User, Activity, Badge) stored in session
- **Deployment**: WSGI-compatible with ProxyFix middleware for production

### Frontend Architecture
- **UI Framework**: Bootstrap 5 for responsive design
- **JavaScript**: Vanilla JavaScript with class-based organization
- **Data Visualization**: Chart.js for progress tracking
- **Icons**: Font Awesome for consistent iconography

### Application Structure
The application is organized into modular blueprints:
- `main`: Core routes (home, profile, leaderboard)
- `games`: Fitness game functionality
- `dashboard`: Statistics and progress tracking
- `diet`: Personalized nutrition recommendations

## Key Components

### Session-Based User Management
- No database required - all user data stored in Flask sessions
- Automatic session initialization for guest users
- User profiles include fitness goals, age, weight, and activity history

### Gamification System
- Points system for completed activities
- Badge achievements with specific requirements
- Leaderboard functionality with mock competitive data
- Progress tracking across multiple metrics

### Fitness Games
- Interactive exercise-based mini-games (squats, jumps, planks, burpees)
- Real-time score tracking and point calculation
- Calorie burn estimation based on activity type and duration
- Usage limit enforcement (2-hour daily limit)

### Diet Recommendations
- Personalized meal plans based on user profile
- Goal-specific nutrition advice (weight loss, muscle gain, maintenance)
- Calorie calculation using simplified BMR formulas
- Meal timing and hydration suggestions

## Data Flow

### User Session Flow
1. User visits site → Session automatically initialized with default values
2. User updates profile → Session data updated, diet plan regenerated
3. User plays games → Points, calories, and activity time tracked in session
4. User views dashboard → Session data aggregated and displayed with charts

### Game Flow
1. User starts game → Game session created, daily usage incremented
2. User performs exercise → Score updated via AJAX calls
3. User ends game → Points and calories calculated, badges checked, session updated

### Dashboard Flow
1. User views dashboard → Session data transformed into weekly progress charts
2. Auto-refresh functionality updates statistics periodically
3. Recent activities displayed from session activity log

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: UI components and responsive grid system
- **Chart.js**: Progress visualization and weekly tracking charts
- **Font Awesome**: Icon library for consistent visual elements

### Backend Dependencies
- **Flask**: Web framework and routing
- **Flask-Session**: Session management with filesystem storage
- **Werkzeug**: WSGI utilities and ProxyFix for deployment

### CDN Resources
All frontend dependencies loaded via CDN for simplicity and reduced bundle size.

## Deployment Strategy

### Development Setup
- Flask development server with debug mode enabled
- Session files stored in filesystem (temporary directory)
- Environment variables for session secrets

### Production Considerations
- ProxyFix middleware configured for reverse proxy deployment
- Session secret configurable via environment variables
- Static files served via Flask (can be offloaded to CDN)
- No database dependencies simplify deployment

### Scalability Limitations
- Session-based storage limits horizontal scaling
- No persistent data storage means user progress lost on session expiry
- Mock leaderboard data doesn't reflect real user competition

## Architecture Decisions

### Session-Based Storage
**Problem**: Need user data persistence without database complexity
**Solution**: Flask-Session with filesystem storage
**Rationale**: Simplifies deployment and development while maintaining user state
**Trade-offs**: Limited scalability, temporary data persistence

### Blueprint Modular Structure
**Problem**: Organize growing application functionality
**Solution**: Separate blueprints for major feature areas
**Rationale**: Improves code organization and maintainability
**Trade-offs**: Slight complexity increase for simple features

### Client-Side Game Logic
**Problem**: Create responsive, interactive fitness games
**Solution**: Vanilla JavaScript with class-based organization
**Rationale**: Reduces server load and provides immediate user feedback
**Trade-offs**: Potential for client-side manipulation, limited offline capability

### Mock Data for Social Features
**Problem**: Demonstrate leaderboard and competitive features
**Solution**: Generate mock leaderboard data relative to user's score
**Rationale**: Showcases functionality without requiring multiple real users
**Trade-offs**: Not truly competitive, may mislead users about actual ranking