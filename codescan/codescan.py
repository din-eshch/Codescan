import argparse
import configparser
import os
import secrets
import subprocess
import sys
import docker
from git import Repo

config = configparser.ConfigParser()
INI_PATH = 'codescan/scanConfig.ini' #  Path to ini
try:
    fp_ini = config.read(INI_PATH)  # Initializing configuration file
    if not fp_ini:
        print('\033[91mError:\033[0mConfiguration file not found')
        sys.exit(1)
except Exception as e:
    print('\033[91mError:\033[0mTypo(s) in configuration file: ' + str(e))
    sys.exit(1)
GIT_PATH = config['GitURL']['Dev']  # Base URL to Git instance
VOLUME_CON = config['MountPoints']['CPath']  # Mount point inside the container
VOLUME_HOST = config['MountPoints']['HPath']  # Mount point on the host
BASEIMG_URL = config['BaseImage']['Url']  # URL for conatiner base image
LOG_FILE = config['FilePath']['Logfile']  # Path to log file


# Parsing cmd line args
def parse_cmds():
    parser = argparse.ArgumentParser(
        prog='codescan',
        usage='%(prog)s -t [rb/py/pw] path')
    parser.add_argument(
        'path',
        help='Specify GHE git path',
        type=str)
    parser.add_argument(
        '-type',
        nargs='?',
        help='Specify type of scan',
        choices=['rb', 'py', 'pw'],
        type=str,
        required=True)
    args = parser.parse_args()
    if args.path.lower().find(GIT_PATH) < 0:  # Only to my Dev URLs
        print('\033[91mError:\033[0mOnly my GIT path permitted')
        sys.exit(1)
    if args.type == 'rb':
        exec_cmd = config['ExecCmds']['rb']  # Cmd to execute Brakeman
    elif args.type == 'py':
        exec_cmd = config['ExecCmds']['py']  # Cmd to exceute Bandit
    elif args.type == 'pw':
        exec_cmd = config['ExecCmds']['pw']  # Cmd to exceute TruffleHog
    else:
        print('\033[91mError:\033[0mScan type not supported')
        sys.exit(1)
    # Clone the Git repo and set up container for scanning
    set_tmp()
    git_clone(args.path)
    set_container(exec_cmd)


# Creating tmp folder for holding git src
def set_tmp():
    print('\033[94mStatus:\033[0mCleaning up ' + VOLUME_HOST)
    subprocess.Popen(['rm', '-rf', VOLUME_HOST]).wait()  # Remove tmp-host
    subprocess.Popen(['mkdir', VOLUME_HOST]).wait()  # Create /tmp/tmp-host


# Cloning git repo into tmp
def git_clone(git_url):
    try:
        print('\033[94mStatus:\033[0mGit clone started')
        cloned_repo = Repo.clone_from(git_url, VOLUME_HOST)
        if not cloned_repo:
            print('\033[91mError:\033[0mGit clone failed')
            sys.exit(1)
    except Exception as e:
            print('\033[91mError:\033[0mGit exception: ' + str(e))
            sys.exit(1)
    print('\033[94mStatus:\033[0mGit clone completed')


# Setting up volume and container env
def set_container(exec_cmd):
    if VOLUME_CON:
        volumes = []
        volumes.append(VOLUME_CON)
        cfs = ['{}:{}:rw'.format(VOLUME_HOST, VOLUME_CON)]  # Mount volume H:C
    else:
        print('\033[91mError:\033[0mVolume Error')
        sys.exit(1)
    print('\033[94mStatus:\033[0m' + VOLUME_HOST + ' mounted on ' + VOLUME_CON)
    client = docker.Client(base_url='unix:///var/run/docker.sock')
    try:  # Pull latest image from Artifactory
        print('\033[94mStatus:\033[0mPulling latest image from Artifactory: '
              + BASEIMG_URL)
        latest_img = client.pull(BASEIMG_URL, tag='latest')
    except Exception as e:
        print('\033[91mError:\033[0mdDocker login before attemping pull: '
              + str(e))
        sys.exit(1)
    # Create container with specified config
    container = client.create_container(
        image=BASEIMG_URL,
        name='sl-'+secrets.token_hex(4),
        stdin_open=True,
        tty=True,
        volumes=volumes,
        working_dir=VOLUME_CON,
        host_config=client.create_host_config(binds=cfs))
    container_id = container.get('Id')
    resource = client.start(container=container_id)
    if resource is None:
        print('\033[94mStatus:\033[0mContainer started: {}'.format(
             container_id[:12]))
        env = client.exec_create(container=container_id, cmd=exec_cmd)
        print('\033[94mStatus:\033[0mCmd running: ' + exec_cmd)
        logs = client.exec_start(exec_id=env)
        #  Write scan info to log file
        with open(LOG_FILE, "w") as w_file:
            w_file.write(str(logs))
        print('\033[94mStatus:\033[0mScan logs written to ' + VOLUME_HOST)
    else:
        print('\033[91mError:\033[0mContainer failed to start')
        sys.exit(1)
    # Stop container
    client.stop(container=container_id)
    # Remove container
    client.remove_container(container=container_id, v=True)
    print('\033[94mStatus:\033[0mContainer removed: {}'.format(
        container_id[:12]))


def main():
    print('+'*50)
    print('CodeScan')
    print('For questions, contact dc@dc')
    print('+'*50)
    parse_cmds()  # Parse cmd line args
    print('\033[94mStatus:\033[0mScan results written to ' + VOLUME_HOST)
    print('+'*50)
    print('DONE!')
    print('+'*50)


if __name__ == '__main__':
    main()
