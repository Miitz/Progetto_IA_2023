import os
import subprocess
import argparse


def process_folder(folder_path, script_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".hrc"):
            file_path = os.path.join(folder_path, filename)
            command = ["python3", script_path, file_path, "--visualize"]
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Errore durante l'esecuzione del comando per {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Percorso File Cartella")
    parser.add_argument("folder_path", help="Il percorso della cartella contenente i file hrc da analizzare")
    args = parser.parse_args()

    script_path = "runner.py"  # Percorso dello script
    process_folder(args.folder_path, script_path)


if __name__ == "__main__":
    main()
