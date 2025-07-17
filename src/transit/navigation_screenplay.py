#!/usr/bin/env python3
"""
DEPRECATED: Navigation Screenplay Generator

This script has been deprecated in favor of the natural speaker-turn format.
All markdown output now uses natural speaker-turn formatting instead of 
fixed-duration navigation segments.

Use the following instead:
- processor-aai.py for manual processing with speaker renaming
- batch-process.py for automated processing 
- transcribe-pipeline.py for interactive processing

These scripts now generate natural speaker-turn screenplays that are both
readable and navigable through speaker-change timestamps.
"""

import sys

def main():
    print("⚠️  DEPRECATED: Navigation screenplay format has been removed.")
    print("📄 All screenplay files now use natural speaker-turn format.")
    print("")
    print("Use these scripts instead:")
    print("  • processor-aai.py - Manual processing with speaker renaming")
    print("  • batch-process.py - Automated batch processing")  
    print("  • transcribe-pipeline.py - Interactive processing")
    print("")
    print("The new format provides natural conversation flow while maintaining")
    print("easy navigation through speaker-change timestamps.")

if __name__ == "__main__":
    main()