import json
import os
from datetime import datetime
from typing import List, Dict, Optional

TODO_FILE = "todos.json"

class TodoManager:
    def __init__(self):
        """Initialize todo manager"""
        self.todos = self._load_todos()
    
    def add_todo(self, title: str, description: str = "", priority: str = "medium") -> Dict:
        """Add a new todo item"""
        if not title.strip():
            raise ValueError("Title cannot be empty")
        
        todo = {
            "id": len(self.todos) + 1,
            "title": title,
            "description": description,
            "priority": priority.lower(),
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "due_date": None,
            "tags": []
        }
        
        self.todos.append(todo)
        self._save_todos()
        return todo
    
    def get_all_todos(self, filter_by: str = None) -> List[Dict]:
        """Get all todos, optionally filtered"""
        if filter_by == "completed":
            return [t for t in self.todos if t["completed"]]
        elif filter_by == "pending":
            return [t for t in self.todos if not t["completed"]]
        elif filter_by == "high":
            return [t for t in self.todos if t["priority"] == "high"]
        elif filter_by == "medium":
            return [t for t in self.todos if t["priority"] == "medium"]
        elif filter_by == "low":
            return [t for t in self.todos if t["priority"] == "low"]
        return self.todos
    
    def get_todo(self, todo_id: int) -> Optional[Dict]:
        """Get a specific todo by ID"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                return todo
        return None
    
    def update_todo(self, todo_id: int, **kwargs) -> Optional[Dict]:
        """Update a todo item"""
        todo = self.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")
        
        allowed_fields = ["title", "description", "priority", "completed", "due_date", "tags"]
        for key, value in kwargs.items():
            if key in allowed_fields:
                todo[key] = value
        
        todo["updated_at"] = datetime.now().isoformat()
        self._save_todos()
        return todo
    
    def complete_todo(self, todo_id: int) -> Optional[Dict]:
        """Mark a todo as completed"""
        return self.update_todo(todo_id, completed=True)
    
    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo item"""
        initial_count = len(self.todos)
        self.todos = [t for t in self.todos if t["id"] != todo_id]
        
        if len(self.todos) < initial_count:
            self._save_todos()
            return True
        return False
    
    def add_tag(self, todo_id: int, tag: str) -> Optional[Dict]:
        """Add a tag to a todo"""
        todo = self.get_todo(todo_id)
        if not todo:
            raise ValueError(f"Todo {todo_id} not found")
        
        if tag not in todo["tags"]:
            todo["tags"].append(tag)
            self._save_todos()
        
        return todo
    
    def get_by_tag(self, tag: str) -> List[Dict]:
        """Get all todos with a specific tag"""
        return [t for t in self.todos if tag in t["tags"]]
    
    def get_stats(self) -> Dict:
        """Get todo statistics"""
        total = len(self.todos)
        completed = len([t for t in self.todos if t["completed"]])
        pending = total - completed
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "by_priority": {
                "high": len([t for t in self.todos if t["priority"] == "high"]),
                "medium": len([t for t in self.todos if t["priority"] == "medium"]),
                "low": len([t for t in self.todos if t["priority"] == "low"])
            }
        }
    
    def _load_todos(self) -> List[Dict]:
        """Load todos from file"""
        try:
            if os.path.exists(TODO_FILE):
                with open(TODO_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[TODO] Error loading todos: {e}")
        return []
    
    def _save_todos(self):
        """Save todos to file"""
        try:
            with open(TODO_FILE, "w") as f:
                json.dump(self.todos, f, indent=2)
        except Exception as e:
            print(f"[TODO] Error saving todos: {e}")


if __name__ == "__main__":
    # Test
    manager = TodoManager()
    
    # Add todos
    t1 = manager.add_todo("Fix weather dashboard", "Integrate OpenWeather API", "high")
    t2 = manager.add_todo("Write documentation", priority="medium")
    t3 = manager.add_todo("Test voice commands", priority="low")
    
    print("[TODO] Added todos:")
    for todo in manager.get_all_todos():
        print(f"  - {todo['title']} ({todo['priority']})")
    
    # Complete one
    manager.complete_todo(t1["id"])
    
    # Add tags
    manager.add_tag(t2["id"], "documentation")
    manager.add_tag(t3["id"], "testing")
    
    # Print stats
    print("\n[TODO] Stats:")
    stats = manager.get_stats()
    print(f"  Total: {stats['total']}, Completed: {stats['completed']}, Pending: {stats['pending']}")
