import os
import json
import re
import shutil
import tempfile
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
import base64
from git import Repo
import logging


class DirectoryStructureGenerator():

    ACCEPTED_BINARY_FILES = ["ico", "jpg", "jpeg", "png", "gif", "svc"]

    def __init__(self, show_full_path, add_file_content, token=None) -> None:
        self.show_full_path = show_full_path
        self.add_file_content = add_file_content
        self.token = token

    def _is_url(self, text):
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return bool(url_pattern.match(text))
    

    def _read_structignore_file(self, path, structignore_file):
        structignore_path = os.path.abspath(os.path.join(path, ".structignore"))
        if os.path.exists(structignore_path):
            with open(structignore_path, "r") as f:
                structignore = f.read().splitlines()
        else:
            with open(structignore_file, "r") as f:
                structignore = f.read().splitlines()

        return PathSpec.from_lines(GitWildMatchPattern, structignore)
    

    def _read_file_content(self, file_name):
        try:
            lala = file_name.split(".")[-1] in self.ACCEPTED_BINARY_FILES
            if file_name.endswith('.ico') or file_name.endswith('.jpg') or file_name.endswith('.png') or file_name.endswith('.jpeg') or file_name.endswith('.gif'):
                with open(file_name, 'rb') as file:
                    file_content = base64.b64encode(file.read()).decode('utf-8')
            else:
                with open(file_name, 'r', encoding='utf-8') as file:
                    file_content = file.read()
        except Exception as e:
            logging.info(f"Error al guardar el contenido del archivo '{file_name}': {e}")
            file_content = "ERROR_SAVING_FILE_CONTENT"

        return file_content
    

    def _process_files_and_folders(self, path, structignore_file, structure, base_path):
        
        structignore = self._read_structignore_file(path, structignore_file)

        for root, dirs, files in os.walk(path):
            for d in dirs[:]:
                folder = os.path.join(root, d)
                directorio_rel = os.path.relpath(folder, base_path)

                if structignore.match_file(directorio_rel):
                    dirs.remove(d)
                    continue

                if self.show_full_path:
                    structure[directorio_rel] = {}
                else:
                    structure[d] = {}

                self._list_directory_recursively(folder, structignore_file, structure[d], base_path)

            for f in files:
                archivo = os.path.join(root, f)
                archivo_rel = os.path.relpath(archivo, base_path)

                if structignore.match_file(archivo_rel):
                    continue

                file_content = self._read_file_content(archivo) if self.add_file_content else None

                if self.show_full_path:
                    structure[archivo_rel] = file_content
                else:
                    structure[f] = file_content

            break
    

    def _list_directory_recursively(self, path, structignore_file, structure=None, base_path=None):
        if structure is None:
            structure = {}
        
        if base_path is None:
            base_path = path

        self._process_files_and_folders(path, structignore_file, structure, base_path)

        return structure
    

    def _save_json_structure(self, structure, output_file):
        with open(output_file, "w") as f:
            json.dump(structure, f, indent=4, ensure_ascii=False)


    def _clone_git_repo(self, url):
        if self.token:
            url_parts = url.split("://")
            url = f"{url_parts[0]}://{self.token}@{url_parts[1]}"

        temp_dir = tempfile.mkdtemp()
        Repo.clone_from(url, temp_dir)

        return temp_dir
    
    def generate_json_from_repos(self, repo_list):

        files_to_return = []

        for repo_url in repo_list:
            # Clonar el repositorio
            repo_local_tmp_folder = self._clone_git_repo(repo_url)

            try:
                # Obtener el nombre del repositorio
                repo_name = repo_url.split("/")[-1].replace(".git", "")
                output_file = f"{repo_name}.json"

                # Comprobar si el repositorio contiene un archivo .structignore
                repo_structignore_file = os.path.join(repo_local_tmp_folder, ".structignore")
                if os.path.exists(repo_structignore_file):
                    structignore_file = repo_structignore_file
                else:
                    # Usar el archivo .structignore predeterminado
                    structignore_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".structignore")

                # Obtener la estructura del directorio
                folder_struct = self._list_directory_recursively(
                    repo_local_tmp_folder,
                    structignore_file,
                )

                # Guardar la estructura en un archivo JSON
                self._save_json_structure(folder_struct, output_file)

                files_to_return.append(output_file)

                logging.info(f"La estructura del repositorio '{repo_url}' ha sido guardada en '{output_file}'.")
            
            except Exception as e:
                logging.error(f"Error al procesar el repositorio '{repo_url}': {e}")

            finally:
                # Eliminar el directorio temporal
                shutil.rmtree(repo_local_tmp_folder)
        
        return files_to_return
    

    def process_repo(self, repo_url):

        # Clonar el repositorio
        repo_local_tmp_folder = self._clone_git_repo(repo_url)

        try:
            # Comprobar si el repositorio contiene un archivo .structignore
            repo_structignore_file = os.path.join(repo_local_tmp_folder, ".structignore")
            if os.path.exists(repo_structignore_file):
                structignore_file = repo_structignore_file
            else:
                # Usar el archivo .structignore predeterminado
                structignore_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".structignore")

            # Obtener la estructura del directorio
            folder_struct = self._list_directory_recursively(
                repo_local_tmp_folder,
                structignore_file,
            )

            logging.info(f"La estructura del repositorio '{repo_url}' ha sido procesada'.")
        
        except Exception as e:
            logging.error(f"Error al procesar el repositorio '{repo_url}': {e}")

        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(repo_local_tmp_folder)
    
        return folder_struct


    def convert_to_string_list(self, data, prefix=''):
        file_paths = []
        for key, value in data.items():
            if value is None:
                file_paths.append(f"{prefix}/{key}")
            else:
                file_paths.extend(self.convert_to_string_list(value, f"{prefix}/{key}"))
        return file_paths
