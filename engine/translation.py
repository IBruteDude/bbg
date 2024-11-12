import os
import requests as rs

from config.translations import LANGUAGES
from engine import OUTPUT_DIR


def generate_translations(project_name):

    base_path = os.path.join(os.getcwd(), OUTPUT_DIR, project_name, "api", "v1")
    os.system(f"pybabel extract -F {os.path.join(base_path, "babel.cfg")} -k _l -o {os.path.join(base_path, "messages.pot")} .")

    lines = []

    for lang in LANGUAGES:
        if lang == 'en':
            continue
        trans = os.path.join(base_path, "translations")
        lang_po = os.path.join(trans, lang, "LC_MESSAGES", "messages.po")

        os.system(f"pybabel init -i {os.path.join(base_path, "messages.pot")} -d {trans} -l {lang}")

        with open(lang_po) as f:
            lines = f.readlines()
            msgs = [
                (i, line[7:-2])
                for i, line in enumerate(lines)
                if line.startswith('msgid "')
            ]
            ids, texts = zip(*msgs)
        rapidapi_key = open("rapidapi.key").readline().strip()
        payload = {"sl": "auto", "tl": lang, "texts": [text for text in texts if text]}
        response = rs.post(
            "https://ai-translate.p.rapidapi.com/translate",
            headers={
                "Content-Type": "application/json",
                "x-rapidapi-host": "ai-translate.p.rapidapi.com",
                "x-rapidapi-key": rapidapi_key,
            },
            json=payload,
        )
        response = response.json()
        assert response["code"] == 200
        tls = response["texts"]
        for i, msgstr in enumerate(tls):
            lines[ids[i] + 1] = f'msgstr "{msgstr}"\n'

        with open(lang_po, "w", encoding="utf-8") as f:
            f.writelines(lines)

    os.system(f"pybabel compile -d {trans}")
