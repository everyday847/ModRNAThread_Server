import os

file_path = os.path.realpath(__file__)
spl = file_path.split("/")
BASE_DIR = "/".join(spl[:-1])
DATA_DIR = BASE_DIR + "/data/"
TEMPLATES_DIR = BASE_DIR + "/templates/"
UNITTEST_DIR = BASE_DIR + "/unittests/"

