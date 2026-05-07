import json
import os
import shutil


def salvar_json_seguro(caminho, data, indent=2, ensure_ascii=False):
    dirpath = os.path.dirname(caminho)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    backup_path = f"{caminho}.bak"
    if os.path.exists(caminho):
        shutil.copy2(caminho, backup_path)

    temp_path = f"{caminho}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

    os.replace(temp_path, caminho)
