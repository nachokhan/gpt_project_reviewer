import os
import re
import shutil
import tempfile
from git import Repo
import logging
from pstruc import get_project_structure
from pstruc.file_tools import get_all_ignore_patterns
import directory_structure.extension_manger as extension_manger


class DirectoryStructureGenerator():
    def __init__(self, token=None) -> None:
        self.token = token

    def _is_url(self, text):
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return bool(url_pattern.match(text))

    def _clone_git_repo(self, url):
        if self.token:
            url_parts = url.split("://")
            url = f"{url_parts[0]}://{self.token}@{url_parts[1]}"

        temp_dir = tempfile.mkdtemp()
        Repo.clone_from(url, temp_dir)

        return temp_dir

    def process_repo(self, repo_url):
        # Clonar el repositorio
        repo_tmp_folder = self._clone_git_repo(repo_url)

        try:
            # Obtener el nombre del repositorio
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            output_file = f"{repo_name}.json"

            ignore_files = []
            extra_patterns = [".git"]
            to_add_content = extension_manger.get_extensions_list(["python", "web", "c"])


            # Comprobar si el repositorio contiene un archivo .structignore
            # y en ese caso agregarlo a la lista
            tmp_ignore_file = os.path.join(repo_tmp_folder, ".structignore")
            if os.path.exists(tmp_ignore_file):
                ignore_files.append(tmp_ignore_file)
            else:
                # Sino, usar el archivo .structignore predeterminado
                ignore_files.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".structignore"))

            # Comprobar si el repositorio contiene un archivo .gitignore
            # y en ese caso agregarlo a la lista
            tmp_ignore_file = os.path.join(repo_tmp_folder, ".gitignore")
            if os.path.exists(tmp_ignore_file):
                ignore_files.append(tmp_ignore_file)

            # Obtener una lista de patrones de archivos a ignorar
            ignore_patterns = get_all_ignore_patterns(
                repo_tmp_folder,
                ignore_files,
                extra_patterns
            )

            # Obtener la estructura del directorio
            folder_struct = get_project_structure(
                repo_tmp_folder,
                output_format="json",
                to_ignore=ignore_patterns,
                to_add_content=to_add_content
            )

            # Guardar la estructura en un archivo JSON
            # save_structure_to_file(
            #     output_file,
            #     folder_struct
            # )

            logging.info(f"La estructura del repositorio '{repo_url}' ha sido guardada en '{output_file}'.")

        except Exception as e:
            logging.error(f"Error al procesar el repositorio '{repo_url}': {e}")

        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(repo_tmp_folder)

        return folder_struct, output_file

    def convert_to_string_list(self, data, prefix=''):
        file_paths = []
        for key, value in data.items():
            if value is None:
                file_paths.append(f"{prefix}/{key}")
            else:
                file_paths.extend(self.convert_to_string_list(value, f"{prefix}/{key}"))
        return file_paths
