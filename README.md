# /transit – Transcription and Speaker Labeling

Automated transcription and processing pipeline for audio and video files using AssemblyAI.

## Features

- **Automated Processing**: Transcribes all media files in directory that haven't been processed
- **Smart File Detection**: Avoids reprocessing files (checks for existing JSON)
- **Consistent Naming**: All outputs use the same base name as input media file
- **Multiple Formats**: Generates JSON transcript, SRT subtitles, and Markdown files
- **Speaker Diarization**: Identifies multiple speakers with preview functionality
- **Local File Support**: Processes local media files (no need to upload to URLs)
- **Auto Organization**: Automatically creates folders and organizes all related files
- **Video Preprocessing**: Automatically extracts audio from video files (MP4, AVI, MOV, etc.)
- **Large File Handling**: Handles files larger than 490MB by extracting audio

## Supported File Formats

Transit can process a wide range of audio and video formats:

### Audio Formats
- **MP3** - Most common audio format
- **WAV** - Uncompressed audio
- **M4A** - Apple audio format
- **AAC** - Advanced Audio Coding
- **FLAC** - Lossless audio
- **OGG** - Open source audio format

### Video Formats (automatically converted to audio)
- **MP4** - Most common video format
- **AVI** - Audio Video Interleave
- **MOV** - QuickTime format
- **MKV** - Matroska video
- **WebM** - Web video format
- **FLV** - Flash video
- **WMV** - Windows Media Video
- **M4V** - iTunes video format

Video files are automatically preprocessed using FFmpeg to extract the audio track before transcription. Files larger than 490MB are handled appropriately.

## Setup

1. Install required libraries:
   ```bash
   pip install assemblyai
   ```

2. Install FFmpeg for video preprocessing (optional, for video files):
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu**: `sudo apt install ffmpeg`
   - **Windows**: Download from https://ffmpeg.org/download.html

3. Set your API key as environment variable:
   ```bash
   export ASSEMBLYAI_API_KEY="your_api_key_here"
   ```

## Files Overview

### Core Scripts

All scripts are located in `src/transit/`:

- **`batch_process.py`** - Fully automated pipeline (no interaction required)
- **`video_preprocessor.py`** - Extracts audio from video files for transcription
- **`label_speakers.py`** - Interactive speaker relabeling for existing transcripts
- **`transcribe_pipeline.py`** - Full transcription pipeline (currently same as batch_process)
- **`processor_aai.py`** - Manual processor for existing JSON files
- **`organize_files.py`** - Standalone file organization tool


## Usage

### Quick Start with Workbench (Recommended)

1. **Place your media files** in `workbench/input/`
2. **Run the processing**:
   ```bash
   python -m src.transit.batch_process
   ```
3. **Find results** in `workbench/output/`

The workbench provides a clean separation between your media files and the source code. See `workbench/README.md` for detailed instructions.

### Automated Batch Processing

Process all unprocessed media files automatically:

```bash
# From project root (uses workbench if available)
python -m src.transit.batch_process

# Or process files in current directory
cd /your/media/folder
python /path/to/transit/src/transit/batch_process.py
```

This will:
1. **Run video preprocessor to extract audio from video files**
2. Find all media files in workbench/input/ or current directory
3. Skip files that already have corresponding JSON files  
4. Transcribe each unprocessed file using AssemblyAI
5. Generate SRT and Markdown files automatically
6. Use original speaker labels (A, B, C, D...)
7. **Organize all files into named folders automatically**

### Speaker Labeling (After Transcription)

To relabel speakers in existing transcripts:

```bash
# Automatically find and process the latest transcript
python -m src.transit.label_speakers

# Or specify a particular transcript
python -m src.transit.label_speakers "output/interview/interview.json"
```

This will:
1. Find the most recent transcript (or use the one you specify)
2. Show speaker statistics and sample text from each speaker
3. Let you assign meaningful names (e.g., "John", "Sarah") instead of A, B, C
4. Generate new output files with your custom speaker names

**Pro tip**: Run this after batch processing to add real names to your transcripts!

### Video Preprocessing

To extract audio from video files separately:

```bash
python -m src.transit.video_preprocessor
```

This will:
1. Find all video files (MP4, AVI, MOV, MKV, etc.) without transcripts
2. Extract audio to MP3 format using FFmpeg
3. Handle large files (>490MB) appropriately
4. Keep the same filename for the extracted audio

### Manual Processing

To process an existing JSON transcript:

```bash
python -m src.transit.processor_aai
```

### File Organization

To organize existing loose files into folders:

```bash
# Organize all audio files and their related files
python -m src.transit.organize_files

# Organize specific file
python -m src.transit.organize_files "meeting_recording.mp3"

# List current file structure
python -m src.transit.organize_files --list
```

### Regenerate Screenplays

To regenerate screenplays with the new natural format for existing transcripts:

```bash
# Interactive processing with speaker renaming
python -m src.transit.processor_aai "transcript.json"

# Or use the test script to preview the format
python test_natural_format.py "transcript.json"
```

## File Naming Convention

For input file `meeting_recording.mp3`, the pipeline creates:

- `meeting_recording.json` - Main transcript with speaker data
- `meeting_recording new_transcript_aai.json` - Processed transcript (with speaker renames)
- `meeting_recording subtitle_aai.srt` - SRT subtitle file  
- `meeting_recording screenplay_aai.md` - **Natural speaker-turn screenplay format**

This naming matches the pattern used throughout the workspace, with the original audio filename prepended to all generated files.

### File Organization Structure

After processing, all files are organized into a folder named after the audio file:

```
meeting_recording/
├── meeting_recording.mp3                    # Original audio
├── meeting_recording.json                   # Main transcript  
├── meeting_recording new_transcript_aai.json # Processed transcript
├── meeting_recording subtitle_aai.srt       # SRT subtitles
└── meeting_recording screenplay_aai.md      # Natural speaker-turn screenplay
```

This makes it easy to find all related files for a specific recording and keeps the workspace organized.

## Screenplay Format

### 📄 Natural Speaker-Turn Screenplay (`screenplay_aai.md`)
- **Purpose**: Natural conversation flow with easy navigation
- **Segments**: Break only on speaker changes or sentence boundaries (45s+ monologues)
- **Best for**: Reading, analysis, quote finding, editing reference
- **Features**: 
  - Clean speaker-turn format without numbered segments
  - Natural conversation rhythm preserved
  - Timestamps at speaker changes for navigation
  - Long monologues broken at sentence boundaries
- **Example**: 
  ```markdown
  SPEAKER_A (00:01:23):
  Hello everyone, welcome to today's meeting. I hope you're all doing well.

  SPEAKER_B (00:01:30):
  Thank you for having me.
  ```

## Output Formats

### JSON Structure (AssemblyAI format)
```json
{
  "id": "transcript_id",
  "text": "Full transcript text...",
  "words": [
    {
      "text": "Hello",
      "start": 1000,
      "end": 1500,
      "confidence": 0.99,
      "speaker": "A"
    }
  ],
  "status": "completed",
  "language_code": "en"
}
```

### SRT Format
```
1
00:00:01,000 --> 00:00:05,500
[SPEAKER_A]
Hello everyone, welcome to the meeting.

2
00:00:06,000 --> 00:00:10,200
[SPEAKER_B]
Thank you for having me.
```

### Markdown Format
```markdown
SPEAKER_A (00:00:01):
Hello everyone, welcome to the meeting.

SPEAKER_B (00:00:06):  
Thank you for having me.
```

## Configuration

### Speaker Segmentation
The pipeline creates natural speaker-turn segments based on:
- Speaker changes (primary segmentation)  
- Sentence boundaries for monologues > 45 seconds
- Natural conversation flow preservation

**Note**: SRT subtitles still use fine segmentation (2s gaps, 15 words) for optimal subtitle display.

### AssemblyAI Settings
Default transcription configuration:
- Speaker diarization enabled
- Best accuracy model
- Automatic language detection
- Text formatting and punctuation

## Error Handling

- **Missing API Key**: Script will prompt for input if not set in environment
- **Network Issues**: Graceful error handling with clear messages
- **File Conflicts**: Skips existing files to prevent overwriting
- **Transcription Errors**: Reports AssemblyAI API errors clearly

## Tips

1. **Batch Processing**: Use `batch-process.py` for unattended processing
2. **Speaker Names**: Use `transcribe-pipeline.py` for better speaker identification
3. **File Organization**: Keep audio files organized by project/date
4. **API Costs**: Monitor usage as AssemblyAI charges per audio minute

## What Next? Using Your Transcripts

After transcription is complete, here are productive ways to use your transcript files:

### 1. 🏷️ Relabel Speakers with Proper Names

If you haven't already during processing, add real names to your speakers:

```bash
python -m src.transit.label_speakers
```

This replaces generic labels (Speaker A, B, C) with actual names (John, Sarah, etc.).

### 2. ✏️ Review and Correct the Screenplay

Open the `screenplay_aai.md` file and check for accuracy, especially:

- **Names of people** - AI often mishears names
  - Example: "Quentin" → "Kanta"
  - Example: "Dorothea" → "Dorothy"
- **Company names** and technical terms
- **Acronyms** and specialized vocabulary

The screenplay format makes it easy to scan and correct these errors.

### 3. 💬 Chat with Your Transcript

Copy the screenplay into your favorite AI assistant:
- **ChatGPT** - Summarize, extract action items, analyze themes
- **Claude** - Deep analysis, rewrite in different styles
- **Gemini** - Research mentioned topics, fact-check claims

**Pro tip**: Start with a structured prompt like:
```
Based on this meeting transcript, please provide:
1. Executive summary (3-5 sentences)
2. Key decisions made
3. Action items with owners
4. Open questions requiring follow-up
```

### 4. 📋 Generate Structured Summaries

Use templates to create consistent meeting documentation:
- [Meeting Summary Template](https://gist.github.com/arnevoelker/cfa835eac23d634de544712108e04e24)
- Project updates
- Interview insights
- Decision logs

### 5. 🎬 Enhance Your Videos

Use the SRT subtitle files to:
- Add captions to your video edits
- Upload accurate subtitles to YouTube
- Create accessible content for all viewers
- Generate closed captions for presentations

### 6. 🔍 Search and Reference

The JSON format preserves timestamps, making it easy to:
- Find exact moments in recordings
- Create highlight reels
- Build searchable archives
- Extract quotes with precise timing

## Example Transcript

The `workbench/output/EXAMPLE - AI Ethics Podcast/` folder contains a complete example showing all output formats. This transcript is from [The AI Impact Podcast](https://youtu.be/s5MMV0EbGoE), featuring Quentin Gallea's interview with Dr. Dorothea Baur on AI ethics and corporate responsibility.

Explore this example to see:
- How speaker labels appear in the transcript
- The natural flow of the screenplay format
- Properly formatted SRT subtitles
- Complete JSON structure with timestamps

## Troubleshooting

**No media files found**: Ensure you're in the correct directory
**API key errors**: Check your AssemblyAI account and key validity  
**Empty transcripts**: Verify audio file quality and format
**Processing slow**: Large files take time; AssemblyAI processes in real-time
