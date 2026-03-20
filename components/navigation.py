import streamlit as st
import math

class Navigation:
    def show_navigation(self):
        """Show question navigation panel"""
        if not st.session_state.questions:
            return
        
        st.markdown("### 🧭 Question Navigation")
        
        total_questions = len(st.session_state.questions)
        current_question = st.session_state.current_question
        
        # Statistics
        answered = len(st.session_state.answers)
        marked = len(st.session_state.marked_for_review)
        unanswered = total_questions - answered
        
        # Show stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Answered", answered)
            st.metric("Marked", marked)
        with col2:
            st.metric("Remaining", unanswered)
            st.metric("Total", total_questions)
        
        st.markdown("---")
        
        # Legend
        st.markdown("""
        **Legend:**
        - 🟢 Answered
        - 🟠 Marked for Review  
        - 🔵 Current Question
        - ⚪ Not Answered
        """)
        
        # Question grid
        questions_per_row = 10
        rows = math.ceil(total_questions / questions_per_row)
        
        for row in range(rows):
            cols = st.columns(questions_per_row)
            
            for col_idx in range(questions_per_row):
                q_idx = row * questions_per_row + col_idx
                
                if q_idx >= total_questions:
                    break
                
                with cols[col_idx]:
                    # Determine button style
                    button_text = str(q_idx + 1)
                    
                    if q_idx == current_question:
                        button_type = "primary"
                        emoji = "🔵"
                    elif q_idx in st.session_state.answers:
                        if q_idx in st.session_state.marked_for_review:
                            emoji = "🟠"
                            button_type = "secondary"
                        else:
                            emoji = "🟢"
                            button_type = "secondary"
                    elif q_idx in st.session_state.marked_for_review:
                        emoji = "🟠"
                        button_type = "secondary"
                    else:
                        emoji = "⚪"
                        button_type = "secondary"
                    
                    # Navigation button
                    if st.button(
                        f"{emoji} {button_text}",
                        key=f"nav_{q_idx}",
                        help=f"Go to question {q_idx + 1}",
                        use_container_width=True
                    ):
                        st.session_state.current_question = q_idx
                        st.rerun()
        
        st.markdown("---")
        
        # Quick navigation
        st.markdown("### ⚡ Quick Navigation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("First Unanswered", use_container_width=True):
                self.go_to_first_unanswered()
        
        with col2:
            if st.button("Next Marked", use_container_width=True):
                self.go_to_next_marked()
        
        # Topic-wise navigation
        if st.session_state.mode == 'practice':
            self.show_topic_navigation()
    
    def go_to_first_unanswered(self):
        """Navigate to first unanswered question"""
        for i, _ in enumerate(st.session_state.questions):
            if i not in st.session_state.answers:
                st.session_state.current_question = i
                st.rerun()
                return
        
        st.info("All questions have been answered!")
    
    def go_to_next_marked(self):
        """Navigate to next marked question"""
        current = st.session_state.current_question
        marked_questions = sorted(st.session_state.marked_for_review)
        
        if not marked_questions:
            st.info("No questions marked for review!")
            return
        
        # Find next marked question after current
        next_marked = None
        for q_idx in marked_questions:
            if q_idx > current:
                next_marked = q_idx
                break
        
        # If no marked question after current, go to first marked
        if next_marked is None:
            next_marked = marked_questions[0]
        
        st.session_state.current_question = next_marked
        st.rerun()
    
    def show_topic_navigation(self):
        """Show topic-wise navigation for practice mode"""
        st.markdown("### 📚 Browse by Topic")
        
        # Get unique topics
        topics = list(set(q['topic'] for q in st.session_state.questions))
        topics.sort()
        
        selected_topic = st.selectbox("Select Topic", ["All Topics"] + topics)
        
        if selected_topic != "All Topics":
            topic_questions = [
                i for i, q in enumerate(st.session_state.questions)
                if q['topic'] == selected_topic
            ]
            
            if topic_questions:
                st.write(f"Found {len(topic_questions)} questions in {selected_topic}")
                
                # Show topic questions as buttons
                for i, q_idx in enumerate(topic_questions):
                    question_num = q_idx + 1
                    status = "✅" if q_idx in st.session_state.answers else "❓"
                    
                    if st.button(
                        f"{status} Question {question_num}",
                        key=f"topic_nav_{q_idx}",
                        use_container_width=True
                    ):
                        st.session_state.current_question = q_idx
                        st.rerun()
