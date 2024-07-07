import subprocess
import json
import os

def run_streamlit():
    # Activate Conda environment
    activate_script = "C:\\Users\\henry\\Anaconda3\\Scripts\\activate.bat"
    conda_activate_command = f"call {activate_script} && conda activate mistral-7b"

    # Change to the project directory
    project_directory = "C:\\Users\\henry\\OneDrive\\Documents\\Python Projects\\evaluation-ai-pro"
    os.chdir(project_directory)

    # Get the Python executable from Pipenv
    pipenv_python_command = "pipenv --py"
    python_executable = subprocess.check_output(pipenv_python_command, shell=True).decode().strip()

    # Prepare the Streamlit command using the Python executable from Pipenv
    streamlit_command = f"{python_executable} -m streamlit run main.py"

    # Combine Conda activation with Streamlit command
    full_command = f"{conda_activate_command} && {streamlit_command}"

    # Execute the command in a new command prompt
    subprocess.call(f"cmd /c \"{full_command}\"", shell=True)

if __name__ == "__main__":
    run_streamlit()
