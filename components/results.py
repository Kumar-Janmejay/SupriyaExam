import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.analytics import Analytics

class Results:
    def show_results(self):
        """Display comprehensive exam results"""
        if 'results' not in st.session_state:
            st.error("No results available. Please take the exam first.")
            return
        
        results = st.session_state.results
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>📊 Exam Results</h1>
            <h3>Detailed Performance Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Overall Score
        self.show_score_summary(results)
        
        # Performance Charts
        self.show_performance_charts(results)
        
        # Topic Analysis
        self.show_topic_analysis(results)
        
        # Detailed Question Review
        self.show_question_review(results)
        
        # Action Buttons
        self.show_action_buttons()
    
    def show_score_summary(self, results):
        """Show overall score summary"""
        score = results['score']
        total = results['total_questions']
        percentage = results['percentage']
        
        # Determine grade and color
        if percentage >= 70:
            grade = "PASS ✅"
            color = "#4CAF50"
        else:
            grade = "FAIL ❌" 
            color = "#F44336"
        
        # Score display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Final Score",
                value=f"{score}/{total}",
                delta=f"{percentage:.1f}%"
            )
        
        with col2:
            st.markdown(f"""
            <div style="background: {color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                <h2>{grade}</h2>
                <p>Passing Score: 70%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.metric(
                label="Time Taken",
                value=results.get('time_taken', 'N/A')
            )
        
        with col4:
            st.metric(
                label="Accuracy",
                value=f"{percentage:.1f}%"
            )
    
    def show_performance_charts(self, results):
        """Show performance visualization charts"""
        st.markdown("## 📈 Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution pie chart
            fig_pie = go.Figure(data=[
                go.Pie(
                    labels=['Correct', 'Incorrect'],
                    values=[results['score'], results['total_questions'] - results['score']],
                    hole=.3,
                    marker_colors=['#4CAF50', '#F44336']
                )
            ])
            fig_pie.update_layout(
                title="Overall Score Distribution",
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Difficulty-wise performance
            if 'difficulty_analysis' in results:
                diff_data = results['difficulty_analysis']
                
                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=list(diff_data.keys()),
                        y=[data['percentage'] for data in diff_data.values()],
                        marker_color=['#4CAF50', '#FF9800', '#F44336'],
                        text=[f"{data['correct']}/{data['total']}" for data in diff_data.values()],
                        textposition='auto'
                    )
                ])
                fig_bar.update_layout(
                    title="Performance by Difficulty",
                    xaxis_title="Difficulty Level",
                    yaxis_title="Accuracy (%)",
                    height=400
                )
                st.plotly_chart(fig_bar, use_container_width=True)
    
    def show_topic_analysis(self, results):
        """Show detailed topic-wise analysis"""
        st.markdown("## 📚 Topic-wise Analysis")
        
        if 'topic_analysis' not in results:
            st.warning("Topic analysis not available.")
            return
        
        topic_data = results['topic_analysis']
        
        # Create DataFrame for better display
        topic_df = pd.DataFrame([
            {
                'Topic': topic,
                'Correct': data['correct'],
                'Total': data['total'],
                'Accuracy (%)': data['percentage'],
                'Status': '✅ Strong' if data['percentage'] >= 70 else '⚠️ Needs Improvement'
            }
            for topic, data in topic_data.items()
        ]).sort_values('Accuracy (%)', ascending=False)
        
        # Display as interactive table
        st.dataframe(
            topic_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Weak areas identification
        weak_topics = [
            topic for topic, data in topic_data.items()
            if data['percentage'] < 70
        ]
        
        if weak_topics:
            st.markdown("### 🎯 Areas for Improvement")
            st.error(f"Focus on these topics: {', '.join(weak_topics)}")
            
            # Show improvement suggestions
            for topic in weak_topics:
                data = topic_data[topic]
                st.warning(f"**{topic}**: {data['correct']}/{data['total']} correct ({data['percentage']:.1f}%)")
        else:
            st.success("🎉 Excellent! You've performed well across all topics.")
        
        # Topic performance chart
        if len(topic_data) > 1:
            fig_topics = px.bar(
                topic_df,
                x='Topic',
                y='Accuracy (%)',
                color='Accuracy (%)',
                color_continuous_scale=['red', 'yellow', 'green'],
                title="Topic-wise Performance Overview"
            )
            fig_topics.update_layout(height=500)
            st.plotly_chart(fig_topics, use_container_width=True)
    
    def show_question_review(self, results):
        """Show detailed question-by-question review"""
        st.markdown("## 🔍 Detailed Question Review")
        
        # Filter options
        review_filter = st.selectbox(
            "Show questions:",
            ["All Questions", "Incorrect Only", "Correct Only", "Marked for Review"]
        )
        
        questions = st.session_state.questions
        answers = st.session_state.answers
        marked = st.session_state.marked_for_review
        
        # Filter questions based on selection
        filtered_questions = []
        
        for i, question in enumerate(questions):
            user_answer = answers.get(i)
            is_correct = user_answer == question['correct']
            is_marked = i in marked
            
            include = False
            if review_filter == "All Questions":
                include = True
            elif review_filter == "Incorrect Only":
                include = user_answer is not None and not is_correct
            elif review_filter == "Correct Only":
                include = user_answer is not None and is_correct
            elif review_filter == "Marked for Review":
                include = is_marked
            
            if include:
                filtered_questions.append((i, question, user_answer, is_correct, is_marked))
        
        if not filtered_questions:
            st.info(f"No questions match the filter: {review_filter}")
            return
        
        st.write(f"Showing {len(filtered_questions)} questions")
        
        # Display questions
        for q_idx, question, user_answer, is_correct, is_marked in filtered_questions:
            with st.expander(f"Question {q_idx + 1} - {question['topic']} {'✅' if is_correct else '❌' if user_answer is not None else '⭐' if is_marked else '❓'}"):
                
                # Question text
                st.markdown(f"**{question['question']}**")
                
                # Show options with indicators
                for i, option in enumerate(question['options']):
                    option_text = f"{chr(65+i)}) {option}"
                    
                    if i == question['correct']:
                        st.success(f"✅ {option_text} (Correct Answer)")
                    elif i == user_answer:
                        if is_correct:
                            st.success(f"✅ {option_text} (Your Answer - Correct)")
                        else:
                            st.error(f"❌ {option_text} (Your Answer - Incorrect)")
                    else:
                        st.write(option_text)
                
                # Show explanation
                st.info(f"💡 **Explanation:** {question['explanation']}")
                
                # Show metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"Topic: {question['topic']}")
                with col2:
                    st.caption(f"Difficulty: {question['difficulty'].title()}")
                with col3:
                    st.caption(f"{'⭐ Marked for Review' if is_marked else ''}")
    
    def show_action_buttons(self):
        """Show action buttons for next steps"""
        st.markdown("---")
        st.markdown("## 🎯 What's Next?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🏠 Go to Home", type="primary", use_container_width=True):
                # Reset session state and return to mode selection
                for key in ['mode', 'questions', 'current_question', 'answers', 
                           'marked_for_review', 'start_time', 'time_remaining', 'exam_submitted', 
                           'show_results', 'results', 'timer_start']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("🔄 Take New Exam", use_container_width=True):
                # Reset session state
                for key in ['mode', 'questions', 'current_question', 'answers', 
                           'marked_for_review', 'start_time', 'time_remaining', 'exam_submitted', 
                           'show_results', 'results', 'timer_start']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        with col3:
            if st.button("📥 Download Results", use_container_width=True):
                self.download_results()
    
    def download_results(self):
        """Prepare results for download"""
        if 'results' not in st.session_state:
            st.error("No results available for download.")
            return
        
        # Create downloadable report
        results = st.session_state.results
        
        report = f"""
# AEM Assets Expert Certification - Exam Results

## Overall Performance
- Score: {results['score']}/{results['total_questions']} ({results['percentage']:.1f}%)
- Grade: {'PASS' if results['percentage'] >= 70 else 'FAIL'}
- Time Taken: {results.get('time_taken', 'N/A')}

## Topic-wise Performance
"""
        
        if 'topic_analysis' in results:
            for topic, data in results['topic_analysis'].items():
                report += f"- {topic}: {data['correct']}/{data['total']} ({data['percentage']:.1f}%)\n"
        
        report += f"""

## Areas for Improvement
"""
        
        if 'topic_analysis' in results:
            weak_topics = [
                topic for topic, data in results['topic_analysis'].items()
                if data['percentage'] < 70
            ]
            
            if weak_topics:
                for topic in weak_topics:
                    report += f"- {topic}\n"
            else:
                report += "- None! Excellent performance across all topics.\n"
        
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"aem_exam_results_{st.session_state.get('start_time', 'unknown').strftime('%Y%m%d_%H%M%S') if st.session_state.get('start_time') else 'unknown'}.txt",
            mime="text/plain"
        )
