import streamlit as st
from collections import defaultdict
from datetime import datetime

class Analytics:
    def calculate_results(self, questions, answers):
        """Calculate comprehensive exam results"""
        total_questions = len(questions)
        correct_answers = 0
        
        # Topic-wise analysis
        topic_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        # Difficulty-wise analysis  
        difficulty_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        # Process each question
        for i, question in enumerate(questions):
            topic = question['topic']
            difficulty = question['difficulty']
            user_answer = answers.get(i)
            
            # Update totals
            topic_stats[topic]['total'] += 1
            difficulty_stats[difficulty]['total'] += 1
            
            # Check if correct
            if user_answer is not None and user_answer == question['correct']:
                correct_answers += 1
                topic_stats[topic]['correct'] += 1
                difficulty_stats[difficulty]['correct'] += 1
        
        # Calculate percentages
        percentage = (correct_answers / total_questions) * 100
        
        # Format topic analysis
        topic_analysis = {}
        for topic, stats in topic_stats.items():
            topic_analysis[topic] = {
                'correct': stats['correct'],
                'total': stats['total'],
                'percentage': (stats['correct'] / stats['total']) * 100
            }
        
        # Format difficulty analysis
        difficulty_analysis = {}
        for difficulty, stats in difficulty_stats.items():
            difficulty_analysis[difficulty] = {
                'correct': stats['correct'],
                'total': stats['total'],
                'percentage': (stats['correct'] / stats['total']) * 100
            }
        
        # Calculate time taken
        time_taken = "N/A"
        if 'start_time' in st.session_state and st.session_state.start_time:
            elapsed = datetime.now() - st.session_state.start_time
            hours = elapsed.seconds // 3600
            minutes = (elapsed.seconds % 3600) // 60
            time_taken = f"{hours:02d}:{minutes:02d}"
        
        return {
            'score': correct_answers,
            'total_questions': total_questions,
            'percentage': percentage,
            'topic_analysis': topic_analysis,
            'difficulty_analysis': difficulty_analysis,
            'time_taken': time_taken,
            'answered_questions': len(answers),
            'unanswered_questions': total_questions - len(answers)
        }
    
    def get_performance_insights(self, results):
        """Generate performance insights and recommendations"""
        insights = []
        
        percentage = results['percentage']
        
        # Overall performance insight
        if percentage >= 90:
            insights.append("🌟 Excellent! You have mastery-level understanding.")
        elif percentage >= 80:
            insights.append("👍 Very good! You're well-prepared for the certification.")
        elif percentage >= 70:
            insights.append("✅ Good job! You meet the passing criteria.")
        else:
            insights.append("⚠️ More preparation needed. Focus on weak areas.")
        
        # Topic-specific insights
        if 'topic_analysis' in results:
            weak_topics = [
                topic for topic, data in results['topic_analysis'].items()
                if data['percentage'] < 70
            ]
            
            if weak_topics:
                insights.append(f"📚 Study these topics: {', '.join(weak_topics)}")
            
            # Best performing topic
            best_topic = max(
                results['topic_analysis'].items(),
                key=lambda x: x[1]['percentage']
            )
            insights.append(f"💪 Strongest area: {best_topic[0]} ({best_topic[1]['percentage']:.1f}%)")
        
        # Difficulty-based insights
        if 'difficulty_analysis' in results:
            for difficulty, data in results['difficulty_analysis'].items():
                if data['percentage'] < 60:
                    insights.append(f"🎯 Practice more {difficulty} questions")
        
        return insights
    
    def export_results_json(self, results):
        """Export results as JSON"""
        import json
        
        export_data = {
            'exam_date': datetime.now().isoformat(),
            'results': results,
            'questions_data': [
                {
                    'question_id': i + 1,
                    'topic': q['topic'],
                    'difficulty': q['difficulty'],
                    'user_answer': st.session_state.answers.get(i),
                    'correct_answer': q['correct'],
                    'is_correct': st.session_state.answers.get(i) == q['correct'] if i in st.session_state.answers else None
                }
                for i, q in enumerate(st.session_state.questions)
            ]
        }
        
        return json.dumps(export_data, indent=2)
