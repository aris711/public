#!/usr/bin/python3

import os
import requests
import time
import platform
import subprocess
import sh


project_name = 'My_project'

bot_token = '1234567890:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
chat_id = 'XXXXXXXXXX'

base_dir = os.path.dirname(os.path.abspath(__file__))
host = f'user@host'
src_dir = f'/path/to/dir/{project_name}/img'
dst_dir = f'{base_dir}/{project_name}/img'
log_file = f'{base_dir}/{project_name}/{project_name}.log'


def get_time_stamp() -> str:
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    return current_time


def log(title: str, text: str) -> None:
    global log_file
    print(f"{get_time_stamp()} [{title}]\t{text}", file=open(log_file, "at"))
    return None


def check_ping(host):
    parameter = '-n' if platform.system().lower()=='windows' else '-c'
    command = 'ping ' + parameter + ' 1 ' + host
    response, *_ = subprocess.getstatusoutput(command)
    if response == 0:
        return True
    else:
        return False


def send_message_telegram(text, device_name='My_server', title=f'{project_name} images copying completed!'):
    parse_mode = "html"
    disable_web_page_preview = "true"
    icon = "📀"
    title_text = f"{icon} <b>{device_name}: {title}</b>\n"
    message = "https://api.telegram.org/bot" + bot_token + \
              "/sendMessage?chat_id=" + chat_id + \
              "&parse_mode=" + parse_mode + \
              "&disable_web_page_preview=" + disable_web_page_preview +\
              "&text=" + title_text + text
    try:
        response = requests.get(message)
        result = response.json()
    except:
        log("backup_img", f'Сообщение не отправлено')
        return False
    else:
        log("backup_img", f'Сообщение отправлено')
        return result

def main() -> None:
    count_new_dirs = 0
    start_time = time.time()
    src_dirs = set(sh.ssh(host, f'ls {src_dir}').split())
    dst_dirs = set(sh.ls(f'{dst_dir}').split())
    new_dirs = src_dirs - dst_dirs
    if new_dirs:
        count_new_dirs = len(new_dirs)
        log('backup_img', f'На сервере обнаружено новых каталогов: {count_new_dirs}. Воссоздание дерева каталогов')
        for new_dir in new_dirs:
            sh.mkdir('-p', f'{dst_dir}/{new_dir}')
    del src_dirs, dst_dirs, new_dirs

    src_files = set(sh.ssh(host, f'cd {src_dir}; find -type f').split())
    sh.cd(dst_dir)
    dst_files = set(sh.find('-type', 'f').split())
    new_files = src_files - dst_files
    size_before_copying = int(sh.du('-s').split()[0])
    if new_files:
        count_new_files = len(new_files)
        log('backup_img', f'На сервере обнаружено новых файлов: {count_new_files}. Начинаю копирование...')
        for cnt, new_file in enumerate(new_files):
            if (cnt + 1) % 10 == 0:
                log('backup_img', f'Скопировано файлов: {cnt}...')
            current_dir, current_file = new_file.split('/')[1:]
            sh.scp('-p', '-r', f'{host}:{src_dir}/{current_dir}/{current_file}', f'{dst_dir}/{current_dir}/{current_file}')

        size_after_copying = int(sh.du('-s').split()[0])
        size_delta = round((size_after_copying - size_before_copying) / 1024, 1)
        log('backup_img', f'Размер скопированных файлов {size_delta} Мб')
        time_delta = int(time.time() - start_time)
        time_delta = f'{str(time_delta // 3600).zfill(2)}:{str(time_delta // 60 % 60).zfill(2)}:{str(time_delta % 60).zfill(2)}'
        log('backup_img', f'Время копирования: {time_delta}')
        message = f'{get_time_stamp()} New images copying completed.\n' \
                  f'Copied file size: {size_delta}Mb\n' \
                  f'New files: {count_new_files}\n' \
                  f'New dirs: {count_new_dirs}\n' \
                  f'Time spent copying: {time_delta}'
        send_message_telegram(message)
    del src_files, dst_files, new_files
    return None


if __name__ == '__main__':

    log('backup_img', f'Начало работы скрипта')
    if check_ping(project_name):
        main()
    else:
        log("backup_img", f'Сервер {project_name} недоступен')

    log('backup_img', f'Завершение работы')
