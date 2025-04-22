from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Load data (lessons + quiz) once
with open('static/data/data.json') as f:
    app_data = json.load(f)

@app.route('/')
def home():
    # start fresh
    session.clear()
    session['learn_history'] = []
    session['quiz_answers'] = {}
    return render_template('home.html', body_id='home-page')

@app.route('/learn/<int:lesson_id>')
def learn(lesson_id):
    # record entry time
    history = session.get('learn_history', [])
    history.append({ 'lesson_id': lesson_id,
                     'timestamp': datetime.utcnow().isoformat() })
    session['learn_history'] = history

    total = len(app_data['lessons'])
    if not (1 <= lesson_id <= total):
        return redirect(url_for('learn', lesson_id=1))
    return render_template('learn.html', lesson_id=lesson_id,
                                           total_lessons=total,
                                           body_id='learn-page')

@app.route('/quiz/<int:quiz_id>', methods=['GET','POST'])
def quiz(quiz_id):
    total = len(app_data['quiz'])
    if request.method == 'POST':
        answers = session.get('quiz_answers', {})
        answers[str(quiz_id)] = request.form.get('answer', '')
        session['quiz_answers'] = answers
        next_id = quiz_id + 1
        if next_id > total:
            return redirect(url_for('quiz_result'))
        return redirect(url_for('quiz', quiz_id=next_id))

    if not (1 <= quiz_id <= total):
        return redirect(url_for('quiz', quiz_id=1))
    return render_template('quiz.html', quiz_id=quiz_id,
                                          total_quiz=total,
                                          body_id='quiz-page')

@app.route('/quiz/result')
def quiz_result():
    answers = session.get('quiz_answers', {})
    results = []
    score = 0
    for q in app_data['quiz']:
        qid = str(q['id'])
        user = answers.get(qid, '').strip()
        correct = q['answer'].strip()
        ok = user.lower() == correct.lower()
        results.append({ 'question': q['question'],
                         'user': user,
                         'correct': correct,
                         'is_correct': ok })
        if ok:
            score += 1
    return render_template('result.html', results=results,
                                            score=score,
                                            total=len(app_data['quiz']),
                                            body_id='result-page')

@app.route('/data')
def data():
    return jsonify(app_data)

if __name__ == '__main__':
    app.run(debug=True)