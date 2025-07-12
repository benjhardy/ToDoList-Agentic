# Dark Mode Todo List Application

A sophisticated Python-based todo list application with dark mode theming, daily task management, project tracking, analog clock, and weather integration.

## Features

### 🌙 Dark Mode Design
- Beautiful dark theme throughout the application
- Modern UI with smooth styling and hover effects
- Eye-friendly color scheme

### 📅 Daily Task Management
- Add, edit, and delete daily tasks
- Navigate between dates to view historical tasks
- Tasks are automatically saved for each day
- Strike-through completed tasks
- Today button for quick navigation

### 🕐 Analog Clock
- Real-time analog clock display
- Shows current date
- Updates every second with smooth animations

### 🌤️ Weather Integration
- Display current weather for your location
- Temperature and weather description
- Configurable zip code
- Uses OpenWeatherMap API (free tier available)
- Updates every 30 minutes

### 📊 Projects & Goals
- Create and manage long-term projects
- Break down projects into smaller steps
- Track progress with step completion
- Project descriptions and completion status
- Visual progress indicators

### 💾 Data Persistence
- All data automatically saved to JSON files
- Separate storage for daily tasks, projects, and settings
- No data loss between sessions

## Installation

1. **Clone or download the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Weather Setup (Optional)

To enable weather functionality:

1. **Get a free API key:**
   - Visit [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up for a free account
   - Get your API key

2. **Configure weather settings:**
   - Click "Weather Settings" in the application
   - Enter your zip code
   - Enter your API key
   - Click Save

## Usage

### Daily Tasks Tab
- **Add tasks:** Type in the text field and press Enter or click "Add Task"
- **Complete tasks:** Click the checkbox next to any task
- **Delete tasks:** Click the red × button
- **Navigate dates:** Use ◀ and ▶ buttons or click "Today"
- **View history:** Navigate to previous days to see past tasks

### Projects & Goals Tab
- **Add projects:** Click "+ New Project" and enter a name
- **Edit projects:** Click "Edit" to modify details, add steps, or descriptions
- **Manage steps:** In the edit dialog, add, toggle, or delete project steps
- **Track progress:** See completion progress for each project
- **Complete projects:** Check the main project checkbox

## File Structure

```
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── data/               # Created automatically
    ├── todos_YYYY-MM-DD.json  # Daily tasks
    ├── projects.json          # Projects and goals
    └── settings.json          # App settings
```

## Keyboard Shortcuts

- **Enter:** Add new task (when in task input field)
- **Tab:** Navigate between interface elements
- **Space:** Toggle checkboxes when focused

## Customization

The application uses a centralized theme system. To customize colors, modify the `DarkTheme` class in `main.py`:

```python
class DarkTheme:
    BG_PRIMARY = "#1a1a1a"    # Main background
    BG_SECONDARY = "#2d2d2d"  # Secondary background
    BG_TERTIARY = "#3a3a3a"   # Tertiary background
    FG_PRIMARY = "#ffffff"    # Main text
    FG_SECONDARY = "#cccccc"  # Secondary text
    FG_MUTED = "#888888"      # Muted text
    ACCENT = "#4a9eff"        # Accent color
    SUCCESS = "#4caf50"       # Success color
    ERROR = "#f44336"         # Error color
```

## Troubleshooting

### Weather not loading
- Ensure you have a valid API key from OpenWeatherMap
- Check your internet connection
- Verify your zip code is correct
- The free tier has usage limits

### Data not saving
- Check that the application has write permissions in its directory
- Ensure sufficient disk space
- The `data/` folder should be created automatically

### Clock not updating
- This should resolve automatically
- Try restarting the application if issues persist

## Dependencies

- `tkinter` - GUI framework (built into Python)
- `requests` - HTTP requests for weather API
- `pillow` - Image processing (for potential future enhancements)
- `python-dateutil` - Date utilities

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
