from parser import xml_parser
from environment_gen import environment_generator
from visualizer import visualize
import os
from dotenv import load_dotenv

# load_dotenv()
# home_path = os.getenv("DESKTOP_PATH")

house_data = environment_generator(xml_parser("huric/it/4168.hrc"))
visualize(house_data)
