#!/usr/bin/python3

import os
import time
import paramiko


www = 'https://my_host/img/'

ssh_user = 'user'
ssh_host = 'my_host'
ssh_pwd = 'p@ssw0rd'
# ssh_host = input('SSH host: ')
# ssh_user = input('SSH username: ')
# ssh_pwd = input('SSH password: ')

src_path = '/path/to/src/'
dst_path = '/path/to/dst/'

log_file = os.getcwd() + "/project_foto.log"
result_file = os.getcwd() + "/result.csv"


def get_time_stamp() -> str:
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    return current_time


def log(title: str, text: str) -> None:
    global log_file
    print(f"{get_time_stamp()} [{title}]\t{text}", file=open(log_file, "at"))
    return None


def log_ssh(command, stdout, stderr) -> bool:
    result = False
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if output:
        log("info", f'Command: {command} return: {output}')
    if error:
        log("error", f'Command: {command} return: {error}')
        result = True
    return result


def normalize_extension(ext: str) -> str:
    result = ext.strip().lower()
    if result[0] == 'j' and len(result) != 3:
        result = 'jpg'
    return result


def get_bypass_name(name: str) -> str:
    result = list(name)
    result = '\\' + '\\'.join(result)
    return result


def is_normal_name(name: str) -> bool:
    if name.count('.'):
        return True
    else:
        return False


def is_normal_ext(name: str) -> bool:
    ext = name.split(".")[-1]
    if ext[0].lower() == 'j' and len(ext) < 3:
        return False
    else:
        return True


def run(src_txt: str, result_csv: str, host: str, user: str, pwd: str) -> None:
    log('task', f'Start {src_txt}')
    subdirs = set()
    rm_files = set()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=host, username=user, password=pwd)
        log("ssh_client", f"Connect to {host}")
        with open(src_txt, 'rt', encoding='utf8') as data:
            codes = dict()
            for line in data.readlines():
                orig_code, orig_file_name = line.strip().split("\t")
                if "-" in orig_code:
                    code = orig_code.replace('-', '')
                    subdir = f'{code[1:4]}/'
                    codes[code] = codes.setdefault(code, 0) + 1
                else:
                    code = orig_code
                    subdir = '_/'
                filename = orig_file_name.split('/')[-1]
                if not is_normal_name(filename):
                    log("error", f"File {orig_file_name} with code {orig_code} is not normal name")
                    continue
                if not is_normal_ext(filename):
                    filename = ".".join(filename.split('.')[:-1]) + '.jpg'
                    log("warning", f"File {orig_file_name} with code {orig_code} is create normal extension {filename}")
                bypass_filename = get_bypass_name(filename)
                ext = filename.split('.')[-1].lower()
                if ext == 'jpeg':
                    ext = 'jpg'
                src_file = f'{src_path}{bypass_filename}'
                suffix = codes.setdefault(code, 0)
                if suffix:
                    dst_short_name = f'{subdir}{code}_{str(suffix).zfill(2)}.{ext}'
                else:
                    dst_short_name = f'{subdir}{code}.{ext}'
                dst_file = f'{dst_path}{dst_short_name}'
                if subdir not in subdirs:
                    command = f'mkdir -p {dst_path}{subdir}'
                    print(command, file=open('command.txt', 'at', encoding='utf-8'))
                    stdin, stdout, stderr = ssh.exec_command(command)
                    log_ssh(command, stdout, stderr)
                    subdirs.add(subdir)
                command = f'cp {src_file} {dst_file}'
                print(command, file=open('command.txt', 'at', encoding='utf-8'))
                stdin, stdout, stderr = ssh.exec_command(command)
                if log_ssh(command, stdout, stderr):
                    log("ssh_client", f"File {orig_code} {orig_file_name} do not copied")
                else:
                    rm_files.add(src_file)
                    print(f'{code}\t{www + dst_short_name}\t{orig_code}\t{orig_file_name}',
                          file=open(result_csv, 'at', encoding='utf8'))
        if rm_files:
            for file in rm_files:
                command = f'rm -f {file}'
                print(command, file=open('command.txt', 'at', encoding='utf-8'))
                stdin, stdout, stderr = ssh.exec_command(command)
                log_ssh(command, stdout, stderr)
    except paramiko.AuthenticationException:
        log('ssh_client', f'{user}@{host} wrong credentials')
    except:
        log('ssh_client', f'{host} cannot connected')
    ssh.close()
    log("ssh_client", f"Disconnected {host}")
    log('task', f'Finish {src_txt}')
    return None


if __name__ == '__main__':

    log("app", f"Starting")

    # Init csv-file
    print('my_id\tnew_url\toriginal_id\toriginal_url', file=open(result_file, 'w', encoding='utf-8'))

    run('_category.txt', result_file, ssh_host, ssh_user, ssh_pwd)
    run('_product.txt', result_file, ssh_host, ssh_user, ssh_pwd)

    log("app", f"Successful")
