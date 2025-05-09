from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'food_labeling_app_secret_key'

# Load label data from JSON file
with open('static/data/labels.json', 'r') as f:
    label_data = json.load(f)

# Load quiz data from JSON file
with open('static/data/quiz.json', 'r') as f:
    quiz_data = json.load(f)

# User data storage (in a real app this would be in a database)
user_data = {
    'current_session': None,
    'sessions': {}
}

@app.route('/')
def home():
    # Create a new session ID based on timestamp
    session_id = str(datetime.now().timestamp())
    
    # Initialize session data
    user_data['current_session'] = session_id
    user_data['sessions'][session_id] = {
        'start_time': datetime.now().isoformat(),
        'lesson_views': {},
        'quiz_answers': {},
        'quiz_score': 0
    }
    
    # Store session ID in Flask session
    session['user_session'] = session_id
    
    return render_template('index.html')

@app.route('/learn_overview')
def learn_overview():
    # Get current session
    session_id = session.get('user_session')
    if not session_id or session_id not in user_data['sessions']:
        return redirect(url_for('home'))
    
    return render_template('learn_overview.html')

@app.route('/learn/<int:label_id>')
def learn(label_id):
    # Get current session
    session_id = session.get('user_session')
    if not session_id or session_id not in user_data['sessions']:
        return redirect(url_for('home'))
    
    # Record page view time
    user_data['sessions'][session_id]['lesson_views'][label_id] = datetime.now().isoformat()
    
    # Check if we have this label
    if label_id < 0 or label_id >= len(label_data):
        return redirect(url_for('home'))
    
    current_label = label_data[label_id]
    
    # Determine next and previous label IDs
    prev_id = label_id - 1 if label_id > 0 else None
    next_id = label_id + 1 if label_id < len(label_data) - 1 else None
    
    # If this is the last label, next goes to quiz
    if next_id is None and label_id == len(label_data) - 1:
        next_url = url_for('quiz_intro')
    else:
        next_url = url_for('learn', label_id=next_id) if next_id is not None else None
    
    prev_url = url_for('learn', label_id=prev_id) if prev_id is not None else None
    
    return render_template(
        'learn.html',
        label=current_label,
        label_id=label_id,
        next_url=next_url,
        prev_url=prev_url,
        total_labels=len(label_data)
    )

@app.route('/quiz_intro')
def quiz_intro():
    # Get current session
    session_id = session.get('user_session')
    if not session_id or session_id not in user_data['sessions']:
        return redirect(url_for('home'))
    
    return render_template('quiz_intro.html')

@app.route('/quiz/<int:question_id>', methods=['GET', 'POST'])
def quiz(question_id):
    # Get current session
    session_id = session.get('user_session')
    if not session_id or session_id not in user_data['sessions']:
        return redirect(url_for('home'))
    
    # Check if we have this question
    if question_id < 0 or question_id >= len(quiz_data):
        return redirect(url_for('home'))
    
    # Handle form submission (POST request)
    if request.method == 'POST':
        selected_options = request.form.getlist('answers')
        
        # Store the user's answer
        user_data['sessions'][session_id]['quiz_answers'][question_id] = selected_options
        
        # Redirect to next question or results
        next_question = question_id + 1
        if next_question < len(quiz_data):
            return redirect(url_for('quiz', question_id=next_question))
        else:
            # Calculate score and redirect to results
            calculate_score(session_id)
            return redirect(url_for('results'))
    
    # For GET request, show the quiz question
    current_question = quiz_data[question_id]
    
    return render_template(
        'quiz.html',
        question=current_question,
        question_id=question_id,
        total_questions=len(quiz_data)
    )

def calculate_score(session_id):
    """Calculate the user's quiz score"""
    if session_id not in user_data['sessions']:
        return
    
    user_session = user_data['sessions'][session_id]
    total_correct = 0
    total_possible = len(quiz_data)
    
    for q_id, question in enumerate(quiz_data):
        user_answers = set(user_session['quiz_answers'].get(q_id, []))
        correct_answers = set(str(i) for i, is_correct in enumerate(question['correct_answers']) if is_correct)
        
        # For partial credit, calculate how many correct options they selected
        correct_selections = len(user_answers.intersection(correct_answers))
        total_correct_options = len(correct_answers)
        
        if correct_selections > 0:
            # Award partial credit based on correct selections
            question_score = correct_selections / total_correct_options
            total_correct += question_score
    
    # Store the score as a percentage
    user_session['quiz_score'] = round((total_correct / total_possible) * 100)

@app.route('/results')
def results():
    # Get current session
    session_id = session.get('user_session')
    if not session_id or session_id not in user_data['sessions']:
        return redirect(url_for('home'))
    
    user_session = user_data['sessions'][session_id]
    score = user_session['quiz_score']
    
    # Analyze quiz answers to provide feedback
    feedback = []
    for q_id, question in enumerate(quiz_data):
        user_answers = set(user_session['quiz_answers'].get(q_id, []))
        correct_answers = set(str(i) for i, is_correct in enumerate(question['correct_answers']) if is_correct)
        
        if user_answers != correct_answers:
            feedback.append({
                'question': question['question'],
                'correct_options': [question['options'][int(i)] for i in correct_answers]
            })
    
    return render_template('results.html', score=score, feedback=feedback)

@app.route('/api/user_data')
def get_user_data():
    """API endpoint to get the current user's data (for debugging)"""
    session_id = session.get('user_session')
    if not session_id or session_id not in user_data['sessions']:
        return jsonify({'error': 'No active session'})
    
    return jsonify(user_data['sessions'][session_id])

if __name__ == '__main__':
    # Create necessary directories if they don't exist
    os.makedirs('static/data', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Check if label data file exists, if not create it
    if not os.path.exists('static/data/labels.json'):
        with open('static/data/labels.json', 'w') as f:
            json.dump([
                {
                    "name": "bioengineered",
                    "title": "Bioengineered/GMO",
                    "description": "Contains ingredients that have been genetically modified",
                    "image_url": "/static/images/bioengineered.jpg",
                    "identifiers": [
                        "5-digit PLU code starting with 8",
                        "Bioengineered disclosure symbol"
                    ]
                },
                {
                    "name": "conventional",
                    "title": "Conventional",
                    "description": "Standard commercially grown produce that may use pesticides and fertilizers",
                    "image_url": "/static/images/conventional.jpg",
                    "identifiers": [
                        "4-digit PLU code starting with 3 or 4",
                        "No special labels"
                    ]
                },
                {
                    "name": "local",
                    "title": "Local",
                    "description": "Grown within a defined local region (usually 100-400 miles)",
                    "image_url": "/static/images/local.jpg",
                    "identifiers": [
                        "Locally grown stickers"
                    ]
                },
                {
                    "name": "non-gmo",
                    "title": "Non-GMO",
                    "description": "Made without genetically modified ingredients but may still use conventional farming methods",
                    "image_url": "/static/images/non-gmo.jpg",
                    "identifiers": [
                        "Non-GMO Project - Verified seal"
                    ]
                },
                {
                    "name": "nutrition",
                    "title": "Nutrition Claims",
                    "description": "Labels that provide information about nutritional content",
                    "image_url": "/static/images/nutrition.jpg",
                    "identifiers": [
                        "Good source (10-19% of Daily Value)",
                        "High in (20% or more of Daily Value)",
                        "Light in (20% or less of Daily Value)"
                    ]
                },
                {
                    "name": "organic",
                    "title": "Organic",
                    "description": "Grown without synthetic pesticides or fertilizers, no GMOs, and meets USDA standards",
                    "image_url": "/static/images/organic.jpg",
                    "identifiers": [
                        "USDA Organic seal",
                        "5-digit PLU code starting with 9"
                    ]
                }
            ], f)
    
    # Check if quiz data file exists, if not create it
    if not os.path.exists('static/data/quiz.json'):
        with open('static/data/quiz.json', 'w') as f:
            json.dump([
                {
                    "question": "Which of these items are organic?",
                    "options": [
                        "Bananas with a sticker that has a 5-digit code starting with 9",
                        "Apples with a sticker that has a 4-digit code starting with 4",
                        "Vegetables with the USDA Organic seal",
                        "Products with the Non-GMO Project seal"
                    ],
                    "correct_answers": [true, false, true, false],
                    "image_url": "/static/images/quiz_organic.jpg"
                },
                {
                    "question": "Which of these items are conventionally grown?",
                    "options": [
                        "Produce with a 4-digit PLU code starting with 3 or 4",
                        "Products with no special labels",
                        "Products with the Non-GMO Project seal",
                        "Produce with a 5-digit PLU code starting with 9"
                    ],
                    "correct_answers": [true, true, false, false],
                    "image_url": "/static/images/quiz_conventional.jpg"
                }
            ], f)
    
    app.run(debug=True)