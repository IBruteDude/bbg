#!/usr/bin/env python
import os
import shutil as su
import json

from engine.postman import generate_postman_collection, generate_postman_test_collection
from engine.routes import generate_routes
from engine.structure import create_directories, mirror_existing_files
from engine.swagger import generate_yaml_files
from engine.translation import generate_translations
from engine.models import generate_models
from engine import OUTPUT_DIR
from config.specification import endpoints
from config.structure import project_structure


# Main function to generate the project
def generate_flask_project(project_name):
    # Create project directories and files
    base_path = os.path.join(os.getcwd(), OUTPUT_DIR, project_name)

    if os.path.exists(base_path):
        su.rmtree(base_path)

    os.makedirs(base_path, exist_ok=True)

    create_directories(base_path, project_structure)

    # create_test_directories(os.path.join(base_path, "tests"), "", project_structure)

    # Generate dynamic code for routes
    generate_routes(base_path, endpoints)

    relational_models = json.load(
        open(os.path.join("config", project_name + ".erdplus"), "+br")
    )

    generate_models(project_name, relational_models)

    generate_yaml_files(base_path, endpoints)

    mirror_existing_files(project_name)

    generate_translations(project_name)

    os.system(f"black -q {os.path.join(OUTPUT_DIR, project_name)}")

    generate_postman_collection(project_name, endpoints)

    tests = json.load(open(os.path.join("config", project_name + "_tests.json"), "+br"))

    generate_postman_test_collection(project_name, tests)

    # su.copytree(base_path, os.path.dirname(os.getcwd()), dirs_exist_ok=True)


# Run the generator
generate_flask_project("QuizQuickie")


import click as ck
