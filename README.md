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
# Start WSL process without showing window
$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.Filename = "wsl.exe"
# Use -c flag to let the command use the WSL2 Ubuntu folder system and not the Windows
$startInfo.Arguments = "bash -c ~/Tools/pythagora-core/workspace/fabric_to_espanso/src/search_qdrant/run_streamlit.sh"
$startInfo.UseShellExecute = $false
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$startInfo.CreateNoWindow = $true

# Start the process
try {
    $process = [System.Diagnostics.Process]::Start($startInfo)
    Start-Sleep -Seconds 5
    
    # Check if Streamlit is actually running
    $streamlitRunning = Test-NetConnection -ComputerName localhost -Port 8501 -WarningAction SilentlyContinue
    
    if ($streamlitRunning.TcpTestSucceeded) {
        Start-Process "msedge.exe" "--app=http://localhost:8501"
    } else {
        Write-Error "Failed to start Streamlit application"
    }
} catch {
    Write-Error "Error starting Streamlit: $_"
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
