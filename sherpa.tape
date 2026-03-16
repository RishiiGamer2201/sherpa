Output assets/demo.gif
Set FontSize 13
Set Width 900
Set Height 420
Set Theme "Dracula"
Set Shell "powershell"

# Activate venv first
Type "C:/Users/seast/VSCODE/sherpa/.venv/Scripts/Activate.ps1"
Enter
Sleep 3s

# Run the failing command
Type "pip install rish"
Enter
Sleep 4s

# Run sherpa
Type "sherpa"
Enter
Sleep 25s