---
name: gods-eye-view
description: "Browser-based satellite imagery simulator using real public data. Explore Earth with spy-satellite-style views, real-time data overlays, and global surveillance visualization. Use when the user wants to visualize geographic data, explore satellite imagery, build OSINT dashboards, or needs an interactive map with real public data layers. Triggers on: satellite view, OSINT, geographic visualization, real-time map, global data, 卫星地图, 地理可视化, 公开数据."
license: MIT
compatibility: Runs entirely in browser. No installation required. Works with Chrome, Firefox, Safari, Edge. Uses public satellite imagery and open data APIs.
metadata:
  author: bilawalsidhu (curated by AthenDrakomin-hub)
  version: "1.0.0"
  category: visualization
  source: "https://github.com/bilawalsidhu/gods-eye-view"
---

# God's Eye View

Browser-based satellite imagery simulator. Explore Earth with real public satellite data, surveillance-style UI, and interactive global visualization.

## Role

You are a geospatial intelligence specialist. Your job is to help users use God's Eye View to explore satellite imagery, visualize geographic data, and build OSINT-style dashboards using real public data.

## What It Is

God's Eye View is a browser application that renders satellite imagery of Earth with a surveillance/spy-satellite aesthetic. It uses real public data sources (NASA, ESA, OpenStreetMap, weather APIs) and presents them in an interactive, cinematic interface.

## Core Capabilities

### 1. Satellite Imagery Browser
- Global satellite imagery with zoom and pan
- Multiple imagery layers (visible, infrared, thermal)
- Historical imagery comparison (where available)
- Coordinate display and measurement tools

### 2. Real-Time Data Overlays
- Weather patterns and storm tracking
- Air traffic (public ADS-B data)
- Maritime traffic (AIS data)
- Seismic activity
- Wildfire and natural disaster monitoring

### 3. Surveillance-Style UI
- Cinematic HUD with targeting reticles
- Data panels with coordinates and metadata
- Scan line and glitch effects
- Night-vision and thermal view modes

### 4. Location Intelligence
- Search by coordinates, address, or landmark
- Save and bookmark locations
- Measure distances and areas
- Export screenshots and data

## Usage

### Access
Open in any modern browser: https://godseyeview.com (or self-host from GitHub repo)

No installation, no account, no API key required for basic functionality.

### Basic Navigation
- **Scroll**: zoom in/out
- **Drag**: pan the map
- **Click**: select location, view metadata
- **Search bar**: enter coordinates (lat, lng) or place name
- **Layer toggle**: switch between imagery / infrared / thermal / data overlays

### Data Layers

| Layer | Source | Update Frequency |
|---|---|---|
| Satellite imagery | NASA/ESA public tiles | Daily to weekly |
| Weather | OpenWeatherMap / NOAA | Hourly |
| Air traffic | OpenSky Network (ADS-B) | Real-time |
| Maritime | MarineTraffic (AIS) | Real-time |
| Seismic | USGS | Real-time |
| Wildfires | NASA FIRMS | Daily |
| Night lights | NASA VIIRS | Monthly |

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `Space` | Toggle scan effect |
| `N` | Night vision mode |
| `T` | Thermal view |
| `R` | Rotate view |
| `M` | Measure distance |
| `S` | Screenshot |
| `+` / `-` | Zoom in/out |
| `Esc` | Close panel |

## Self-Hosting

```bash
git clone https://github.com/bilawalsidhu/gods-eye-view.git
cd gods-eye-view
# Static site — open index.html directly or serve with any web server
python -m http.server 8080
# Open http://localhost:8080
```

No build step, no backend required. All data comes from public APIs client-side.

## Use Cases

### OSINT Investigation
- Cross-reference locations with multiple data layers
- Track activity patterns over time
- Document findings with timestamped screenshots

### Education & Demonstration
- Teach satellite imagery interpretation
- Demonstrate real-time global data streams
- Visualize geographic concepts

### Journalism & Research
- Verify event locations with satellite imagery
- Monitor environmental changes
- Create data-driven visualizations

### Creative & Entertainment
- Cinematic map backgrounds for videos
- Spy-thriller aesthetic for presentations
- Interactive fiction worldbuilding

## Privacy & Ethics

- Uses only publicly available data sources
- Does not access private or classified imagery
- Resolution limited to public satellite data (typically 0.5-10m)
- No real-time person tracking (legal and technical limitations)
- Users are responsible for compliance with local laws regarding imagery use

## Troubleshooting

| Problem | Solution |
|---|---|
| Imagery not loading | Check internet connection, try different layer, clear cache |
| Data overlay empty | Some APIs have rate limits; wait and retry |
| Performance lag | Reduce zoom level, disable heavy layers, use Chrome |
| Mobile touch issues | Use two-finger drag for pan, pinch for zoom |
| API key errors | Some layers require free API keys; check console for specifics |

## References

- GitHub: https://github.com/bilawalsidhu/gods-eye-view
- Live demo: https://godseyeview.com
- NASA Earthdata: https://earthdata.nasa.gov
- OpenSky Network: https://opensky-network.org
- USGS Earthquake: https://earthquake.usgs.gov
