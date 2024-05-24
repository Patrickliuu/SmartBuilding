Microsoft Lida
==============

- `Lida github <https://github.com/microsoft/lida>`_
- `Project page <https://microsoft.github.io/lida/>`_

In the FAQ, it is recommended to run Lida in a sandbox, because it 
relies on code execution. chatGPT suggested the following solution to 
sandbox:

    If you need to use Visual Studio Code (VS Code) with a GUI in a Docker container, it 
    indeed complicates things a bit, as typical Windows server images used in Docker don't 
    come with a GUI. However, there's an alternative approach that might suit your needs: 
    using VS Code's Remote Development capabilities. This allows you to run and debug code 
    inside a Docker container while still using the VS Code interface on your host machine.

    Here's a brief overview of how you can set this up:

    Use a Headless Container: You can still use a Windows Server Core or Nano Server Docker 
    image. These images are lightweight and don't include the Windows GUI, but they are 
    sufficient for running most backend services and applications.

    Install VS Code Extensions: On your host machine, install the "Dev Containers" extension 
    in VS Code. This extension allows VS Code to connect to and interact with a Docker container.

    Configure Your Project: Set up your project on your host machine and create a Dockerfile that 
    defines the environment needed to run your project. This includes the base image, any dependencies, 
    and configuration settings.

    Open Project in Container: With the Dev Containers extension, you can open your project 
    directly in the context of the container. VS Code will build the container as defined in your 
    Dockerfile and then connect to it. Your code runs inside the container, but you edit and interact 
    with it just as if it were running locally on your host machine.

    Develop and Debug: You can write, run, and debug your code as if it were running locally. The 
    difference is that the execution environment is entirely encapsulated within the Docker container.

Current status: the dockerfile works when building manually. Running the image in Dev Container extension 
does not yet work. Running Lida in the github Codespace works partly, so the UI shows up, but uploading
a cvs, respectively using one of the provided data files, does not work. I did not find the detailed error
messages.

To run Lida:
set OPENAI_API_KEY=<your key>
lida ui  --port=8080
http://localhost:8080/

use AzureAI: https://github.com/microsoft/lida/blob/main/notebooks/tutorial.ipynb