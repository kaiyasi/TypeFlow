# Python - Data Processing Example

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class TypingSession:
    """Represents a typing practice session"""
    
    def __init__(self, user_id: str, text: str, duration: int):
        self.user_id = user_id
        self.text = text
        self.duration = duration
        self.start_time = datetime.now()
        self.keystrokes: List[Dict] = []
        self.completed = False
    
    def add_keystroke(self, char: str, timestamp: datetime, correct: bool):
        """Add a keystroke to the session"""
        keystroke = {
            'char': char,
            'timestamp': timestamp.isoformat(),
            'correct': correct,
            'position': len(self.keystrokes)
        }
        self.keystrokes.append(keystroke)
    
    def calculate_wpm(self) -> float:
        """Calculate words per minute"""
        if not self.completed:
            return 0.0
        
        total_chars = len([k for k in self.keystrokes if k['correct']])
        elapsed_minutes = self.duration / 60
        return (total_chars / 5) / elapsed_minutes if elapsed_minutes > 0 else 0
    
    def calculate_accuracy(self) -> float:
        """Calculate typing accuracy percentage"""
        if not self.keystrokes:
            return 100.0
        
        correct_count = sum(1 for k in self.keystrokes if k['correct'])
        return (correct_count / len(self.keystrokes)) * 100
    
    def finish_session(self):
        """Mark session as completed"""
        self.completed = True
        self.end_time = datetime.now()
    
    def to_json(self) -> str:
        """Export session data as JSON"""
        data = {
            'user_id': self.user_id,
            'text': self.text,
            'duration': self.duration,
            'start_time': self.start_time.isoformat(),
            'wpm': self.calculate_wpm(),
            'accuracy': self.calculate_accuracy(),
            'keystroke_count': len(self.keystrokes),
            'completed': self.completed
        }
        return json.dumps(data, indent=2)

# Example usage
if __name__ == "__main__":
    session = TypingSession("user123", "The quick brown fox", 60)
    
    # Simulate some keystrokes
    sample_keystrokes = [
        ('T', True), ('h', True), ('e', True), (' ', True),
        ('q', True), ('u', True), ('i', True), ('c', False)
    ]
    
    for char, correct in sample_keystrokes:
        session.add_keystroke(char, datetime.now(), correct)
    
    session.finish_session()
    print(session.to_json())