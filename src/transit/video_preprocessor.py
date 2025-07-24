#!/usr/bin/env python3
"""
Video Preprocessor for AssemblyAI Workbench
Handles large video files by extracting audio before transcription
"""

import os
import glob
import subprocess
import time
from pathlib import Path

# Maximum file size for AssemblyAI (490 MB)
MAX_FILE_SIZE_MB = 490
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Supported video formats
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']

def get_file_size_mb(filepath):
    """Get file size in MB"""
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024 * 1024)

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def extract_audio(input_file, output_file):
    """Extract audio from video file using ffmpeg"""
    try:
        print(f"🎬 Extracting audio from: {input_file}")
        start_time = time.time()
        
        # Build ffmpeg command
        # -i: input file
        # -vn: no video
        # -acodec: audio codec (mp3)
        # -ab: audio bitrate (192k for good quality)
        # -ar: audio sample rate (44100 Hz)
        # -y: overwrite output file
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-vn',  # No video
            '-acodec', 'mp3',
            '-ab', '192k',
            '-ar', '44100',
            '-y',  # Overwrite if exists
            output_file
        ]
        
        # Run ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
        
        elapsed = time.time() - start_time
        output_size = get_file_size_mb(output_file)
        
        print(f"✅ Audio extracted in {elapsed:.1f}s")
        print(f"📄 Output: {output_file} ({output_size:.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error extracting audio: {str(e)}")
        return False

def find_unprocessed_media_files():
    """Find all media files that need processing"""
    unprocessed = []
    
    # Check if we're in workbench mode
    current_dir = os.getcwd()
    in_workbench = 'workbench/input' in current_dir or current_dir.endswith('input')
    
    # Find all video and audio files
    all_extensions = VIDEO_EXTENSIONS + AUDIO_EXTENSIONS
    media_files = []
    
    for ext in all_extensions:
        media_files.extend(glob.glob(f"*{ext}"))
        media_files.extend(glob.glob(f"*{ext.upper()}"))
    
    print(f"   Found {len(media_files)} media files in directory")
    
    for media_file in media_files:
        base_name = Path(media_file).stem
        print(f"   Checking: {media_file}")
        
        # Check if already processed (has corresponding JSON)
        if in_workbench:
            # In workbench mode, check output directory
            output_dir = current_dir.replace('/input', '/output')
            json_file = os.path.join(output_dir, base_name, f"{base_name}.json")
            print(f"      Looking for JSON at: {json_file}")
        else:
            # Normal mode - check current directory
            json_file = f"{base_name}.json"
            
        if os.path.exists(json_file):
            print(f"      Skipping - already processed (found {json_file})")
            continue
        
        # Check if it's already in a folder
        dirname = os.path.dirname(media_file)
        if dirname and dirname != '.':
            print(f"      Skipping - file is in subdirectory: {dirname}")
            continue
        
        # Get file info
        file_size_mb = get_file_size_mb(media_file)
        file_ext = Path(media_file).suffix.lower()
        
        file_info = {
            'path': media_file,
            'size_mb': file_size_mb,
            'extension': file_ext,
            'is_video': file_ext in VIDEO_EXTENSIONS,
            'needs_extraction': False
        }
        
        # Determine if extraction is needed
        if file_ext in VIDEO_EXTENSIONS:
            file_info['needs_extraction'] = True
        elif file_size_mb > MAX_FILE_SIZE_MB:
            file_info['needs_extraction'] = True
        
        unprocessed.append(file_info)
    
    return unprocessed

def preprocess_media_files():
    """Main preprocessing function"""
    print("🎬 Video Preprocessor for AssemblyAI Workbench")
    print("=" * 50)
    
    # Check ffmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg not found! Please install ffmpeg:")
        print("   • macOS: brew install ffmpeg")
        print("   • Ubuntu: sudo apt install ffmpeg")
        print("   • Windows: Download from https://ffmpeg.org/download.html")
        return
    
    print("✅ FFmpeg is available")
    
    # Find unprocessed files
    unprocessed = find_unprocessed_media_files()
    
    if not unprocessed:
        print("✨ No unprocessed media files found")
        return
    
    # Categorize files
    videos = [f for f in unprocessed if f['is_video']]
    large_audios = [f for f in unprocessed if not f['is_video'] and f['needs_extraction']]
    ready_audios = [f for f in unprocessed if not f['needs_extraction']]
    
    print(f"\n📊 Found {len(unprocessed)} unprocessed files:")
    print(f"   • {len(videos)} video files")
    print(f"   • {len(large_audios)} large audio files (>{MAX_FILE_SIZE_MB}MB)")
    print(f"   • {len(ready_audios)} ready audio files")
    
    # Process files that need extraction
    extracted_files = []
    
    for file_info in unprocessed:
        if not file_info['needs_extraction']:
            print(f"\n✅ {file_info['path']} ({file_info['size_mb']:.1f}MB) - Ready for transcription")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing: {file_info['path']} ({file_info['size_mb']:.1f}MB)")
        print(f"{'='*60}")
        
        # Generate output filename
        base_name = Path(file_info['path']).stem
        output_file = f"{base_name}.mp3"
        
        # Check if MP3 already exists
        if os.path.exists(output_file):
            print(f"⚠️  MP3 already exists: {output_file}")
            extracted_files.append(output_file)
            continue
        
        # Extract audio
        if extract_audio(file_info['path'], output_file):
            extracted_files.append(output_file)
            
            # Check if extracted file is small enough
            extracted_size = get_file_size_mb(output_file)
            if extracted_size > MAX_FILE_SIZE_MB:
                print(f"⚠️  Warning: Extracted audio is still large ({extracted_size:.1f}MB)")
                print(f"   Consider using a lower bitrate or splitting the file")
        else:
            print(f"❌ Failed to extract audio from {file_info['path']}")
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 PREPROCESSING SUMMARY")
    print(f"{'='*50}")
    print(f"📁 Total files found: {len(unprocessed)}")
    print(f"🎬 Videos processed: {len([f for f in videos if f['path'] in extracted_files])}")
    print(f"🎵 Large audios processed: {len([f for f in large_audios if f['path'] in extracted_files])}")
    print(f"✅ Ready for transcription: {len(ready_audios) + len(extracted_files)}")
    
    if extracted_files:
        print(f"\n💡 Next step: Run batch-process.py to transcribe the extracted audio files")

def main():
    """Entry point"""
    import sys
    
    if len(sys.argv) > 1:
        # Process specific files passed as arguments
        files_to_process = sys.argv[1:]
        print("🎬 Video Preprocessor for AssemblyAI Workbench")
        print("=" * 50)
        
        # Check ffmpeg
        if not check_ffmpeg():
            print("❌ FFmpeg not found! Please install ffmpeg:")
            print("   • macOS: brew install ffmpeg")
            print("   • Ubuntu: sudo apt install ffmpeg")
            print("   • Windows: Download from https://ffmpeg.org/download.html")
            return
        
        print("✅ FFmpeg is available")
        print(f"📁 Processing {len(files_to_process)} specified file(s)")
        
        extracted_count = 0
        for file_path in files_to_process:
            if not os.path.exists(file_path):
                print(f"\n❌ File not found: {file_path}")
                continue
            
            # Check if it's a video file
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in VIDEO_EXTENSIONS:
                print(f"\n⚠️  {file_path} is not a video file")
                continue
            
            print(f"\n{'='*60}")
            print(f"Processing: {file_path}")
            print(f"{'='*60}")
            
            # Generate output filename
            base_name = Path(file_path).stem
            output_file = f"{base_name}.mp3"
            
            # Check if MP3 already exists
            if os.path.exists(output_file):
                print(f"⚠️  MP3 already exists: {output_file}")
                continue
            
            # Extract audio
            if extract_audio(file_path, output_file):
                extracted_count += 1
                print(f"✅ Successfully extracted audio to: {output_file}")
        
        print(f"\n{'='*50}")
        print(f"📊 Processed {extracted_count} file(s)")
    else:
        # Run normal batch mode
        preprocess_media_files()

if __name__ == "__main__":
    main()