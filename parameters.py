"""Checks on input data are done in config.py
These parameters must be loaded in the script using config.py"""
import os

# 
# Initialize some automated variables
#
# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Get Windows user profile path
import subprocess
windows_user = subprocess.check_output(['cmd.exe', '/c', 'echo %USERNAME%'], text=True).strip()

# 
# User parameters
#
# Location of input and output files
# TODO: make us of ~ possible in setting of path
FABRIC_PATTERNS_FOLDER="/home/jelle/.config/fabric/patterns"
OBSIDIAN_OUTPUT_FOLDER="/mnt/c/Obsidian/BrainCave/Extra/textgenerator/templates/fabric"
OBSIDIAN_INPUT_FOLDER="/mnt/c/Obsidian/BrainCave/d5 WDODelta/50-59 Programmeren en development/56 Generative AI en LLM/56.15 PromptsLibrary"

# Headings to extract from markdown files
BASE_WORDS = ['Identity', 'Purpose', 'Task', 'Goal']

# Espanso parameters
DEFAULT_TRIGGER = ";;fab"
YAML_OUTPUT_FOLDER=f"/mnt/c/Users/{windows_user}/AppData/Roaming/espanso/match"

# Qdrant database parameters
# TODO: deze paramater wordt nu niet in het script gebruikt, is nu hard coded, dit moet wel gebruikt worden
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "fabric_patterns"

# Required fields for database points
REQUIRED_FIELDS = ['filename', 'content', 'purpose', 'filesize', 'trigger']
REQUIRED_FIELDS_DEFAULTS = {
    'trigger': ';;fab',
    'filesize': 0,
    'purpose': None  # Will be set to content if missing
}

# Embedding Model parameters voor Qdrant
USE_FASTEMBED = True
EMBED_MODEL = "fast-bge-small-en" 