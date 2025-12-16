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

# === 2. Вспомогательная функция ===
def clean_filename(text):
    return re.sub(r'[^\w\-]+', '_', text).strip('_')

# === 3. Подготовка данных ===
safe_filename = clean_filename(picture_text)
encoded_text = quote(picture_text, safe='')
image_url = f"https://cataas.com/cat/says/{encoded_text}".strip()
folder_name = "pd-fpy_140"

headers_cataas = {
    "User-Agent": "Mozilla/5.0"
}
# === 4. Получение размера файла через GET с stream=True ===
try:
    response = requests.get(
        image_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
        stream=True
    )
    if response.status_code != 200:
        print(f"Ошибка: cataas.com вернул статус {response.status_code}")
        response.close()
        exit(1)

    size_str = response.headers.get('Content-Length')
    file_size = int(size_str) if size_str is not None else None
    response.close()

except requests.exceptions.RequestException as e:
    print(f"Ошибка соединения с cataas.com: {e}")
    exit(1)

# === 5. Создание папки на Яндекс.Диске ===
headers = {"Authorization": f"OAuth {token_disk}"}
url_create_folder = "https://cloud-api.yandex.net/v1/disk/resources"
params_folder = {"path": folder_name}

try:
    response = requests.put(url_create_folder, headers=headers, params=params_folder, timeout=10)
except requests.exceptions.RequestException as e:
    print(f"Ошибка при создании папки: {e}")
    exit(1)

if response.status_code == 201:
    print("Папка успешно создана.")
elif response.status_code == 409:
    print("Папка уже существует — продолжаем.")
else:
    error_msg = response.json().get('message', 'Неизвестная ошибка')
    print(f"Ошибка при создании папки: {response.status_code} — {error_msg}")
    exit(1)

# === 6. Загрузка картинки по URL ===
upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
params_upload = {
    "path": f"{folder_name}/{safe_filename}.jpg",
    "url": image_url
}

try:
    response = requests.post(upload_url, headers=headers, params=params_upload, timeout=10)
except requests.exceptions.RequestException as e:
    print(f"Ошибка при загрузке файла: {e}")
    exit(1)

if response.status_code == 202:
    print("Загрузка файла запрошена успешно (Яндекс.Диск скачивает картинку).")
else:
    error_msg = response.json().get('message', 'Неизвестная ошибка')
    print(f"Ошибка при загрузке файла: {response.status_code} — {error_msg}")
    exit(1)

# === 7. Сохранение информации в JSON ===
data = {
    "filename": picture_text,
    "size_bytes": file_size
}

try:
    with open("backup_info.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Информация о файле сохранена в backup_info.json")
except Exception as e:
    print(f"Ошибка при записи JSON-файла: {e}")
    exit(1)

print("Программа завершена успешно.")