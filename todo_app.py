
import json
import os
from datetime import datetime
from typing import List, Dict

class TodoApp:
    def __init__(self, filename: str = "todos.json"):
        self.filename = filename
        self.todos = self.load_todos()
    
    def load_todos(self) -> List[Dict]:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_todos(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    def add_todo(self, task: str, priority: str = "normal") -> bool:
        if not task.strip():
            return False
        
        todo = {
            "id": len(self.todos) + 1,
            "task": task.strip(),
            "completed": False,
            "priority": priority.lower(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None
        }
        
        self.todos.append(todo)
        self.save_todos()
        return True
    
    def complete_todo(self, todo_id: int) -> bool:
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = True
                todo["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_todos()
                return True
        return False
    
    def delete_todo(self, todo_id: int) -> bool:
        initial_length = len(self.todos)
        self.todos = [todo for todo in self.todos if todo["id"] != todo_id]
        
        if len(self.todos) < initial_length:
            self.save_todos()
            return True
        return False
    
    def edit_todo(self, todo_id: int, new_task: str) -> bool:
        if not new_task.strip():
            return False
        
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["task"] = new_task.strip()
                self.save_todos()
                return True
        return False
    
    def list_todos(self, filter_status: str = "all") -> List[Dict]:
        if filter_status == "completed":
            return [todo for todo in self.todos if todo["completed"]]
        elif filter_status == "pending":
            return [todo for todo in self.todos if not todo["completed"]]
        else:
            return self.todos
    
    def get_stats(self) -> Dict:
        total = len(self.todos)
        completed = len([t for t in self.todos if t["completed"]])
        pending = total - completed
        
        priority_stats = {}
        for priority in ["high", "normal", "low"]:
            priority_stats[priority] = len([t for t in self.todos if t["priority"] == priority])
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": f"{(completed/total*100):.1f}%" if total > 0 else "0%",
            "priority_stats": priority_stats
        }

def print_header():
    print("\n" + "="*50)
    print("        📝 PYTHON TODO LIST APP")
    print("="*50)

def print_menu():
    print("\n🔹 MENU:")
    print("1. ➕ Add new task")
    print("2. 📋 List tasks")
    print("3. ✅ Complete task")
    print("4. ✏️  Edit task")
    print("5. 🗑️  Delete task")
    print("6. 📊 Statistics")
    print("7. 🔍 Filtered list")
    print("8. ❌ Exit")

def display_todos(todos: List[Dict], title: str = "TASKS"):
    if not todos:
        print(f"\n📭 {title}: No tasks yet!")
        return
    
    print(f"\n📋 {title}:")
    print("-" * 80)
    
    for todo in todos:
        status = "✅" if todo["completed"] else "⭕"
        priority_icon = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(todo["priority"], "⚪")
        
        print(f"{status} ID: {todo['id']} | {priority_icon} {todo['task']}")
        print(f"   📅 Created at: {todo['created_at']}")
        if todo["completed"]:
            print(f"   ✅ Completed at: {todo['completed_at']}")
        print("-" * 80)

def get_priority():
    print("\nSelect priority:")
    print("1. 🔴 High")
    print("2. 🟡 Normal")
    print("3. 🟢 Low")
    
    choice = input("Choice (1-3, default: 2): ").strip()
    return {"1": "high", "2": "normal", "3": "low"}.get(choice, "normal")

def main():
    app = TodoApp()
    
    while True:
        print_header()
        print_menu()
        
        choice = input("\n🔸 Make your choice (1-8): ").strip()
        
        if choice == "1":
            print("\n➕ ADD NEW TASK")
            task = input("Task description: ").strip()
            if task:
                priority = get_priority()
                if app.add_todo(task, priority):
                    print(f"✅ Task added successfully! (Priority: {priority})")
                else:
                    print("❌ Could not add task!")
            else:
                print("❌ Invalid task description!")
        
        elif choice == "2":
            display_todos(app.list_todos(), "ALL TASKS")
        
        elif choice == "3":
            print("\n✅ COMPLETE TASK")
            display_todos([t for t in app.list_todos() if not t["completed"]], "PENDING TASKS")
            try:
                todo_id = int(input("Enter the ID of the task to complete: "))
                if app.complete_todo(todo_id):
                    print("✅ Task completed!")
                else:
                    print("❌ Task not found!")
            except ValueError:
                print("❌ Invalid ID!")
        
        elif choice == "4":
            print("\n✏️ EDIT TASK")
            display_todos(app.list_todos())
            try:
                todo_id = int(input("Enter the ID of the task to edit: "))
                new_task = input("New task description: ").strip()
                if app.edit_todo(todo_id, new_task):
                    print("✅ Task updated!")
                else:
                    print("❌ Task could not be updated!")
            except ValueError:
                print("❌ Invalid ID!")
        
        elif choice == "5":
            print("\n🗑️ DELETE TASK")
            display_todos(app.list_todos())
            try:
                todo_id = int(input("Enter the ID of the task to delete: "))
                confirm = input(f"Are you sure you want to delete task ID {todo_id}? (y/n): ")
                if confirm.lower() == 'y':
                    if app.delete_todo(todo_id):
                        print("✅ Task deleted!")
                    else:
                        print("❌ Task not found!")
                else:
                    print("ℹ️ Delete cancelled.")
            except ValueError:
                print("❌ Invalid ID!")
        
        elif choice == "6":
            print("\n📊 STATISTICS")
            stats = app.get_stats()
            print(f"📊 Total tasks: {stats['total']}")
            print(f"✅ Completed: {stats['completed']}")
            print(f"⭕ Pending: {stats['pending']}")
            print(f"📈 Completion rate: {stats['completion_rate']}")
            print("\n📊 Priority distribution:")
            print(f"🔴 High: {stats['priority_stats']['high']}")
            print(f"🟡 Normal: {stats['priority_stats']['normal']}")
            print(f"🟢 Low: {stats['priority_stats']['low']}")
        
        elif choice == "7":
            print("\n🔍 FILTERED LIST")
            print("1. ✅ Completed")
            print("2. ⭕ Pending")
            print("3. 📋 All")
            
            filter_choice = input("Choice (1-3): ").strip()
            if filter_choice == "1":
                display_todos(app.list_todos("completed"), "COMPLETED TASKS")
            elif filter_choice == "2":
                display_todos(app.list_todos("pending"), "PENDING TASKS")
            else:
                display_todos(app.list_todos(), "ALL TASKS")
        
        elif choice == "8":
            print("\n👋 Goodbye! Exiting the Todo App...")
            break
        
        else:
            print("❌ Invalid choice! Please enter a number between 1-8.")
        
        input("\n⏸️ Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program terminated. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
