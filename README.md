# Fabric to Espanso Converter

A Python application that bridges Fabric prompts with Espanso by managing and converting prompts through a vector database.

## Features

- Store and manage Fabric prompts in a Qdrant vector database
- Convert stored prompts into Espanso YAML format for system-wide usage
- Semantic search functionality to find relevant prompts based on their meaning
- Web interface for easy interaction with the prompt database

## Prerequisites

- Python 3.11
- Qdrant vector database server (local or cloud)
- Obsidian with MeshAI plugin installed
- Windows (for PowerShell script) or Linux/WSL for direct execution

## Installation

1. Install Obsidian and the MeshAI plugin
2. In Obsidian, create the following folder structure:
   ```
   Extra/
   └── FabricPatterns/
       ├── Official/  # For downloaded Fabric patterns
       └── Own/       # For your custom additions
   ```
3. Clone this repository
4. Install dependencies using PDM:
   ```bash
   pdm install
   ```
5. Configure your Qdrant server connection in the application settings

## Usage

### Linux/WSL

Run the Streamlit application directly:
```bash
./src/search_qdrant/run_streamlit.sh
```

### Windows

Create a PowerShell script with the following content to start the application:

```powershell
# Start streamlit process and capture output
$streamlitPath = "~/Tools/pythagora-core/workspace/fabric-to-espanso/src/search_qdrant/run_streamlit.sh"
$output = wsl bash $streamlitPath

$url = "http://localhost:8501" # Default value

$pattern = "https?:\/\/localhost:[0-9]+"
if ($output -match $pattern) {
    $urls = $output | Select-String -Pattern $pattern -AllMatches
    Write-Host "Found URL in output: $($urls.Matches.Value)"
    $url = $urls.Matches.Value[0]
} else {
    Write-Host "No URL found in output. Probably because Streamlit app is already running."
}

# Wait and check for server
$attempts = 0
while ($attempts -lt 5) {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop
        Write-Host "$url"
        Start-Process "msedge.exe" "--app=$url" -WindowStyle Normal
        break
    }
    catch {
        Start-Sleep -Seconds 1
        $attempts++
        if ($attempts -eq 5) {
            Write-Warning "Failed to start Streamlit server after 5 attempts."
        }
    }
}
```

This script will:
1. Start the Streamlit server if it's not already running
2. Open the application in Microsoft Edge in app mode
3. Automatically handle server startup and connection

## Dependencies

- ipykernel >= 6.29.5
- markdown >= 3.7
- pyyaml >= 6.0.2
- qdrant-client >= 1.12.1
- fastembed >= 0.4.2
- streamlit >= 1.41.1
- pyperclip >= 1.9.0
- regex >= 2024.11.6

## License

This project is licensed under the MIT License.
