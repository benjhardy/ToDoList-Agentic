import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, date, timedelta
import requests
import math
import threading
import time
from typing import Dict, List, Optional
import calendar


class DarkTheme:
    """Dark theme color scheme"""
    BG_PRIMARY = "#1a1a1a"
    BG_SECONDARY = "#2d2d2d"
    BG_TERTIARY = "#3a3a3a"
    FG_PRIMARY = "#ffffff"
    FG_SECONDARY = "#cccccc"
    FG_MUTED = "#888888"
    ACCENT = "#4a9eff"
    ACCENT_HOVER = "#6bb6ff"
    SUCCESS = "#4caf50"
    SUCCESS_BRIGHT = "#66bb6a"
    WARNING = "#ff9800"
    ERROR = "#f44336"
    BORDER = "#555555"
    COMPLETION_FLASH = "#ffd700"  # Gold color for completion flash


class DataManager:
    """Handles data persistence"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def save_daily_todos(self, date_str: str, todos: List[Dict]):
        """Save todos for a specific date"""
        filepath = os.path.join(self.data_dir, f"todos_{date_str}.json")
        with open(filepath, 'w') as f:
            json.dump(todos, f, indent=2)
    
    def load_daily_todos(self, date_str: str) -> List[Dict]:
        """Load todos for a specific date"""
        filepath = os.path.join(self.data_dir, f"todos_{date_str}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return []
    
    def save_projects(self, projects: Dict):
        """Save projects/goals data"""
        filepath = os.path.join(self.data_dir, "projects.json")
        with open(filepath, 'w') as f:
            json.dump(projects, f, indent=2)
    
    def load_projects(self) -> Dict:
        """Load projects/goals data"""
        filepath = os.path.join(self.data_dir, "projects.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def save_settings(self, settings: Dict):
        """Save application settings"""
        filepath = os.path.join(self.data_dir, "settings.json")
        with open(filepath, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def load_settings(self) -> Dict:
        """Load application settings"""
        filepath = os.path.join(self.data_dir, "settings.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {"zip_code": "10001", "api_key": ""}


class WeatherWidget:
    """Weather information widget"""
    
    def __init__(self, parent, data_manager):
        self.parent = parent
        self.data_manager = data_manager
        self.weather_data = None
        self.settings = data_manager.load_settings()
        
        self.frame = tk.Frame(parent, bg=DarkTheme.BG_SECONDARY)
        
        # Weather info display
        self.weather_label = tk.Label(
            self.frame, 
            text="Loading weather...", 
            font=("Arial", 10),
            bg=DarkTheme.BG_SECONDARY,
            fg=DarkTheme.FG_PRIMARY
        )
        self.weather_label.pack(pady=5)
        
        # Settings button
        self.settings_btn = tk.Button(
            self.frame,
            text="Weather Settings",
            command=self.open_settings,
            bg=DarkTheme.BG_TERTIARY,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 8),
            relief="flat",
            cursor="hand2"
        )
        self.settings_btn.pack(pady=2)
        
        # Start weather updates
        self.update_weather()
    
    def open_settings(self):
        """Open weather settings dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Weather Settings")
        dialog.geometry("300x200")
        dialog.configure(bg=DarkTheme.BG_PRIMARY)
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Zip code input
        tk.Label(dialog, text="Zip Code:", bg=DarkTheme.BG_PRIMARY, fg=DarkTheme.FG_PRIMARY).pack(pady=5)
        zip_entry = tk.Entry(dialog, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.FG_PRIMARY, insertbackground=DarkTheme.FG_PRIMARY)
        zip_entry.insert(0, self.settings.get("zip_code", "10001"))
        zip_entry.pack(pady=5)
        
        # API key input
        tk.Label(dialog, text="OpenWeatherMap API Key:", bg=DarkTheme.BG_PRIMARY, fg=DarkTheme.FG_PRIMARY).pack(pady=5)
        api_entry = tk.Entry(dialog, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.FG_PRIMARY, insertbackground=DarkTheme.FG_PRIMARY, show="*")
        api_entry.insert(0, self.settings.get("api_key", ""))
        api_entry.pack(pady=5)
        
        # Info label
        info_label = tk.Label(
            dialog, 
            text="Get free API key from:\nopenweathermap.org/api",
            bg=DarkTheme.BG_PRIMARY,
            fg=DarkTheme.FG_MUTED,
            font=("Arial", 8)
        )
        info_label.pack(pady=5)
        
        def save_settings():
            self.settings["zip_code"] = zip_entry.get()
            self.settings["api_key"] = api_entry.get()
            self.data_manager.save_settings(self.settings)
            dialog.destroy()
            self.update_weather()
        
        # Save button
        save_btn = tk.Button(
            dialog,
            text="Save",
            command=save_settings,
            bg=DarkTheme.ACCENT,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 10),
            relief="flat",
            cursor="hand2"
        )
        save_btn.pack(pady=10)
    
    def update_weather(self):
        """Update weather information"""
        def fetch_weather():
            try:
                api_key = self.settings.get("api_key")
                zip_code = self.settings.get("zip_code", "10001")
                
                if not api_key:
                    self.weather_label.config(text="Weather: API key required")
                    return
                
                url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code}&appid={api_key}&units=imperial"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if response.status_code == 200:
                    temp = int(data['main']['temp'])
                    description = data['weather'][0]['description'].title()
                    city = data['name']
                    
                    weather_text = f"{city}\n{temp}°F\n{description}"
                    self.weather_label.config(text=weather_text)
                else:
                    self.weather_label.config(text="Weather: Error loading")
                    
            except Exception as e:
                self.weather_label.config(text="Weather: Connection error")
        
        # Run in background thread
        threading.Thread(target=fetch_weather, daemon=True).start()
        
        # Schedule next update in 30 minutes
        self.parent.after(30 * 60 * 1000, self.update_weather)


class AnalogClock:
    """Analog clock widget"""
    
    def __init__(self, parent, size=200):
        self.size = size
        self.canvas = tk.Canvas(
            parent,
            width=size,
            height=size,
            bg=DarkTheme.BG_SECONDARY,
            highlightthickness=0
        )
        
        # Date label
        self.date_label = tk.Label(
            parent,
            text="",
            font=("Arial", 12, "bold"),
            bg=DarkTheme.BG_SECONDARY,
            fg=DarkTheme.FG_PRIMARY
        )
        self.date_label.pack(pady=5)
        
        self.canvas.pack(pady=10)
        self.update_clock()
    
    def update_clock(self):
        """Update the analog clock"""
        self.canvas.delete("all")
        
        # Get current time
        now = datetime.now()
        
        # Update date
        date_str = now.strftime("%B %d, %Y")
        self.date_label.config(text=date_str)
        
        # Clock face
        center_x = center_y = self.size // 2
        radius = self.size // 2 - 20
        
        # Draw clock face
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline=DarkTheme.BORDER,
            fill=DarkTheme.BG_TERTIARY,
            width=3
        )
        
        # Draw hour markers
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = center_x + (radius - 15) * math.cos(angle)
            y1 = center_y + (radius - 15) * math.sin(angle)
            x2 = center_x + (radius - 5) * math.cos(angle)
            y2 = center_y + (radius - 5) * math.sin(angle)
            
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=DarkTheme.FG_PRIMARY,
                width=3
            )
        
        # Draw minute markers
        for i in range(60):
            if i % 5 != 0:  # Skip hour markers
                angle = math.radians(i * 6 - 90)
                x1 = center_x + (radius - 10) * math.cos(angle)
                y1 = center_y + (radius - 10) * math.sin(angle)
                x2 = center_x + (radius - 5) * math.cos(angle)
                y2 = center_y + (radius - 5) * math.sin(angle)
                
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=DarkTheme.FG_SECONDARY,
                    width=1
                )
        
        # Calculate hand positions
        hour_angle = math.radians((now.hour % 12) * 30 + now.minute * 0.5 - 90)
        minute_angle = math.radians(now.minute * 6 - 90)
        second_angle = math.radians(now.second * 6 - 90)
        
        # Hour hand
        hour_x = center_x + (radius * 0.5) * math.cos(hour_angle)
        hour_y = center_y + (radius * 0.5) * math.sin(hour_angle)
        self.canvas.create_line(
            center_x, center_y, hour_x, hour_y,
            fill=DarkTheme.FG_PRIMARY,
            width=4,
            capstyle=tk.ROUND
        )
        
        # Minute hand
        minute_x = center_x + (radius * 0.7) * math.cos(minute_angle)
        minute_y = center_y + (radius * 0.7) * math.sin(minute_angle)
        self.canvas.create_line(
            center_x, center_y, minute_x, minute_y,
            fill=DarkTheme.FG_PRIMARY,
            width=3,
            capstyle=tk.ROUND
        )
        
        # Second hand
        second_x = center_x + (radius * 0.8) * math.cos(second_angle)
        second_y = center_y + (radius * 0.8) * math.sin(second_angle)
        self.canvas.create_line(
            center_x, center_y, second_x, second_y,
            fill=DarkTheme.ACCENT,
            width=2,
            capstyle=tk.ROUND
        )
        
        # Center dot
        self.canvas.create_oval(
            center_x - 5, center_y - 5,
            center_x + 5, center_y + 5,
            fill=DarkTheme.FG_PRIMARY,
            outline=DarkTheme.FG_PRIMARY
        )
        
        # Schedule next update
        self.canvas.after(1000, self.update_clock)


class CalendarWidget:
    """Custom calendar widget for date selection"""
    
    def __init__(self, parent, callback=None, current_date=None):
        self.parent = parent
        self.callback = callback
        self.current_date = current_date or date.today()
        self.selected_date = self.current_date
        self.viewing_date = date(self.current_date.year, self.current_date.month, 1)
        
        # Main calendar frame
        self.frame = tk.Frame(parent, bg=DarkTheme.BG_SECONDARY, relief="solid", bd=1)
        
        self.setup_calendar()
        self.render_calendar()
    
    def setup_calendar(self):
        """Setup the calendar interface"""
        # Header with month/year navigation
        header_frame = tk.Frame(self.frame, bg=DarkTheme.BG_SECONDARY)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Previous month button
        self.prev_btn = tk.Button(
            header_frame,
            text="◀",
            command=self.prev_month,
            bg=DarkTheme.BG_TERTIARY,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 10),
            relief="flat",
            cursor="hand2",
            width=3
        )
        self.prev_btn.pack(side=tk.LEFT)
        
        # Month/Year label
        self.month_label = tk.Label(
            header_frame,
            text="",
            font=("Arial", 12, "bold"),
            bg=DarkTheme.BG_SECONDARY,
            fg=DarkTheme.FG_PRIMARY
        )
        self.month_label.pack(side=tk.LEFT, expand=True)
        
        # Next month button
        self.next_btn = tk.Button(
            header_frame,
            text="▶",
            command=self.next_month,
            bg=DarkTheme.BG_TERTIARY,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 10),
            relief="flat",
            cursor="hand2",
            width=3
        )
        self.next_btn.pack(side=tk.RIGHT)
        
        # Days of week header
        days_frame = tk.Frame(self.frame, bg=DarkTheme.BG_SECONDARY)
        days_frame.pack(fill=tk.X, padx=5)
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for day in days:
            day_label = tk.Label(
                days_frame,
                text=day,
                font=("Arial", 9, "bold"),
                bg=DarkTheme.BG_SECONDARY,
                fg=DarkTheme.FG_MUTED,
                width=4
            )
            day_label.pack(side=tk.LEFT, padx=1)
        
        # Calendar grid
        self.calendar_frame = tk.Frame(self.frame, bg=DarkTheme.BG_SECONDARY)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def prev_month(self):
        """Go to previous month"""
        if self.viewing_date.month == 1:
            self.viewing_date = date(self.viewing_date.year - 1, 12, 1)
        else:
            self.viewing_date = date(self.viewing_date.year, self.viewing_date.month - 1, 1)
        self.render_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.viewing_date.month == 12:
            self.viewing_date = date(self.viewing_date.year + 1, 1, 1)
        else:
            self.viewing_date = date(self.viewing_date.year, self.viewing_date.month + 1, 1)
        self.render_calendar()
    
    def date_selected(self, selected_date):
        """Handle date selection"""
        self.selected_date = selected_date
        if self.callback:
            self.callback(selected_date)
        self.render_calendar()
    
    def render_calendar(self):
        """Render the calendar grid"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Update month label
        month_year = self.viewing_date.strftime("%B %Y")
        self.month_label.config(text=month_year)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.viewing_date.year, self.viewing_date.month)
        
        # Create date buttons
        for week_num, week in enumerate(cal):
            week_frame = tk.Frame(self.calendar_frame, bg=DarkTheme.BG_SECONDARY)
            week_frame.pack(fill=tk.X)
            
            for day_num in week:
                if day_num == 0:
                    # Empty cell for days from other months
                    empty_label = tk.Label(
                        week_frame,
                        text="",
                        width=4,
                        height=2,
                        bg=DarkTheme.BG_SECONDARY
                    )
                    empty_label.pack(side=tk.LEFT, padx=1, pady=1)
                else:
                    # Create date for this day
                    day_date = date(self.viewing_date.year, self.viewing_date.month, day_num)
                    
                    # Determine button style
                    is_today = day_date == date.today()
                    is_selected = day_date == self.selected_date
                    is_current_month = day_date.month == self.viewing_date.month
                    
                    if is_selected:
                        bg_color = DarkTheme.ACCENT
                        fg_color = DarkTheme.FG_PRIMARY
                        font_weight = "bold"
                    elif is_today:
                        bg_color = DarkTheme.SUCCESS
                        fg_color = DarkTheme.FG_PRIMARY
                        font_weight = "bold"
                    else:
                        bg_color = DarkTheme.BG_TERTIARY
                        fg_color = DarkTheme.FG_PRIMARY if is_current_month else DarkTheme.FG_MUTED
                        font_weight = "normal"
                    
                    day_btn = tk.Button(
                        week_frame,
                        text=str(day_num),
                        command=lambda d=day_date: self.date_selected(d),
                        bg=bg_color,
                        fg=fg_color,
                        font=("Arial", 9, font_weight),
                        relief="flat",
                        cursor="hand2",
                        width=4,
                        height=2
                    )
                    day_btn.pack(side=tk.LEFT, padx=1, pady=1)
                    
                    # Hover effects
                    def on_enter(event, btn=day_btn, orig_bg=bg_color):
                        if not is_selected:
                            btn.config(bg=DarkTheme.ACCENT_HOVER)
                    
                    def on_leave(event, btn=day_btn, orig_bg=bg_color):
                        if not is_selected:
                            btn.config(bg=orig_bg)
                    
                    day_btn.bind("<Enter>", on_enter)
                    day_btn.bind("<Leave>", on_leave)


class TodoTab:
    """Daily todo list tab"""
    
    def __init__(self, parent, data_manager):
        self.parent = parent
        self.data_manager = data_manager
        self.current_date = date.today()
        
        # Main frame
        self.main_frame = tk.Frame(parent, bg=DarkTheme.BG_PRIMARY)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Todo list
        self.left_frame = tk.Frame(self.main_frame, bg=DarkTheme.BG_PRIMARY)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right side - Clock and weather
        self.right_frame = tk.Frame(self.main_frame, bg=DarkTheme.BG_PRIMARY, width=250)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        self.right_frame.pack_propagate(False)
        
        self.setup_todo_list()
        self.setup_clock_weather()
        self.load_todos()
    
    def setup_todo_list(self):
        """Setup the todo list interface"""
        # Header
        header_frame = tk.Frame(self.left_frame, bg=DarkTheme.BG_PRIMARY)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date navigation with calendar
        nav_frame = tk.Frame(header_frame, bg=DarkTheme.BG_PRIMARY)
        nav_frame.pack(fill=tk.X)
        
        # Quick navigation buttons
        quick_nav_frame = tk.Frame(nav_frame, bg=DarkTheme.BG_PRIMARY)
        quick_nav_frame.pack(side=tk.LEFT)
        
        tk.Button(
            quick_nav_frame,
            text="◀",
            command=self.prev_day,
            bg=DarkTheme.BG_TERTIARY,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 12),
            relief="flat",
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            quick_nav_frame,
            text="▶",
            command=self.next_day,
            bg=DarkTheme.BG_TERTIARY,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 12),
            relief="flat",
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Date display with calendar toggle
        date_frame = tk.Frame(nav_frame, bg=DarkTheme.BG_PRIMARY)
        date_frame.pack(side=tk.LEFT, expand=True)
        
        self.date_label = tk.Label(
            date_frame,
            text=self.current_date.strftime("%A, %B %d, %Y"),
            font=("Arial", 16, "bold"),
            bg=DarkTheme.BG_PRIMARY,
            fg=DarkTheme.FG_PRIMARY
        )
        self.date_label.pack()
        
        # Calendar toggle button
        self.calendar_toggle_btn = tk.Button(
            date_frame,
            text="📅 Select Date",
            command=self.toggle_calendar,
            bg=DarkTheme.ACCENT,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 10),
            relief="flat",
            cursor="hand2"
        )
        self.calendar_toggle_btn.pack(pady=(5, 0))
        
        # Right side buttons
        right_buttons_frame = tk.Frame(nav_frame, bg=DarkTheme.BG_PRIMARY)
        right_buttons_frame.pack(side=tk.RIGHT)
        
        tk.Button(
            right_buttons_frame,
            text="Today",
            command=self.go_to_today,
            bg=DarkTheme.SUCCESS,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 10),
            relief="flat",
            cursor="hand2"
        ).pack()
        
        # Calendar widget (initially hidden)
        self.calendar_frame = tk.Frame(header_frame, bg=DarkTheme.BG_PRIMARY)
        self.calendar_visible = False
        
        self.calendar_widget = CalendarWidget(
            self.calendar_frame, 
            callback=self.on_date_selected,
            current_date=self.current_date
        )
        self.calendar_widget.frame.pack(pady=10)
        
        # Add new todo
        add_frame = tk.Frame(header_frame, bg=DarkTheme.BG_PRIMARY)
        add_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.new_todo_entry = tk.Entry(
            add_frame,
            font=("Arial", 12),
            bg=DarkTheme.BG_SECONDARY,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            relief="flat"
        )
        self.new_todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.new_todo_entry.bind("<Return>", self.add_todo)
        
        tk.Button(
            add_frame,
            text="Add Task",
            command=self.add_todo,
            bg=DarkTheme.SUCCESS,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 10),
            relief="flat",
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Todo list
        list_frame = tk.Frame(self.left_frame, bg=DarkTheme.BG_PRIMARY)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable todo list
        self.todo_canvas = tk.Canvas(
            list_frame,
            bg=DarkTheme.BG_PRIMARY,
            highlightthickness=0
        )
        self.todo_scrollbar = tk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.todo_canvas.yview,
            bg=DarkTheme.BG_SECONDARY
        )
        self.todo_scrollable_frame = tk.Frame(self.todo_canvas, bg=DarkTheme.BG_PRIMARY)
        
        self.todo_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.todo_canvas.configure(scrollregion=self.todo_canvas.bbox("all"))
        )
        
        self.todo_canvas.create_window((0, 0), window=self.todo_scrollable_frame, anchor="nw")
        self.todo_canvas.configure(yscrollcommand=self.todo_scrollbar.set)
        
        self.todo_canvas.pack(side="left", fill="both", expand=True)
        self.todo_scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        self.todo_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        self.todos = []
    
    def setup_clock_weather(self):
        """Setup clock and weather widgets"""
        # Clock
        clock_frame = tk.Frame(self.right_frame, bg=DarkTheme.BG_SECONDARY)
        clock_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.clock = AnalogClock(clock_frame)
        
        # Weather
        weather_frame = tk.Frame(self.right_frame, bg=DarkTheme.BG_SECONDARY)
        weather_frame.pack(fill=tk.X)
        
        self.weather = WeatherWidget(weather_frame, self.data_manager)
        self.weather.frame.pack(fill=tk.X)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.todo_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def prev_day(self):
        """Go to previous day"""
        self.current_date -= timedelta(days=1)
        self.update_date_display()
        self.load_todos()
    
    def next_day(self):
        """Go to next day"""
        self.current_date += timedelta(days=1)
        self.update_date_display()
        self.load_todos()
    
    def go_to_today(self):
        """Go to today's date"""
        self.current_date = date.today()
        self.update_date_display()
        self.load_todos()
    
    def update_date_display(self):
        """Update the date display"""
        self.date_label.config(text=self.current_date.strftime("%A, %B %d, %Y"))
        # Update calendar widget's selected date
        if hasattr(self, 'calendar_widget'):
            self.calendar_widget.selected_date = self.current_date
            self.calendar_widget.viewing_date = date(self.current_date.year, self.current_date.month, 1)
            self.calendar_widget.render_calendar()
    
    def toggle_calendar(self):
        """Toggle calendar visibility"""
        if self.calendar_visible:
            self.calendar_frame.pack_forget()
            self.calendar_toggle_btn.config(text="📅 Select Date")
            self.calendar_visible = False
        else:
            # Pack calendar after the navigation frame
            nav_frame = self.calendar_toggle_btn.master.master
            if nav_frame:
                self.calendar_frame.pack(fill=tk.X, pady=(10, 0), after=nav_frame)
            else:
                self.calendar_frame.pack(fill=tk.X, pady=(10, 0))
            self.calendar_toggle_btn.config(text="📅 Hide Calendar")
            self.calendar_visible = True
    
    def on_date_selected(self, selected_date):
        """Handle date selection from calendar"""
        self.current_date = selected_date
        self.update_date_display()
        self.load_todos()
        # Auto-hide calendar after selection
        if self.calendar_visible:
            self.toggle_calendar()
    
    def celebration_animation(self, widget, callback=None):
        """Create a satisfying celebration animation when task is completed"""
        original_bg = widget.cget("bg")
        original_fg = widget.cget("fg")
        
        # Flash sequence with golden color
        def flash_step(step=0, max_steps=6):
            if step < max_steps:
                if step % 2 == 0:
                    # Flash to celebration color
                    widget.config(
                        bg=DarkTheme.COMPLETION_FLASH,
                        fg=DarkTheme.BG_PRIMARY
                    )
                    # Scale effect (simulate with font size)
                    current_font = widget.cget("font")
                    if isinstance(current_font, str):
                        font_parts = current_font.split()
                        if len(font_parts) >= 2:
                            size = int(font_parts[1]) if font_parts[1].isdigit() else 11
                        else:
                            size = 11
                    else:
                        size = current_font[1] if len(current_font) > 1 else 11
                    
                    widget.config(font=("Arial", size + 2, "bold"))
                else:
                    # Flash back to original
                    widget.config(bg=original_bg, fg=original_fg)
                    widget.config(font=("Arial", 11, "normal"))
                
                # Schedule next flash
                widget.after(150, lambda: flash_step(step + 1, max_steps))
            else:
                # Animation complete - final state
                widget.config(bg=original_bg, fg=original_fg)
                widget.config(font=("Arial", 11, "overstrike"))
                if callback:
                    callback()
        
        # Start the animation
        flash_step()
    
    def add_todo(self, event=None):
        """Add a new todo item"""
        text = self.new_todo_entry.get().strip()
        if text:
            todo = {
                "text": text,
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            self.todos.append(todo)
            self.new_todo_entry.delete(0, tk.END)
            self.render_todos()
            self.save_todos()
    
    def toggle_todo(self, index, checkbox_widget=None):
        """Toggle todo completion status with celebration animation"""
        was_completed = self.todos[index]["completed"]
        self.todos[index]["completed"] = not self.todos[index]["completed"]
        
        # If task is being completed (not uncompleted), show celebration
        if not was_completed and self.todos[index]["completed"] and checkbox_widget:
            # Start celebration animation
            def finish_toggle():
                self.render_todos()
                self.save_todos()
            
            self.celebration_animation(checkbox_widget, finish_toggle)
        else:
            # Normal toggle without animation
            self.render_todos()
            self.save_todos()
    
    def delete_todo(self, index):
        """Delete a todo item"""
        if messagebox.askyesno("Confirm", "Delete this task?"):
            self.todos.pop(index)
            self.render_todos()
            self.save_todos()
    
    def render_todos(self):
        """Render the todo list"""
        # Clear existing widgets
        for widget in self.todo_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.todos:
            tk.Label(
                self.todo_scrollable_frame,
                text="No tasks for this day",
                font=("Arial", 12),
                bg=DarkTheme.BG_PRIMARY,
                fg=DarkTheme.FG_MUTED
            ).pack(pady=20)
            return
        
        for i, todo in enumerate(self.todos):
            todo_frame = tk.Frame(
                self.todo_scrollable_frame,
                bg=DarkTheme.BG_SECONDARY,
                relief="solid",
                bd=1
            )
            todo_frame.pack(fill=tk.X, pady=2, padx=5)
            
            # Checkbox with animation support
            checkbox_var = tk.BooleanVar(value=todo["completed"])
            checkbox = tk.Checkbutton(
                todo_frame,
                text=todo["text"],
                variable=checkbox_var,
                bg=DarkTheme.BG_SECONDARY,
                fg=DarkTheme.FG_PRIMARY if not todo["completed"] else DarkTheme.FG_MUTED,
                selectcolor=DarkTheme.BG_TERTIARY,
                font=("Arial", 11),
                anchor="w"
            )
            
            # Custom command to pass the widget reference
            def create_toggle_command(idx, widget):
                return lambda: self.toggle_todo(idx, widget)
            
            checkbox.config(command=create_toggle_command(i, checkbox))
            checkbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
            
            # Strike through completed tasks
            if todo["completed"]:
                checkbox.config(font=("Arial", 11, "overstrike"))
            
            # Delete button
            delete_btn = tk.Button(
                todo_frame,
                text="✕",
                command=lambda idx=i: self.delete_todo(idx),
                bg=DarkTheme.ERROR,
                fg=DarkTheme.FG_PRIMARY,
                font=("Arial", 8),
                relief="flat",
                cursor="hand2",
                width=3
            )
            delete_btn.pack(side=tk.RIGHT, padx=5)
    
    def load_todos(self):
        """Load todos for current date"""
        date_str = self.current_date.strftime("%Y-%m-%d")
        self.todos = self.data_manager.load_daily_todos(date_str)
        self.render_todos()
    
    def save_todos(self):
        """Save todos for current date"""
        date_str = self.current_date.strftime("%Y-%m-%d")
        self.data_manager.save_daily_todos(date_str, self.todos)


class ProjectsTab:
    """Projects and goals management tab"""
    
    def __init__(self, parent, data_manager):
        self.parent = parent
        self.data_manager = data_manager
        self.projects = self.data_manager.load_projects()
        
        # Main frame
        self.main_frame = tk.Frame(parent, bg=DarkTheme.BG_PRIMARY)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.setup_projects_interface()
        self.render_projects()
    
    def setup_projects_interface(self):
        """Setup the projects interface"""
        # Header
        header_frame = tk.Frame(self.main_frame, bg=DarkTheme.BG_PRIMARY)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            header_frame,
            text="Projects & Goals",
            font=("Arial", 18, "bold"),
            bg=DarkTheme.BG_PRIMARY,
            fg=DarkTheme.FG_PRIMARY
        ).pack(side=tk.LEFT)
        
        tk.Button(
            header_frame,
            text="+ New Project",
            command=self.add_project,
            bg=DarkTheme.SUCCESS,
            fg=DarkTheme.FG_PRIMARY,
            font=("Arial", 10),
            relief="flat",
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Projects list
        self.projects_frame = tk.Frame(self.main_frame, bg=DarkTheme.BG_PRIMARY)
        self.projects_frame.pack(fill=tk.BOTH, expand=True)
    
    def add_project(self):
        """Add a new project"""
        name = simpledialog.askstring("New Project", "Enter project name:")
        if name:
            project_id = str(len(self.projects) + 1)
            self.projects[project_id] = {
                "name": name,
                "description": "",
                "steps": [],
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            self.save_projects()
            self.render_projects()
    
    def edit_project(self, project_id):
        """Edit project details"""
        project = self.projects[project_id]
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Project")
        dialog.geometry("500x400")
        dialog.configure(bg=DarkTheme.BG_PRIMARY)
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Project name
        tk.Label(dialog, text="Project Name:", bg=DarkTheme.BG_PRIMARY, fg=DarkTheme.FG_PRIMARY).pack(pady=5)
        name_entry = tk.Entry(dialog, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.FG_PRIMARY, insertbackground=DarkTheme.FG_PRIMARY, width=50)
        name_entry.insert(0, project["name"])
        name_entry.pack(pady=5)
        
        # Description
        tk.Label(dialog, text="Description:", bg=DarkTheme.BG_PRIMARY, fg=DarkTheme.FG_PRIMARY).pack(pady=5)
        desc_text = tk.Text(dialog, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.FG_PRIMARY, insertbackground=DarkTheme.FG_PRIMARY, width=50, height=5)
        desc_text.insert(tk.END, project.get("description", ""))
        desc_text.pack(pady=5)
        
        # Steps
        tk.Label(dialog, text="Steps:", bg=DarkTheme.BG_PRIMARY, fg=DarkTheme.FG_PRIMARY).pack(pady=5)
        
        steps_frame = tk.Frame(dialog, bg=DarkTheme.BG_PRIMARY)
        steps_frame.pack(fill=tk.X, padx=20)
        
        steps_listbox = tk.Listbox(
            steps_frame,
            bg=DarkTheme.BG_SECONDARY,
            fg=DarkTheme.FG_PRIMARY,
            selectbackground=DarkTheme.ACCENT,
            height=8
        )
        steps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(steps_frame, orient=tk.VERTICAL, command=steps_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        steps_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate steps
        for step in project.get("steps", []):
            status = "✓" if step["completed"] else "○"
            steps_listbox.insert(tk.END, f"{status} {step['text']}")
        
        # Step management buttons
        step_btn_frame = tk.Frame(dialog, bg=DarkTheme.BG_PRIMARY)
        step_btn_frame.pack(pady=5)
        
        def add_step():
            step_text = simpledialog.askstring("New Step", "Enter step description:")
            if step_text:
                project["steps"].append({"text": step_text, "completed": False})
                steps_listbox.insert(tk.END, f"○ {step_text}")
        
        def toggle_step():
            selection = steps_listbox.curselection()
            if selection:
                index = selection[0]
                step = project["steps"][index]
                step["completed"] = not step["completed"]
                status = "✓" if step["completed"] else "○"
                steps_listbox.delete(index)
                steps_listbox.insert(index, f"{status} {step['text']}")
        
        def delete_step():
            selection = steps_listbox.curselection()
            if selection:
                index = selection[0]
                if messagebox.askyesno("Confirm", "Delete this step?"):
                    project["steps"].pop(index)
                    steps_listbox.delete(index)
        
        tk.Button(step_btn_frame, text="Add Step", command=add_step, bg=DarkTheme.SUCCESS, fg=DarkTheme.FG_PRIMARY, font=("Arial", 8), relief="flat").pack(side=tk.LEFT, padx=2)
        tk.Button(step_btn_frame, text="Toggle", command=toggle_step, bg=DarkTheme.ACCENT, fg=DarkTheme.FG_PRIMARY, font=("Arial", 8), relief="flat").pack(side=tk.LEFT, padx=2)
        tk.Button(step_btn_frame, text="Delete", command=delete_step, bg=DarkTheme.ERROR, fg=DarkTheme.FG_PRIMARY, font=("Arial", 8), relief="flat").pack(side=tk.LEFT, padx=2)
        
        # Save and Cancel buttons
        btn_frame = tk.Frame(dialog, bg=DarkTheme.BG_PRIMARY)
        btn_frame.pack(pady=10)
        
        def save_project():
            project["name"] = name_entry.get()
            project["description"] = desc_text.get("1.0", tk.END).strip()
            self.save_projects()
            self.render_projects()
            dialog.destroy()
        
        tk.Button(btn_frame, text="Save", command=save_project, bg=DarkTheme.SUCCESS, fg=DarkTheme.FG_PRIMARY, font=("Arial", 10), relief="flat").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, bg=DarkTheme.BG_TERTIARY, fg=DarkTheme.FG_PRIMARY, font=("Arial", 10), relief="flat").pack(side=tk.LEFT, padx=5)
    
    def delete_project(self, project_id):
        """Delete a project"""
        if messagebox.askyesno("Confirm", "Delete this project?"):
            del self.projects[project_id]
            self.save_projects()
            self.render_projects()
    
    def toggle_project_completion(self, project_id):
        """Toggle project completion status"""
        self.projects[project_id]["completed"] = not self.projects[project_id]["completed"]
        self.save_projects()
        self.render_projects()
    
    def render_projects(self):
        """Render the projects list"""
        # Clear existing widgets
        for widget in self.projects_frame.winfo_children():
            widget.destroy()
        
        if not self.projects:
            tk.Label(
                self.projects_frame,
                text="No projects yet",
                font=("Arial", 12),
                bg=DarkTheme.BG_PRIMARY,
                fg=DarkTheme.FG_MUTED
            ).pack(pady=20)
            return
        
        for project_id, project in self.projects.items():
            project_frame = tk.Frame(
                self.projects_frame,
                bg=DarkTheme.BG_SECONDARY,
                relief="solid",
                bd=1
            )
            project_frame.pack(fill=tk.X, pady=5, padx=10)
            
            # Project header
            header_frame = tk.Frame(project_frame, bg=DarkTheme.BG_SECONDARY)
            header_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Project name and completion status
            name_frame = tk.Frame(header_frame, bg=DarkTheme.BG_SECONDARY)
            name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            completed_var = tk.BooleanVar(value=project["completed"])
            project_checkbox = tk.Checkbutton(
                name_frame,
                text=project["name"],
                variable=completed_var,
                command=lambda pid=project_id: self.toggle_project_completion(pid),
                bg=DarkTheme.BG_SECONDARY,
                fg=DarkTheme.FG_PRIMARY if not project["completed"] else DarkTheme.FG_MUTED,
                selectcolor=DarkTheme.BG_TERTIARY,
                font=("Arial", 14, "bold"),
                anchor="w"
            )
            project_checkbox.pack(side=tk.LEFT)
            
            if project["completed"]:
                project_checkbox.config(font=("Arial", 14, "bold", "overstrike"))
            
            # Action buttons
            btn_frame = tk.Frame(header_frame, bg=DarkTheme.BG_SECONDARY)
            btn_frame.pack(side=tk.RIGHT)
            
            tk.Button(
                btn_frame,
                text="Edit",
                command=lambda pid=project_id: self.edit_project(pid),
                bg=DarkTheme.ACCENT,
                fg=DarkTheme.FG_PRIMARY,
                font=("Arial", 8),
                relief="flat",
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=2)
            
            tk.Button(
                btn_frame,
                text="Delete",
                command=lambda pid=project_id: self.delete_project(pid),
                bg=DarkTheme.ERROR,
                fg=DarkTheme.FG_PRIMARY,
                font=("Arial", 8),
                relief="flat",
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=2)
            
            # Description
            if project.get("description"):
                desc_label = tk.Label(
                    project_frame,
                    text=project["description"],
                    font=("Arial", 10),
                    bg=DarkTheme.BG_SECONDARY,
                    fg=DarkTheme.FG_SECONDARY,
                    wraplength=400,
                    justify=tk.LEFT
                )
                desc_label.pack(anchor=tk.W, padx=10, pady=(0, 5))
            
            # Steps progress
            steps = project.get("steps", [])
            if steps:
                completed_steps = sum(1 for step in steps if step["completed"])
                total_steps = len(steps)
                progress_text = f"Progress: {completed_steps}/{total_steps} steps completed"
                
                tk.Label(
                    project_frame,
                    text=progress_text,
                    font=("Arial", 9),
                    bg=DarkTheme.BG_SECONDARY,
                    fg=DarkTheme.FG_MUTED
                ).pack(anchor=tk.W, padx=10, pady=(0, 10))
    
    def save_projects(self):
        """Save projects data"""
        self.data_manager.save_projects(self.projects)


class TodoApp:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dark Mode Todo List")
        self.root.geometry("1200x800")
        self.root.configure(bg=DarkTheme.BG_PRIMARY)
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Setup UI
        self.setup_ui()
        
        # Center window
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_ui(self):
        """Setup the main UI"""
        # Configure style for ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure ttk styles for dark theme
        style.configure('TNotebook', background=DarkTheme.BG_PRIMARY)
        style.configure('TNotebook.Tab', background=DarkTheme.BG_SECONDARY, foreground=DarkTheme.FG_PRIMARY)
        style.map('TNotebook.Tab', background=[('selected', DarkTheme.BG_TERTIARY)])
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Todo tab
        self.todo_frame = tk.Frame(self.notebook, bg=DarkTheme.BG_PRIMARY)
        self.notebook.add(self.todo_frame, text="Daily Tasks")
        
        # Projects tab
        self.projects_frame = tk.Frame(self.notebook, bg=DarkTheme.BG_PRIMARY)
        self.notebook.add(self.projects_frame, text="Projects & Goals")
        
        # Initialize tabs
        self.todo_tab = TodoTab(self.todo_frame, self.data_manager)
        self.projects_tab = ProjectsTab(self.projects_frame, self.data_manager)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = TodoApp()
    app.run()