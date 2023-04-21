import os
import tempfile
import shutil
import json
import base64
import logging
from git import Repo

logging.basicConfig(level=logging.INFO)

class DirectoryStructureGenerator:
    def __init__(self, include_full_path=False, include_file_content=False):
        self.include_full_path = include_full_path
        self.include_file_content = include_file_content
        self.archivo_structignore_default = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".structignore")

    def clone_git_repository(self, url, token=None):
        if token:
            url = url.replace("https://", f"https://x-access-token:{token}@")
        temp_directory = tempfile.mkdtemp()
        Repo.clone_from(url, temp_directory)
        return temp_directory

    def is_url(self, input_string):
        if input_string.startswith("http://") or input_string.startswith("https://"):
            return True
        return False

    def read_structignore_file(self, structignore_path):
        with open(structignore_path, "r") as f:
            rules = f.readlines()
        rules = [rule.strip() for rule in rules if rule.strip()]
        return rules

    def save_structure_to_json(self, structure, output_file):
        with open(output_file, "w") as f:
            json.dump(structure, f, ensure_ascii=False, indent=4)

    def list_directory_recursively(self, directory_path, structignore_path=None):
        if structignore_path:
            ignore_rules = self.read_structignore_file(structignore_path)
        else:
            ignore_rules = []

        def _build_structure(path):
            structure = {}
            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                if any(fnmatch.fnmatch(item_path, rule) for rule in ignore_rules):
                    continue

                if os.path.isdir(item_path):
                    key = item if self.include_full_path else os.path.basename(item_path)
                    structure[key] = _build_structure(item_path)
                elif os.path.isfile(item_path):
                    key = item_path if self.include_full_path else item
                    if self.include_file_content:
                        with open(item_path, "rb") as f:
                            content = f.read()
                            structure[key] = base64.b64encode(content).decode("utf-8")
                    else:
                        structure[key] = "file"
            return structure

        return _build_structure(directory_path)

    def generate_json_structures_for_repositories(self, repositories, token=None):
        for url_repository in repositories:
            analysis_directory = self.clone_git_repository(url_repository, token)

            repository_name = url_repository.split("/")[-1].replace(".git", "")
            output_file = f"{repository_name}.json"

            structignore_path = os.path.join(analysis_directory, ".structignore")
            structignore = structignore_path if os.path.exists(structignore_path) else self.archivo_structignore_default

            directory_structure = self.list_directory_recursively(analysis_directory, structignore)

            self.save_structure_to_json(directory_structure, output_file)

            shutil.rmtree(analysis_directory)

            logging.info(f"The structure of the repository '{url_repository}' has been saved in '{output_file}'.")
