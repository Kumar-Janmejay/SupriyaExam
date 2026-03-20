import streamlit as st
import json
import pickle
from datetime import datetime

class StateManager:
    def __init__(self):
        self.state_file = "exam_state.pkl"
    
    def save_state(self):
        """Save current exam state"""
        state_data = {
            'mode': st.session_state.get('mode'),
            'current_question': st.session_state.get('current_question', 0),
            'answers': st.session_state.get('answers', {}),
            'marked_for_review': list(st.session_state.get('marked_for_review', set())),
            'start_time': st.session_state.get('start_time'),
            'time_remaining': st.session_state.get('time_remaining'),
            'questions': st.session_state.get('questions', [])
        }
        
        try:
            with open(self.state_file, 'wb') as f:
                pickle.dump(state_data, f)
            return True
        except Exception as e:
            st.error(f"Failed to save state: {e}")
            return False
    
    def load_state(self):
        """Load saved exam state"""
        try:
            with open(self.state_file, 'rb') as f:
                state_data = pickle.load(f)
            
            # Restore state
            for key, value in state_data.items():
                if key == 'marked_for_review':
                    st.session_state[key] = set(value)
                else:
                    st.session_state[key] = value
            
            return True
        except Exception:
            return False
    
    def clear_state(self):
        """Clear saved state"""
        try:
            import os
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
            return True
        except Exception:
            return False
    
    def auto_save(self):
        """Auto-save state periodically"""
        if st.session_state.get('mode') == 'exam' and not st.session_state.get('exam_submitted'):
            self.save_state()
