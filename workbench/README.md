# Transit Workbench

Welcome to your transcription workspace! This is where you process your media files.

## 📁 Directory Structure

```
workbench/
├── input/                          # 📥 Place your media files here
└── output/                         # 📤 Processed files appear here
    └── EXAMPLE - AI Ethics Podcast/  # 📚 Example output to see the format
```

## 🚀 Quick Start

1. **Add your media files** to the `input/` folder
   - Supported formats: MP3, WAV, M4A, MP4, MOV, MKV, and more
   - No size limits (large files are preprocessed automatically)

2. **Run the processing script** from the project root:
   ```bash
   python -m src.transit.batch_process
   ```

3. **Find your results** in the `output/` folder
   - Each media file gets its own folder with all outputs
   - Includes transcript, subtitles, and screenplay formats

## 📂 File Organization

After processing `input/interview.mp4`, you'll find:

```
output/
└── interview/
    ├── interview.mp3                    # Extracted audio (if from video)
    ├── interview.json                   # Full transcript with speaker labels
    ├── interview new_transcript_aai.json # Processed transcript
    ├── interview subtitle_aai.srt       # Subtitle file for video editors
    └── interview screenplay_aai.md      # Natural reading format
```

## 💡 Tips

- **Batch Processing**: Add multiple files at once - they'll all be processed
- **Video Files**: Automatically converted to audio before transcription
- **Large Files**: Files over 490MB are handled automatically
- **Privacy**: Your files stay local - nothing is stored online

## 🧪 Example Output

Check out the `output/EXAMPLE - AI Ethics Podcast/` folder to see what your processed files will look like:

- **The AI impact on Ethics.mp3** - Original audio file
- **The AI impact on Ethics.json** - Full transcript with timestamps
- **The AI impact on Ethics screenplay_aai.md** - Natural reading format
- **The AI impact on Ethics subtitle_aai.srt** - Subtitle file for videos

This example is from [The AI Impact Podcast](https://youtu.be/s5MMV0EbGoE) featuring Dr. Dorothea Baur discussing AI ethics.

## ⚠️ Note

The `input/` and `output/` folders are ignored by Git to protect your privacy. Your media files and transcripts will never be committed to the repository.