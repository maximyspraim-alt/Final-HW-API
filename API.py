import re
import requests
import json
from urllib.parse import quote

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def get_user_input() -> tuple[str, str]:
    """Получает от пользователя текст для картинки и токен Яндекс.Диска."""
    token = input('Введите токен Яндекс.Диска: ').strip()
    if not token:
        print("Ошибка: токен не может быть пустым.")
        exit(1)

    text = input('Введите текст для картинки: ').strip()
    if not text:
        print("Ошибка: текст не может быть пустым.")
        exit(1)

    return token, text


def clean_filename(text: str) -> str:
    """Очищает текст для безопасного использования в имени файла."""
    return re.sub(r'[^\w\-]+', '_', text).strip('_')

# === 3. Подготовка данных ===
safe_filename = clean_filename(picture_text)
encoded_text = quote(picture_text, safe='')
image_url = f"https://cataas.com/cat/says/{encoded_text}".strip()
folder_name = "pd-fpy_140"

def get_image_info(text: str) -> tuple[str, int | None]:
    """Получает URL и размер изображения с cataas.com."""
    encoded_text = quote(text, safe='')
    image_url = f"https://cataas.com/cat/says/{encoded_text}"

    try:
        response = requests.get(
            image_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
            stream=True
        )
        if response.status_code != 200:
            print(f"Ошибка: cataas.com вернул статус {response.status_code}")
            exit(1)

        size_str = response.headers.get('Content-Length')
        file_size = int(size_str) if size_str else None
        response.close()
        return image_url, file_size

    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения с cataas.com: {e}")
        exit(1)


def create_yandex_folder(folder_name: str, token: str) -> None:
    """Создаёт папку на Яндекс.Диске, если её ещё нет."""
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": folder_name}

    try:
        response = requests.put(url, headers=headers, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании папки: {e}")
        exit(1)

    if response.status_code == 201:
        print("Папка успешно создана.")
    elif response.status_code == 409:
        print("Папка уже существует — продолжаем.")
    else:
        msg = response.json().get('message', 'Неизвестная ошибка')
        print(f"Ошибка при создании папки: {response.status_code} — {msg}")
        exit(1)


def upload_image_to_yandex(image_url: str, folder_name: str, filename: str, token: str) -> None:
    """Загружает изображение на Яндекс.Диск по URL."""
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {"Authorization": f"OAuth {token}"}
    full_path = f"{folder_name}/{filename}.jpg"
    params = {
        "path": full_path,
        "url": image_url
    }

    try:
        response = requests.post(upload_url, headers=headers, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке файла: {e}")
        exit(1)

    if response.status_code == 202:
        print("Загрузка файла запрошена успешно (Яндекс.Диск скачивает картинку).")
    else:
        msg = response.json().get('message', 'Неизвестная ошибка')
        print(f"Ошибка при загрузке файла: {response.status_code} — {msg}")
        exit(1)


def save_backup_info(text: str, size: int | None, filename: str = "backup_info.json") -> None:
    """Сохраняет информацию о файле в JSON."""
    data = {
        "filename": text,
        "size_bytes": size
    }
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Информация о файле сохранена в {filename}")
    except Exception as e:
        print(f"Ошибка при записи JSON-файла: {e}")
        exit(1)


# === ОСНОВНАЯ ФУНКЦИЯ ===

def main():
    FOLDER_NAME = "pd-fpy_140"

    token, picture_text = get_user_input()
    safe_filename = clean_filename(picture_text)
    image_url, file_size = get_image_info(picture_text)

    create_yandex_folder(FOLDER_NAME, token)
    upload_image_to_yandex(image_url, FOLDER_NAME, safe_filename, token)
    save_backup_info(picture_text, file_size)


# === ТОЧКА ВХОДА ===

if __name__ == "__main__":
    main()