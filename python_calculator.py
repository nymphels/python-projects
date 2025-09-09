import tkinter as tk
from tkinter import messagebox
import math
import json
from datetime import datetime

class Calculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧮 Python Calculator")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")
        
        # Variables
        self.current = ""
        self.previous = ""
        self.operator = ""
        self.result_shown = False
        self.history = []
        
        # Display variable
        self.display_var = tk.StringVar(value="0")
        
        # Create UI
        self.create_widgets()
        
        # Load history
        self.load_history()
        
        # Keyboard bindings
        self.setup_keyboard_bindings()
    
    def create_widgets(self):
        """Create UI"""
        # Display frame
        display_frame = tk.Frame(self.root, bg="#34495e", padx=10, pady=10)
        display_frame.pack(fill="x", padx=10, pady=(10,5))
        
        # Display
        display = tk.Entry(
            display_frame,
            textvariable=self.display_var,
            font=("Arial", 24, "bold"),
            justify="right",
            state="readonly",
            bg="#ecf0f1",
            fg="#2c3e50",
            borderwidth=0,
            highlightthickness=2,
            highlightcolor="#3498db"
        )
        display.pack(fill="x", ipady=10)
        
        # Info label
        self.info_label = tk.Label(
            display_frame,
            text="Ready",
            font=("Arial", 10),
            bg="#34495e",
            fg="#bdc3c7"
        )
        self.info_label.pack(anchor="e", pady=(5,0))
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg="#2c3e50")
        buttons_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Button configurations
        button_style = {
            "font": ("Arial", 16, "bold"),
            "border": 0,
            "highlightthickness": 0,
            "activebackground": "#3498db",
            "activeforeground": "white"
        }
        
        number_style = {
            **button_style,
            "bg": "#ecf0f1",
            "fg": "#2c3e50"
        }
        
        operator_style = {
            **button_style,
            "bg": "#e67e22",
            "fg": "white"
        }
        
        special_style = {
            **button_style,
            "bg": "#95a5a6",
            "fg": "white"
        }
        
        # Button layout
        buttons = [
            [("C", special_style, self.clear), ("CE", special_style, self.clear_entry), ("⌫", special_style, self.backspace), ("÷", operator_style, lambda: self.set_operator("/"))],
            [("7", number_style, lambda: self.add_digit("7")), ("8", number_style, lambda: self.add_digit("8")), ("9", number_style, lambda: self.add_digit("9")), ("×", operator_style, lambda: self.set_operator("*"))],
            [("4", number_style, lambda: self.add_digit("4")), ("5", number_style, lambda: self.add_digit("5")), ("6", number_style, lambda: self.add_digit("6")), ("−", operator_style, lambda: self.set_operator("-"))],
            [("1", number_style, lambda: self.add_digit("1")), ("2", number_style, lambda: self.add_digit("2")), ("3", number_style, lambda: self.add_digit("3")), ("+", operator_style, lambda: self.set_operator("+"))],
            [("±", special_style, self.toggle_sign), ("0", number_style, lambda: self.add_digit("0")), (".", number_style, self.add_decimal), ("=", operator_style, self.calculate)],
        ]
        
        # Create buttons
        for i, row in enumerate(buttons):
            for j, (text, style, command) in enumerate(row):
                btn = tk.Button(
                    buttons_frame,
                    text=text,
                    command=command,
                    **style
                )
                btn.grid(row=i, column=j, sticky="nsew", padx=2, pady=2)
        
        # Configure grid weights
        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1)
        
        # Scientific functions frame
        sci_frame = tk.Frame(self.root, bg="#2c3e50")
        sci_frame.pack(fill="x", padx=10, pady=5)
        
        sci_buttons = [
            ("√", self.square_root), ("x²", self.square), ("1/x", self.reciprocal),
            ("sin", self.sin), ("cos", self.cos), ("tan", self.tan),
            ("log", self.log), ("ln", self.ln), ("π", self.pi)
        ]
        
        for i, (text, command) in enumerate(sci_buttons):
            btn = tk.Button(
                sci_frame,
                text=text,
                command=command,
                font=("Arial", 10, "bold"),
                bg="#9b59b6",
                fg="white",
                border=0,
                activebackground="#8e44ad",
                activeforeground="white"
            )
            btn.grid(row=i//3, column=i%3, sticky="ew", padx=1, pady=1)
        
        for j in range(3):
            sci_frame.grid_columnconfigure(j, weight=1)
        
        # History buttons
        control_frame = tk.Frame(self.root, bg="#2c3e50")
        control_frame.pack(fill="x", padx=10, pady=5)
        
        control_buttons = [
            ("History", self.show_history),
            ("Clear History", self.clear_history)
        ]
        
        for i, (text, command) in enumerate(control_buttons):
            btn = tk.Button(
                control_frame,
                text=text,
                command=command,
                font=("Arial", 10),
                bg="#34495e",
                fg="white",
                border=0
            )
            btn.grid(row=0, column=i, sticky="ew", padx=2)
        
        for j in range(2):
            control_frame.grid_columnconfigure(j, weight=1)
    
    def setup_keyboard_bindings(self):
        """Keyboard shortcuts"""
        self.root.bind("<Key>", self.key_press)
        self.root.focus_set()
    
    def key_press(self, event):
        """Keyboard input"""
        key = event.char
        
        if key.isdigit():
            self.add_digit(key)
        elif key == ".":
            self.add_decimal()
        elif key in "+-*/":
            self.set_operator(key)
        elif key in ["\r", "\n", "="]:  # Enter or =
            self.calculate()
        elif key in ["\b"]:  # Backspace
            self.backspace()
        elif key.lower() == "c":
            self.clear()
    
    def update_display(self, value=""):
        """Update display"""
        if value == "":
            value = self.current if self.current else "0"
        
        if len(str(value)) > 15:
            try:
                value = f"{float(value):.6e}"
            except:
                value = str(value)[:15] + "..."
        
        self.display_var.set(str(value))
    
    def update_info(self, text):
        """Update info label"""
        self.info_label.config(text=text)
    
    def add_digit(self, digit):
        """Add digit"""
        if self.result_shown:
            self.current = ""
            self.result_shown = False
        
        if self.current == "0" and digit == "0":
            return
        
        if self.current == "0" and digit != "0":
            self.current = digit
        else:
            self.current += digit
        
        self.update_display()
        self.update_info("Ready")
    
    def add_decimal(self):
        """Add decimal point"""
        if self.result_shown:
            self.current = "0"
            self.result_shown = False
        
        if "." not in self.current:
            if not self.current:
                self.current = "0"
            self.current += "."
            self.update_display()
    
    def set_operator(self, op):
        """Set operator"""
        if self.current:
            if self.previous and self.operator and not self.result_shown:
                self.calculate()
            
            self.previous = self.current
            self.current = ""
            self.operator = op
            
            op_symbols = {"+": "+", "-": "−", "*": "×", "/": "÷"}
            self.update_info(f"{self.previous} {op_symbols.get(op, op)}")
    
    def calculate(self):
        """Calculate"""
        if not self.previous or not self.operator:
            return
        
        if not self.current:
            self.current = self.previous
        
        try:
            prev_num = float(self.previous)
            curr_num = float(self.current)
            
            if self.operator == "+":
                result = prev_num + curr_num
            elif self.operator == "-":
                result = prev_num - curr_num
            elif self.operator == "*":
                result = prev_num * curr_num
            elif self.operator == "/":
                if curr_num == 0:
                    raise ZeroDivisionError("Cannot divide by zero!")
