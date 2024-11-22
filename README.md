# Fabric to Espanso

This project converts markdown files to YAML format for use with Espanso.

## Configuration

You can customize the folder locations by setting the following environment variables:

- `FABRIC_MARKDOWN_FOLDER`: Location of the markdown files
- `FABRIC_QDRANT_DB_LOCATION`: Location of the Qdrant database
- `FABRIC_YAML_OUTPUT_FOLDER`: Location for the output YAML files
- `FABRIC_PURPOSES_FILE`: Location of the Fabric_purposes.md file

If not set, default locations within the project root will be used.

To set these variables, you can:

1. Create a `.env` file in the project root (use `.env.example` as a template)
2. Set them in your shell before running the application

## Usage

(Add usage instructions here)