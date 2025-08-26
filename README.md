# Matter Device Configuration Tool

A simple Python script to configure Matter device attributes via Home Assistant's Matter Server. This tool allows you to read and write any attribute on any Matter device, making it easy to customize device behavior that isn't exposed through the standard Home Assistant UI.

## 🔍 How It Works

The script uses Home Assistant's Matter Server WebSocket API to:

1. **Connect** to the Matter Server via WebSocket
2. **Read** current attribute value using `read_attribute` command
3. **Write** new value using `write_attribute` command  
4. **Verify** the change was applied successfully
5. **Report** success or failure with detailed logging

The Matter Server handles all the low-level Matter protocol communication, making device configuration simple and reliable.

## 📋 Prerequisites

### Home Assistant Setup
- **Home Assistant** with Matter integration enabled
- **Matter Server Add-on** installed and running
- Matter devices already commissioned to your network

### Python Environment
- **Python 3.9+** 
- **python-matter-server** library
- **aiohttp** library

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/sharaf-n/ha-matter-device-configure.git
cd ha-matter-device-configure
```

### 2. Run Setup Script
The setup script will create a virtual environment and install all dependencies:
```bash
source ./setup.sh
```

### 3. Ready to Use!
After setup completes, you can immediately use the tool:
```bash
python matter_config.py 3 1 1030 3 30
```

### Subsequent Usage
Each time you want to use the tool, run the setup script first to activate the environment:
```bash
source ./setup.sh
python matter_config.py [arguments...]
```

## 💡 Usage

### Quick Start
```bash
# First, activate the environment
source ./setup.sh

# Interactive mode - prompts for all values
python matter_config.py

# All arguments provided
python matter_config.py 3 1 1030 3 30

# Partial arguments - prompts for missing ones
python matter_config.py 3 1 1030
```

### Argument Order
1. **Node ID** - Matter device node ID (find in HA Developer Tools)
2. **Endpoint ID** - Usually `1` for most devices
3. **Cluster ID** - Matter cluster (e.g., `1030` for OccupancySensing)
4. **Attribute ID** - Specific attribute within the cluster
5. **Value** - New value to set (1-65535)
6. **URL** (optional) - Matter server URL (defaults to `ws://homeassistant.local:5580/ws`)

## 🎯 Common Use Case

### Aqara P2 Motion Sensor - HoldTime Configuration
The Aqara P2 motion sensor has a default 60-second timeout before reporting "no motion". You can reduce this for faster automation responses:

```bash
# First activate environment
source ./setup.sh

# Set HoldTime to 30 seconds (faster response)
python matter_config.py 3 1 1030 3 30

# Set HoldTime to 10 seconds (very fast response)
python matter_config.py 3 1 1030 3 10

# Set HoldTime to 120 seconds (slower, battery saving)
python matter_config.py 3 1 1030 3 120
```

**Parameters Explained:**
- `3` - Node ID (your Aqara P2's ID in HA)
- `1` - Endpoint ID (standard for most devices)
- `1030` - OccupancySensing cluster ID
- `3` - HoldTime attribute ID
- `30` - New timeout value in seconds

## 🔧 Finding Device Information

The Matter Server add-on includes a web dashboard that provides detailed device information including node IDs, clusters, and attributes.

#### Accessing the WebUI

**Option A: Through Home Assistant Add-on Page**
1. **Navigate to Add-ons**:
   - Go to **Settings** → **Add-ons** in Home Assistant
   - Find **Matter Server** in your installed add-ons
   - Click on the **Matter Server** add-on

2. **Open Web UI**:
   - Look for **"Open Web UI"** button in the add-on page
   - Click it to open the Matter Server dashboard
   - This will open the web interface in a new tab

**Option B: Direct URL Access**
If the Web UI button isn't available, access directly:
```
http://homeassistant.local:5580
```
Or if using IP address:
```
http://[YOUR_HA_IP]:5580
```

#### Using the WebUI Dashboard

**1. Device Overview**
- The dashboard shows all commissioned Matter devices
- Each device displays its **Node ID** (this is what you need for the script)
- Device names and types are clearly labeled

**2. Device Details**
- Click on any device to view detailed information
- **Node Information** section shows:
  - Node ID (required for script)
  - Device type and manufacturer
  - Firmware version

**3. Endpoint Information**
- Below device details, you'll see **"Endpoints"** section
- Most devices have **Endpoint 1** (this is what you need for the script)
- Some complex devices may have multiple endpoints:
  - Endpoint 0 - Root device information
  - Endpoint 1 - Primary functionality (most common)
  - Endpoint 2+ - Additional features (multi-gang switches, etc.)

**4. Cluster Information**
- Within each endpoint, expand **"Clusters"** section
- Shows all available clusters with their **Cluster IDs**
- Common clusters you'll see:
  - `6` - OnOff (switches, lights)
  - `8` - LevelControl (dimmers)
  - `1030` - OccupancySensing (motion sensors)
  - `1024` - IlluminanceMeasurement (light sensors)

**5. Attribute Details**
- Within each cluster, expand to see **Attributes**
- Each attribute shows:
  - **Attribute ID** (required for script)
  - **Current Value**
  - **Data Type** (boolean, integer, etc.)
  - **Access Level** (read-only, read-write)

#### Finding Your Device Parameters

**For Aqara P2 Motion Sensor:**
1. Look for your motion sensor in the device list
2. Note the **Node ID** (usually 3, 4, 5, etc.)
3. Expand **Endpoint 1** (primary functionality)
4. Expand **OccupancySensing (1030)** cluster
5. Find **HoldTime (3)** attribute
6. Current value shows your current timeout setting

**Example WebUI Information:**
```
Device: Aqara Motion Sensor P2
Node ID: 3
├── Endpoint 0 (Root Device)
│   └── Cluster: Basic (40)
│       ├── VendorName (1) - Read Only - Current: "Aqara"
│       └── ProductName (3) - Read Only - Current: "Motion Sensor P2"
└── Endpoint 1 (Primary Sensor)
    └── Cluster: OccupancySensing (1030)
        ├── Occupancy (0) - Read Only - Current: false
        ├── OccupancySensorType (1) - Read Only - Current: 1
        └── HoldTime (3) - Read/Write - Current: 60
```

**Script Parameters from WebUI:**
- **Node ID**: 3 (from device header)
- **Endpoint ID**: 1 (primary functionality)
- **Cluster ID**: 1030 (OccupancySensing)
- **Attribute ID**: 3 (HoldTime)
- **New Value**: Your desired timeout (e.g., 30 seconds)

#### Troubleshooting WebUI Access

**If Web UI button is missing:**
- Ensure Matter Server add-on is running
- Restart the add-on if needed
- Check add-on logs for any errors

## 🛠️ Troubleshooting

### Connection Issues
```
ERROR: Could not connect to Matter server
```
**Solutions:**
- Verify Matter Server add-on is running
- Check the WebSocket URL (try `ws://homeassistant.local:5580/ws`)
- Ensure you're running from the correct network

### Device Not Found
```
ERROR: Node 3 not found
```
**Solutions:**
- Verify node ID in Home Assistant Developer Tools
- Ensure device is commissioned and online
- Try re-commissioning the device if necessary

### Attribute Write Failed
```
ERROR: Failed to write attribute
```
**Solutions:**
- Verify the attribute is writable (not read-only)
- Check if the value is within valid range
- Ensure device supports the specific attribute
- Some devices require specific conditions (e.g., device awake)

### Permission Denied
```
ERROR: Permission denied
```
**Solutions:**
- Run with appropriate permissions
- Ensure Matter Server has device access
- Check if device is in a special mode (pairing, etc.)

## 🤝 Contributing

### Reporting Issues
- Include your Home Assistant version
- Provide Matter Server logs
- Specify device model and firmware version
- Include the exact command that failed

### Code Contributions
- Follow existing code style
- Add appropriate error handling
- Update documentation for new features
- Test with multiple device types

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool directly modifies device attributes. While generally safe, incorrect configurations could potentially:
- Cause devices to behave unexpectedly
- Require device re-commissioning
- In rare cases, require factory reset

Always test changes on non-critical devices first and keep note of original values for rollback.

## 🙏 Acknowledgments

- Home Assistant team for the excellent Matter integration
- Python Matter Server developers
- Matter specification contributors
- Community members who shared device configurations

---

**Happy configuring!** 🏠✨

