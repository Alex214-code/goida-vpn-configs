
import os
import requests
from github import Github
from github import GithubException
from datetime import datetime
import zoneinfo
import concurrent.futures

# Получение текущего времени по часовому поясу Европа/Москва
zone = zoneinfo.ZoneInfo("Europe/Moscow")
thistime = datetime.now(zone)
offset = thistime.strftime("%H:%M | %d.%m.%Y")  # Формат времени для коммитов

# Получение GitHub токена из переменных окружения
GITHUB_TOKEN = os.environ.get("MY_TOKEN")
# Имя репозитория для загрузки файлов
REPO_NAME = "AvenCores/goida-vpn-configs"

# Создаём объект Github и репозиторий один раз, чтобы не делать это при каждой загрузке
g = Github(GITHUB_TOKEN)
REPO = g.get_repo(REPO_NAME)

# Проверка и создание локальной папки для хранения файлов, если она отсутствует
if not os.path.exists("githubmirror"):
    os.mkdir("githubmirror")

# Список URL-адресов для скачивания конфигов
URLS = [
    "https://istanbulsydneyhotel.com/blogs/site/sni.php?security=reality", #1
    "https://istanbulsydneyhotel.com/blogs/site/sni.php", #2
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt", #3
    "https://raw.githubusercontent.com/acymz/AutoVPN/refs/heads/main/data/V2.txt", #4
    "https://raw.githubusercontent.com/AliDev-ir/FreeVPN/main/pcvpn",  #5
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt",  #6
    "https://github.com/Epodonios/v2ray-configs/raw/main/All_Configs_Sub.txt",  #7
    "https://raw.githubusercontent.com/YasserDivaR/pr0xy/main/mycustom1.txt",  #8
    "https://vpn.fail/free-proxy/v2ray",   #9
    "https://raw.githubusercontent.com/Proxydaemitelegram/Proxydaemi44/refs/heads/main/Proxydaemi44",  #10
    "https://raw.githubusercontent.com/youfoundamin/V2rayCollector/main/mixed_iran.txt",   #11
    "https://raw.githubusercontent.com/mheidari98/.proxy/refs/heads/main/all",   #12
    "https://github.com/Kwinshadow/TelegramV2rayCollector/raw/refs/heads/main/sublinks/mix.txt",   #13
    "https://github.com/LalatinaHub/Mineral/raw/refs/heads/master/result/nodes",   #14
    "https://github.com/4n0nymou3/multi-proxy-config-fetcher/raw/refs/heads/main/configs/proxy_configs.txt",   #15
    "https://github.com/freefq/free/raw/refs/heads/master/v2",    #16
    "https://github.com/MhdiTaheri/V2rayCollector_Py/raw/refs/heads/main/sub/Mix/mix.txt", #17
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/All_Configs_Sub.txt", #18
    "https://github.com/MhdiTaheri/V2rayCollector/raw/refs/heads/main/sub/mix",   #19
    "https://raw.githubusercontent.com/mehran1404/Sub_Link/refs/heads/main/V2RAY-Sub.txt",  #20
    "https://raw.githubusercontent.com/shabane/kamaji/master/hub/merged.txt",   #21
    "https://raw.githubusercontent.com/wuqb2i4f/xray-config-toolkit/main/output/base64/mix-uri",   #22
    "https://raw.githubusercontent.com/V2RAYCONFIGSPOOL/V2RAY_SUB/refs/heads/main/v2ray_configs.txt",  #23
]

# Пути для сохранения файлов локально и в репозитории
REMOTE_PATHS = [f"githubmirror/{i+1}.txt" for i in range(len(URLS))]
LOCAL_PATHS = [f"githubmirror/{i+1}.txt" for i in range(len(URLS))]

# Функция для скачивания данных по URL
def fetch_data(url, timeout: int = 10):
    """Скачивает данные по URL с таймаутом и базовой обработкой ошибок."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()  # Генерирует исключение при ошибке
    return response.text

# Сохраняет полученные данные в локальный файл
def save_to_local_file(path, content):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"📁 Данные сохранены локально в {path}")

# Загружает файл в репозиторий GitHub (обновляет или создаёт новый)
def upload_to_github(local_path, remote_path):
    """Загружает или обновляет файл в репозитории GitHub.

    1. Если файл отсутствует – создаёт его.
    2. Если файл уже есть и содержимое изменилось – обновляет его.
    3. Если изменений нет – пропускает загрузку.
    """

    # Проверка наличия локального файла
    if not os.path.exists(local_path):
        print(f"❌ Файл {local_path} не найден.")
        return

    # Используем уже созданный объект репозитория
    repo = REPO

    # Чтение содержимого локального файла
    with open(local_path, "r", encoding="utf-8") as file:
        content = file.read()

    try:
        # Пытаемся получить файл из репозитория
        file_in_repo = repo.get_contents(remote_path)

        # Обновляем файл, только если содержимое изменилось
        if file_in_repo.decoded_content.decode("utf-8") != content:
            repo.update_file(
                path=remote_path,
                message=f"🚀 Обновление конфига ({offset})",
                content=content,
                sha=file_in_repo.sha
            )
            print(f"🚀 Файл {remote_path} обновлён в репозитории.\n")
        else:
            print(f"🔄 Изменений для {remote_path} нет.\n")
    except GithubException as e:
        if e.status == 404:
            # Файл не найден – создаём новый
            repo.create_file(
                path=remote_path,
                message=f"🆕 Первый коммит ({offset})",
                content=content
            )
            print(f"🆕 Файл {remote_path} создан.\n")
        else:
            # Любая другая ошибка
            print(f"⚠️ Ошибка при загрузке {remote_path}: {e.data.get('message', e)}\n")

# Функция для параллельного скачивания и сохранения файла
def download_and_save(idx):
    url = URLS[idx]
    local_path = LOCAL_PATHS[idx]
    try:
        data = fetch_data(url)
        save_to_local_file(local_path, data)
        return local_path, REMOTE_PATHS[idx]
    except Exception as e:
        print(f"⚠️ Ошибка при скачивании {url}: {e}\n")
        return None

# Основная функция: скачивает, сохраняет и загружает все конфиги
def main():
    # Параллельно скачиваем файлы и сохраняем их локально
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(URLS))) as executor:
        futures = [executor.submit(download_and_save, i) for i in range(len(URLS))]

        # По мере завершения скачивания — загружаем файл в GitHub
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                local_path, remote_path = result
                upload_to_github(local_path, remote_path)

# Точка входа в программу
if __name__ == "__main__":
    main()
