from pathlib import Path
from shutil import copy2, rmtree
from fastcore.utils import L
import re

from src.fabrics_processor.config import config

def sentence2snake(name: str) -> str:
    """Convert any string to snake_case, replacing non-alphanumeric with underscore"""
    s1 = name.lower()
    s2 = re.sub(r'\W', r'_', s1)
    return re.sub(r'_+', r'_', s2)

def round_timestamp(ts: float) -> int:
    """Round timestamp to handle filesystem differences"""
    return int(str(ts).split('.')[0][:-4])

def get_md_files_obsidian(path: Path) -> dict:
    """Get files from obsidian vault: stem -> (path, timestamp, size)"""
    # Rename files to snake_case and add identifier to distinguish own prompts from others
    return {sentence2snake(p.stem)+"-"+p.parent.name.lower(): (p, p.stat().st_mtime, p.stat().st_size) 
            for p in Path(path).glob('**/*.md')}

def get_md_files_fabricsfolder(path: Path) -> dict:
    """Get files from target structure: dir_name -> (system.md_path, timestamp, size)"""
    target_subdirs = [x for x in path.iterdir() if x.is_dir()]
    return {x.stem: (x/'system.md', (x/'system.md').stat().st_mtime, (x/'system.md').stat().st_size)
            for x in target_subdirs 
            if (x/'system.md').exists()}

def get_modified_files(source_files: dict, target_files: dict) -> list:
    """Compare timestamps between source and target files, returns dictionary of
    entries needing updates. The dictionary has the filename as key and the following
    values:
        path, timestamp, size"""
    existing_files = L(k for k in source_files.keys() if k in target_files)
    # removed checking for timestamp. Because you don't want false positives because of file system differences
    # or daylight savings. But you also want to be able to update files that have almost the same timestamp
    # when you change the file.
    # different_timestamps = L(k for k in existing_files 
    #                        if round_timestamp(source_files[k][1]) > round_timestamp(target_files[k][1]))
    # return L(source_files[k][0] for k in different_timestamps 
    #         if source_files[k][2] != target_files[k][2])
    return L({k: source_files[k]} for k in existing_files if source_files[k][2] != target_files[k][2])

def get_new_files(source_files: dict, target_files: dict) -> list:
    """Return list of dictionaries containing with the key as filename and these values:
        path, timestamp, size"""
    return L({k: source_files[k]} for k in source_files.keys() if k not in target_files)

def process_file(source: dict, target_dir: Path) -> None:
    """
    Process a single file: create directory, copy as system.md, create user.md
    
    Args:
        source: Dict of source file: filename:(path, timestamp, size)
        target_dir: Base target directory (e.g. 'md_target')
    """
    filename = next(iter(source))
    filepath = next(iter(source.values()))[0]
    subdir = target_dir/filename
    subdir.mkdir(mode=0o755, exist_ok=True)
    copy2(filepath, subdir/'system.md')
    (subdir/'user.md').touch()

def sync_folders(source_dir: Path, target_dir: Path) -> None:
    """
    Main function to synchronize folders
    
    Args:
        source_dir: Path to source directory (obsidian vault)
        target_dir: Path to target directory (fabrics folder)
    """
    source_files = get_md_files_obsidian(Path(source_dir))
    target_files = get_md_files_fabricsfolder(Path(target_dir))
    
    # Get all files that need processing
    files_to_process = L(get_new_files(source_files, target_files) + 
                        get_modified_files(source_files, target_files))
    
    # Process each file
    for i in files_to_process:
        process_file(i, target_dir)
    
    # Get all files that need deleting
    files_to_delete = L(k for k in target_files.keys() if k not in source_files and "-" in k)

    # Delete each directory and its contents
    for file_name in files_to_delete:
        rmtree(target_dir/file_name)