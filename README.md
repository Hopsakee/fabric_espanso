# Fabric_to_espanso

Fabric_to_espanso is a Python project designed to automate the conversion of markdown files to a specific YAML format. It also tracks changes in the markdown files and maintains a database using Qdrant. The project extracts specific content from the markdown files and ensures data consistency and reliability.

## Overview

Fabric_to_espanso consists of several components that work together to process markdown files, convert them to YAML, and store metadata in a Qdrant database. The architecture follows the C4 model with clearly defined contexts, containers, and deployment scenarios.

### Technologies Used

- **Python**: Main programming language.
- **Qdrant**: Vector similarity search engine for maintaining a database.
- **pandas**: Data manipulation and analysis.
- **pyyaml**: Parsing and producing YAML.
- **qdrant-client**: Python client for Qdrant.
- **markdown**: Parsing Markdown files.
- **watchdog**: Monitoring file system events.

### Project Structure

- **main.py**: Entry point for initializing the Qdrant database connection.
- **parameters.py**: Contains configuration parameters such as the location of the markdown files and the Qdrant database.
- **src/fabric_to_espanso/**: Contains core functionality including database initialization, file processing, and YAML generation.
  - **database.py**: Functions for initializing and managing the Qdrant database.
  - **database_updater.py**: Functions for updating the Qdrant database based on file changes.
  - **file_processor.py**: Functions for processing markdown files.
  - **file_change_detector.py**: Functions for detecting changes in markdown files.
  - **logger.py**: Logger configuration.
  - **markdown_parser.py**: Functions for parsing markdown files.
  - **yaml_generator.py**: Functions for generating YAML content from markdown files.
- **tests/**: Contains test files for the project.

## Features

- **Markdown to YAML Conversion**: Converts markdown files to a specific YAML format.
- **Change Tracking**: Monitors updates, deletions, and additions in markdown files.
- **Content Extraction**: Extracts specific sections from markdown files.
- **Database Management**: Uses Qdrant to store and manage file metadata and content.
- **Error Handling**: Provides robust error handling and logging.

## Getting Started

### Requirements

- Python 3.11
- Qdrant
- pandas
- pyyaml
- qdrant-client
- markdown
- watchdog

The Qdrant dabase server must be running on localhost:6333.
The easiest way is using the docker image, see https://qdrant.tech/documentation/quickstart/

### Quickstart

1. **Clone the repository**:
   ```sh
   git clone <repository_url>
   cd fabric-to-espanso
   ```

2. **Set up a virtual environment**:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure parameters**:
   Edit the `parameters.py` file to set the location of the markdown files and the Qdrant database.

5. **Initialize the Qdrant database**:
   ```sh
   python main.py
   ```

6. **Run the file processor**:
   ```sh
   python -m src.fabric_to_espanso.file_processor
   ```

### License

The project is proprietary (not open source). Copyright (c) 2024.
