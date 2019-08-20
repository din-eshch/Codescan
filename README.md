# Python script to run sec tools within a Docker container

The script clones git repo to a local */tmp*, creates a dummy container, mounts */tmp* as a volume, run sec tools for the language/type specified and outputs the results to a text file. All config options are availble inside *scanConfig.ini*. Modify command line options for the tools under *[ExecCmds]* or update the docker image with new tools as you see fit.

*Usage: codescan -t [rb/py/pw] path_to_git_src*

**Note:** The following tools are added to the base image at this point
- [Bandit](https://github.com/PyCQA/bandit) for Python
- [Brakeman](https://github.com/presidentbeef/brakeman) for Rails
- [TruffleHog](https://github.com/dxa4481/truffleHog) for secrets

### To run the script on your local machine

**Step 1:** Install these dev dependencies: docker and git SDKs for python
    [Git Python](https://github.com/gitpython-developers/GitPython), 
    [Docker Python API](https://docker-py.readthedocs.io/en/1.8.0/) and 
    [Docker SDK](https://docker-py.readthedocs.io/en/stable/)

**Step 2:** Run *setup.py* with *python3* (secrets module is only available in >= python 3)

    python3 setup.py install

**Step 3:** Run *codescan* from the installation directory


### To add new tools to the Docker base image

Build using the Dockerfile

    docker build -t codesign:latest .


