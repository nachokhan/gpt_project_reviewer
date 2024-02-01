import os
import json
import logging
import shutil
import copy

from datetime import datetime

from tokens import chat_key, github_token

from directory_structure.directory_structure import DirectoryStructureGenerator
from chatgptcall.ChatGPTCalls import ChatGPTCalls

improvement2 = """Act as a software architect who has to review a project based on its files and folder's structure.  Provide specific, detailed, and comprehensive improvements in a JSON array format, as follows:[{"category": "(e.g. Folder Structure)","task": "(task to be carried out, specify each case with detail and concrete examples)"},...]Keep category names under 4 words. Do not use triple backticks or markdown syntax. Ensure the file is not truncated."""
improvement = """You are a software architect tasked with improving a project based on its file structure. Analyze the structure, files, and folders, taking into account names, languages (idiom), etc. Provide specific, detailed, and comprehensive improvements in a JSON array format, as follows:[{"category": "(e.g. Folder Structure)","task": "(task to be carried out, specify each case with detail and concrete examples)"},...]Keep category names under 4 words. Do not use triple backticks or markdown syntax."""
improvement3 = """You are a software architect who has to review a project bases on it file's structure. Consider the best folder structure once you know the kind of project. Give me 7 super detailed improvements that will considerably improve my project. Do it as if I am a computer program that need all specified. Do it in a JSON array format, as follows:[{"category": "(e.g. Folder Structure)","task": "(task to be carried out, specify each case with detail and concrete examples)"},...]Keep category names under 4 words. Do not use triple backticks or markdown syntax. Ensure the file is not truncated"""
improvement4 = """You are a software architect who has to review a project bases on it file's structure. Consider the best folder structure once you know the 
kind of project. Describe 5 problems that the project has based on its files and folders structure. Mention only critical problems. Only those who you see are there. And give the concrete steps to solve them. Do it as json file with no markup language."""
script = """Given the tasks, create a shell script to execute the modifications outlined in the tasks. Prompt the user for confirmation (Y/N) before performing each change. Provide the complete script content directly, without using triple backticks or markdown syntax. Save the content in a file."""

gpt_config = {
    "improvement" : {
        "prompt" : improvement3,
        "temperature": 0.2,
        "top_p": 0.2,
        "model": ChatGPTCalls.ModelName.GPT_4
    },
    "script" : {
        "prompt" : script,
        "temperature": 0.2,
        "top_p": 0.2,
        "model": ChatGPTCalls.ModelName.GPT_4
    }
}


def remove_unnecesary_chars(content):
    clean_content = content
    clean_content = clean_content.replace(": null", "")
    clean_content = clean_content.replace(":null", "")
    clean_content = clean_content.replace(" ", "")
    clean_content = clean_content.replace("\n", "")
    clean_content = clean_content.replace(",", "")
    return clean_content


def save_json(file, structure):
    with open(file, "w") as f:
        json.dump(structure, f, indent=4, ensure_ascii=False)


def save_file(file, text):
    with open(file, "w") as f:
        f.write(text)


def append_to_file(file, text):
    with open(file, "a") as f:
        f.write(text)


def create_html_answer(project_name_folder):
    # define the names of the relevant folders and files
    templates_folder = "templates"
    html_folder = os.path.join(project_name_folder, "html")
    answer_json_file = os.path.join(project_name_folder, "answer.json")
    script_file = "script.js"
    org_improvement_script_file =  os.path.join(project_name_folder, "make_improvements.sh")
    dst_improvement_script_file =  os.path.join(html_folder, "make_improvements.sh")

    # create the new "html" folder inside the project folder
    os.makedirs(html_folder)

    # copy the contents of the "templates" folder to the new "html" folder
    for item in os.listdir(templates_folder):
        src_path = os.path.join(templates_folder, item)
        dst_path = os.path.join(html_folder, item)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)

    # copy the improvement script file into html folder.
    if os.path.exists(org_improvement_script_file):
        shutil.copy(org_improvement_script_file, dst_improvement_script_file)

    # load the contents of the "answer.json" file
    with open(answer_json_file) as f:
        answer = json.load(f)

    # read the contents of the "script.js" file
    with open(os.path.join(html_folder, script_file)) as f:
        script_content = f.read()

    # replace "{put_answer_here}" with the contents of the "answer" variable
    script_content = script_content.replace("{put_answer_here}", json.dumps(answer))

    # write the updated JS to a new file in the "html" folder
    with open(os.path.join(html_folder, script_file), "w") as f:
        f.write(script_content)


def send_chat_request(prompt, temperature, top_p, output_file, model, info_text):
    logging.info(info_text)
    answer = gpt.send_chat_request(
        prompt=prompt,
        temperature=temperature,
        top_p=top_p,
        model=model,
    )
    save_file(output_file, answer)
    logging.info(f"{output_file} saved")



if __name__ == "__main__":
    os.system('clear')

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    repo_list = [
        # "https://github.com/NicolasLefeld/brincalto-S.A-Back.git",
        # "https://github.com/NicolasLefeld/CodeChallenge-Lolocar",
        # "https://github.com/nachokhan/resto_reservas_webapp.git",
        "https://github.com/nachokhan/pstruc",
        # "https://github.com/nachokhan/turnero.git",
        # "https://github.com/DLR-SC/tasking-framework.git"
        # "https://github.com/sammchardy/python-binance.git",
        # "https://github.com/h5bp/html5-boilerplate.git",
    ]

    try:

        structre_analizer = DirectoryStructureGenerator(
            token=github_token,
        )

        gpt = ChatGPTCalls(
            chat_key,
        )

        base_projects_folder = "projects"

        for repo_url in repo_list:

            project_name = repo_url.split("/")[-1].replace(".git", "")
            logging.info(f"# Project: {project_name}")

            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name_folder = f"{base_projects_folder}/{current_date}_{project_name}"
            os.makedirs(project_name_folder)

            json_file = os.path.join(project_name_folder, f"structure.json")
            min_json_file = os.path.join(project_name_folder, f"structure_min.json")
            txt_file = os.path.join(project_name_folder, f"answer.json")
            html_file = os.path.join(project_name_folder, f"answer.html")
            script_file = os.path.join(project_name_folder, "make_improvements.sh")
            gpt_config_file = os.path.join(project_name_folder, "gtp_config.json")


            ##### GITHUB REPO ANALYSIS #####

            logging.info(f"Processing repo at {repo_url}")
            project_structure = structre_analizer.process_repo(repo_url)
            logging.info("Processing complete")

            save_json(json_file, project_structure)
            logging.info(f"Project structure saved in JSON format to {json_file}")

            json_as_text = json.dumps(project_structure)

            clean_content = remove_unnecesary_chars(json_as_text)
            save_file(min_json_file, clean_content)
            logging.info(f"Project structure saved in minimized JSON format to {min_json_file}")

            gpt_config_serializabel = copy.deepcopy(gpt_config)
            gpt_config_serializabel["improvement"]["model"] = gpt_config["improvement"]["model"].value
            gpt_config_serializabel["script"]["model"] = gpt_config["script"]["model"].value
            save_json(gpt_config_file, gpt_config_serializabel)


            #### LALALA ADDED #####
            lalala = structre_analizer.convert_to_string_list(project_structure)
            lala = str(lalala)
            lala = lala.replace("'", "")
            lala = lala.replace(" ", "")
            lala = lala.replace(",/", ",")
            lala = lala.replace("[/", "")
            lala = lala.replace("]", "")
            clean_content = lala


            #####CHAT GPT IMPROVEMENT #####
            logging.info(f"Calling ChatGPT for improvement...")
            improvement_prompt = f"{gpt_config['improvement']['prompt']}\n{clean_content}"
            improvement_answer = gpt.send_chat_request(
                prompt=improvement_prompt,
                temperature=gpt_config['improvement']['temperature'],
                top_p=gpt_config['improvement']['top_p'],
                model=gpt_config['improvement']['model'],
            )
            save_file(txt_file, improvement_answer)
            logging.info(f"Improvement answer saved to {txt_file}")

          
            # script_prompt = f"{gpt_config['script']['prompt']}\n{improvement_answer}"
            # script_answer = gpt.send_chat_request(
            #     prompt=script_prompt,
            #     temperature=gpt_config['improvement']['temperature'],
            #     top_p=gpt_config['improvement']['top_p'],
            #     model=gpt_config['improvement']['model'],
            # )
            # save_file(script_file, script_answer)
            # logging.info(f"Script saved to {script_file}")

            create_html_answer(project_name_folder)

    except Exception as e:
        print(f"Exception: {e}")
