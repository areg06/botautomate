"""
Shared log storage for web display.
"""
import threading
from typing import List

class LogStorage:
    """Thread-safe log storage for web display."""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LogStorage, cls).__new__(cls)
                    cls._instance.logs: List[str] = []
                    cls._instance.max_logs = 500
        return cls._instance
    
    def add_log(self, log_entry: str):
        """Add a log entry."""
        with self._lock:
            self.logs.append(log_entry)
            if len(self.logs) > self.max_logs:
                self.logs.pop(0)
    
    def get_logs(self, limit: int = 200) -> List[str]:
        """Get recent log entries."""
        with self._lock:
            return self.logs[-limit:] if limit else self.logs.copy()
    
    def clear_logs(self):
        """Clear all logs."""
        with self._lock:
            self.logs.clear()

# Global instance
log_storage = LogStorage()
