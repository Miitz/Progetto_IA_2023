from parser import xml_parser
from environment_gen import environment_generator
from visualizer import visualize

data, room = xml_parser("huric/it/4169.hrc")
house_data = environment_generator(data, room)
visualize(house_data)
