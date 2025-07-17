"""
Transit - Transcripts in Motion

A privacy-first, local transcription pipeline using AssemblyAI.
Transcripts are never the destination - they're always in transit to becoming something more useful.
"""

__version__ = "0.1.0"
__author__ = "Arne Völker"

# Main entry points
from .batch_process import main as batch_process
from .transcribe_pipeline import main as transcribe_pipeline
from .processor_aai import main as process_transcript
from .organize_files import main as organize_files
from .label_speakers import main as label_speakers

__all__ = [
    'batch_process',
    'transcribe_pipeline', 
    'process_transcript',
    'organize_files',
    'label_speakers'
]