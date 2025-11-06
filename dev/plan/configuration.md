# Configuration Guide

## Overview

Configuration files, settings, and deployment procedures for the Transit Automation System.

## Configuration Files

### 1. orchestrator_config.json

**Location:** `/Users/av/0-prod/transit/config/orchestrator_config.json`

**Key Settings:**
```json
{
  "paths": {
    "input_dir": "/Users/av/0-prod/transit/workbench/input",
    "output_dir": "/Users/av/0-prod/transit/workbench/output",
    "speakers_db": "/Users/av/0-prod/transit/config/speakers_db.json",
    "audio_profiles": "/Users/av/0-prod/transit/config/audio_profiles"
  },
  
  "speaker_detection": {
    "auto_assign_threshold": 0.80,
    "extract_audio_profiles": true,
    "sample_duration_ms": 3500
  },
  
  "projects": {
    "wir24": {
      "enabled": true,
      "reference_path": "/Users/av/PARA/01 PROJECTS/WIR24.../",
      "output_path": "/Users/av/PARA/.../Sessions",
      "enable_enhancement": true
    }
  },
  
  "notifications": {
    "desktop_on_success": true,
    "email_on_failure": true
  },
  
  "email": {
    "to_address": "arne.voelker@aebivoelkerund.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
  }
}
```

---

### 2. speakers_db.json

**Location:** `/Users/av/0-prod/transit/config/speakers_db.json`

**Structure:**
```json
{
  "projects": {
    "wir24": {
      "common_participants": [
        "Arne", "Rebecca", "Denise", "Igor", "Tobias"
      ],
      "speaker_profiles": {
        "Arne": {
          "audio_samples": [...]
        }
      },
      "filename_patterns": {
        "rebecca.*arne": {
          "speakers": ["Rebecca", "Arne"],
          "confidence": 0.85
        }
      }
    }
  }
}
```

---

### 3. Environment Variables

**File:** `.env` (not in version control)

```bash
# AssemblyAI API Key
ASSEMBLYAI_API_KEY=your_api_key_here

# Email Configuration
TRANSIT_EMAIL_PASSWORD=your_app_password_here
TRANSIT_EMAIL_USER=transit@aebivoelkerund.com
```

**Security:**
```bash
chmod 600 .env
echo ".env" >> .gitignore
```

---

### 4. launchd Service

**File:** `~/Library/LaunchAgents/com.aebivoelkerund.transit.plist`

**Key Settings:**
```xml
<key>ProgramArguments</key>
<array>
    <string>/usr/local/bin/python3</string>
    <string>/Users/av/0-prod/transit/src/transit/watcher.py</string>
    <string>--daemon</string>
</array>

<key>RunAtLoad</key>
<true/>

<key>KeepAlive</key>
<true/>
```

**Management:**
```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.aebivoelkerund.transit.plist

# Check status
launchctl list | grep transit

# View logs
tail -f logs/watcher.out.log
```

---

## Installation

### 1. Clone Repository
```bash
cd /Users/av/0-prod
git clone <repository-url> transit
cd transit
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
brew install ffmpeg
```

### 3. Create Directories
```bash
mkdir -p workbench/input
mkdir -p workbench/output
mkdir -p config/audio_profiles
mkdir -p logs
```

### 4. Configure Environment
```bash
cp .env.example .env
nano .env  # Add your credentials
```

### 5. Initialize Configuration
```bash
cp config/orchestrator_config.example.json config/orchestrator_config.json
cp config/speakers_db.example.json config/speakers_db.json
```

### 6. Test Installation
```bash
python src/transit/orchestrator.py --test
```

### 7. Install Service (Phase 2)
```bash
./scripts/install_service.sh
```

---

## Maintenance

### Daily
- Monitor log files
- Check service status

### Weekly
- Review detection accuracy
- Check profile library growth

### Monthly
- Backup configurations
- Update filename patterns
- Performance optimization

---

## Troubleshooting

### Service Won't Start
```bash
# Check plist syntax
plutil -lint ~/Library/LaunchAgents/com.aebivoelkerund.transit.plist

# View logs
log show --predicate 'process == "launchd"' | grep transit
```

### Processing Failures
```bash
# Test API connection
curl -H "Authorization: $ASSEMBLYAI_API_KEY" \
     https://api.assemblyai.com/v2/upload

# Check FFmpeg
ffmpeg -version
```

### Notification Issues
```bash
# Test desktop notification
osascript -e 'display notification "Test" with title "Transit"'

# Test email
python -c "from transit.notification_manager import send_email; ..."
```

---

For complete configuration reference, see full documentation.
