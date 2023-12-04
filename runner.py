from parser import xml_parser
from environment_gen import environment_generator
from visualizer import visualize

# house_data = environment_generator(xml_parser("huric/it/4266.hrc"))
house_data = environment_generator(xml_parser("huric/it/4169.hrc"))
visualize(house_data)
