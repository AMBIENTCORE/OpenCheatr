# OpenCheatr - OpenGuessr Location Detector

![image](assets/I-pixel-u.ttf)

Currently compatible with **Windows, macOS, and Linux**.

A desktop application that automatically detects and displays the 5 round locations from OpenGuessr games. It monitors network traffic to capture location coordinates and displays them on an interactive map with detailed location information.

## Backstory

I created this tool to help with OpenGuessr gameplay by automatically detecting the 5 round locations that are normally hidden until you make your guesses. The application uses browser automation to monitor network requests and extract location coordinates, then displays them on a map for easy reference.

The tool was built using Python with a modern dark-themed GUI and includes both embedded map display and browser-based map generation for detailed viewing.

## Features

- 🎯 Automatic detection of OpenGuessr round locations (5 rounds per game)
- 🗺️ Interactive map display with numbered pins for each round
- 📍 Detailed location information with reverse geocoding
- 🌐 Browser-based map generation for detailed viewing
- 🖥️ Modern dark-themed desktop interface
- 🔄 Real-time monitoring of OpenGuessr network traffic
- 📊 Live logging of detection events and location details
- 🎮 Works with any OpenGuessr game session

## How It Works

1. **Launch Detection**: Click "LAUNCH" to start monitoring OpenGuessr
2. **Browser Automation**: Opens a Chromium browser window to OpenGuessr.com
3. **Network Monitoring**: Watches for location data in network requests
4. **Location Extraction**: Automatically captures the 5 round coordinates
5. **Map Generation**: Creates an interactive map with numbered pins
6. **Location Details**: Provides detailed location information for each round

## Dependencies

- tkinter - GUI framework
- playwright - Browser automation
- folium - Interactive map generation
- requests - HTTP requests for reverse geocoding
- tkintermapview - Embedded map widget (optional)

## Installation

1. Clone the repository
2. Optional: Setup a virtual environment so dependencies are not installed globally:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python3 OpenCheatr.py
```

## Usage

1. **Launch the Application**: Run `OpenCheatr.py`
2. **Start Monitoring**: Click the "LAUNCH" button
3. **Play OpenGuessr**: A Chromium browser window will open to OpenGuessr.com
4. **Start a Game**: Begin any OpenGuessr game - the tool will automatically detect the 5 round locations
5. **View Results**: 
   - See locations on the embedded map with numbered pins
   - Check the log panel for detailed location information
   - Click "OPEN WEB MAP" for a detailed browser-based map
6. **Clear and Restart**: Use "CLEAR" to reset and start a new game

## Map Features

- **Embedded Map**: Interactive map display within the application
- **Numbered Pins**: Each round location is marked with a number (1-5)
- **Location Details**: Reverse geocoding provides city, state, and country information
- **Browser Map**: Detailed map opens in your default browser with auto-refresh
- **Coordinate Display**: Exact latitude and longitude coordinates for each round

## Technical Details

- **Network Monitoring**: Uses Playwright to intercept OpenGuessr's location API calls
- **Reverse Geocoding**: Uses OpenStreetMap's Nominatim service for location details
- **Map Generation**: Creates interactive Folium maps with custom styling
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Real-time Updates**: Automatically updates as new locations are detected

## File Structure

```
OpenCheatr/
├── OpenCheatr.py              # Main application file
├── assets/
│   └── I-pixel-u.ttf         # Custom pixel font
├── openguessr_round_map.html  # Generated map file
└── README.md                  # This file
```

## Contributing

Contributions are welcome!
Please feel free to submit a Pull Request.

## License

MIT
