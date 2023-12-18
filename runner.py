from parser import xml_parser
from environment_gen import environment_generator
from visualizer import visualize
import argparse


def main():
    parser = argparse.ArgumentParser(description="Percorso File Huric")
    parser.add_argument("file_path", help="Il percorso del file hrc da analizzare")
    parser.add_argument("--visualize", "-v", action="store_true", help="Genera immagini")
    args = parser.parse_args()

    try:
        with open(args.file_path, 'r') as file:
            data, room = xml_parser(args.file_path)
            house_data = environment_generator(data, room)
            if args.visualize:
                visualize(house_data)
    except FileNotFoundError:
        print(f"Il file non è stato trovato: {args.file_path}")
    except Exception as e:
        print(f"Si è verificato un errore: {e}")


if __name__ == "__main__":
    main()

