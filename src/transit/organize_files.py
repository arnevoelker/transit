import os
import glob
import shutil
from pathlib import Path

def get_base_filename(filepath):
    """Get base filename without extension"""
    return Path(filepath).stem

def get_related_files(base_name):
    """Find all files related to a base audio name"""
    patterns = [
        f"{base_name}.mp3",
        f"{base_name}.mp4", 
        f"{base_name}.json",
        f"{base_name} new_transcript_aai.json",
        f"{base_name} subtitle_aai.srt",
        f"{base_name} screenplay_aai.md",
        f"{base_name} screenplay_navigation.md"
    ]
    
    related_files = []
    for pattern in patterns:
        if os.path.exists(pattern):
            related_files.append(pattern)
    
    return related_files

def organize_files_for_audio(audio_file):
    """Organize all files related to an audio file into a folder"""
    base_name = get_base_filename(audio_file)
    folder_name = base_name
    
    # Get all related files
    related_files = get_related_files(base_name)
    
    if not related_files:
        print(f"⚠️  No related files found for {audio_file}")
        return False
    
    print(f"📁 Organizing files for: {base_name}")
    print(f"   Creating folder: {folder_name}")
    
    # Create folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"   ✅ Created folder: {folder_name}")
    else:
        print(f"   📂 Folder already exists: {folder_name}")
    
    # Move all related files
    moved_count = 0
    for file in related_files:
        destination = os.path.join(folder_name, file)
        
        if os.path.exists(destination):
            print(f"   ⚠️  File already exists in folder: {file}")
        else:
            try:
                shutil.move(file, destination)
                print(f"   📄 Moved: {file}")
                moved_count += 1
            except Exception as e:
                print(f"   ❌ Error moving {file}: {e}")
    
    print(f"   ✅ Moved {moved_count} files to {folder_name}/")
    return True

def organize_all_audio_files():
    """Organize all audio files in the current directory"""
    print("🗂️  Audio File Organization Tool")
    print("=" * 50)
    
    # Find all audio files
    audio_files = glob.glob("*.mp3") + glob.glob("*.mp4")
    
    if not audio_files:
        print("⚠️  No audio files (MP3/MP4) found in current directory")
        return
    
    print(f"📁 Found {len(audio_files)} audio files:")
    for file in audio_files:
        print(f"   • {file}")
    
    print(f"\n🔄 Starting organization...")
    
    organized_count = 0
    for audio_file in audio_files:
        print(f"\n{'-' * 40}")
        if organize_files_for_audio(audio_file):
            organized_count += 1
    
    print(f"\n{'=' * 50}")
    print(f"📊 ORGANIZATION SUMMARY")
    print(f"{'=' * 50}")
    print(f"✅ Successfully organized: {organized_count}")
    print(f"📂 Total audio files: {len(audio_files)}")

def organize_specific_file(audio_filename):
    """Organize files for a specific audio file"""
    if not os.path.exists(audio_filename):
        print(f"❌ Audio file not found: {audio_filename}")
        return False
    
    return organize_files_for_audio(audio_filename)

def list_current_files():
    """List all files in current directory grouped by audio base name"""
    print("📋 Current File Structure")
    print("=" * 40)
    
    # Find all audio files
    audio_files = glob.glob("*.mp3") + glob.glob("*.mp4")
    
    if not audio_files:
        print("⚠️  No audio files found")
        return
    
    for audio_file in audio_files:
        base_name = get_base_filename(audio_file)
        related_files = get_related_files(base_name)
        
        print(f"\n📁 {base_name}:")
        for file in related_files:
            file_size = os.path.getsize(file) / (1024 * 1024)  # MB
            print(f"   📄 {file} ({file_size:.1f} MB)")

def main():
    """Main function with interactive options"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_current_files()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python organize-files.py               # Organize all audio files")
            print("  python organize-files.py --list        # List current file structure")
            print("  python organize-files.py <filename>    # Organize specific file")
            print("  python organize-files.py --help        # Show this help")
        else:
            # Organize specific file
            organize_specific_file(sys.argv[1])
    else:
        # Organize all files
        organize_all_audio_files()

if __name__ == "__main__":
    main()