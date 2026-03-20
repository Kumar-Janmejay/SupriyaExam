import streamlit as st
import time
from datetime import datetime, timedelta

class Timer:
    def __init__(self):
        self.duration = 6000  # 100 minutes in seconds
    
    def show_timer(self):
        """Display and manage the exam timer"""
        if st.session_state.mode != 'exam':
            return
        
        # Initialize timer if not started
        if 'timer_start' not in st.session_state:
            st.session_state.timer_start = time.time()
            st.session_state.time_remaining = self.duration
        
        # Calculate remaining time
        elapsed = time.time() - st.session_state.timer_start
        remaining = max(0, self.duration - elapsed)
        
        # Update session state
        st.session_state.time_remaining = remaining
        
        # Auto-submit when time is up
        if remaining <= 0:
            st.error("⏰ Time's up! Auto-submitting exam...")
            st.session_state.exam_submitted = True
            st.session_state.show_results = True
            st.rerun()
        
        # Format time display
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Determine timer style based on remaining time
        if remaining <= 300:  # 5 minutes
            timer_class = "timer-container timer-critical"
        elif remaining <= 1200:  # 20 minutes
            timer_class = "timer-container timer-warning"
        else:
            timer_class = "timer-container"
        
        # Display timer
        st.markdown(f"""
        <div class="{timer_class}">
            ⏰ Time Remaining: {time_str}
        </div>
        """, unsafe_allow_html=True)
        
        # Show warnings
        if remaining <= 300:
            st.error("⚠️ Only 5 minutes remaining!")
        elif remaining <= 1200:
            st.warning("⚠️ 20 minutes remaining - consider reviewing your answers")
    
    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time"""
        if 'timer_start' not in st.session_state:
            return "00:00"
        
        elapsed = time.time() - st.session_state.timer_start
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_remaining_time(self) -> int:
        """Get remaining time in seconds"""
        return st.session_state.get('time_remaining', self.duration)
