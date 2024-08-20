from web_ui.Main_Ui import main
import subprocess
if __name__ == '__main__':
    print("[SERVER INFO] Launching Ollama server...")
    subprocess.Popen('ollama serve', shell=True)
    print("[SERVER INFO] Ollama server is running.")
    print("[INFO] Launching the main UI...")
    main()