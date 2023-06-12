import sys
from pathlib import Path
import uuid
import shutil

EXCEPTION = ["Audio", "Documents", "Images", "Video", "Archives", "Other"]

CATEGORIES = {
    "Audio": [".mp3", ".aiff", ".oog", ".wav", ".amr"],
    "Documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx"],
    "Images": [".jpeg", ".png", ".jpg", ".svg"],
    "Video": [".avi", ".mp4", ".mov", ".mkv"],
    "Archives": [".zip", ".gz", ".tar"],
    "Other": [],
}
CYRILLIC_SYMBOLS = "абвгґдеёєжзиіїйклмнопрстуфхцчшщъыьэюя"
TRANSLATION = (
    "a",
    "b",
    "v",
    "h",
    "g",
    "d",
    "e",
    "e",
    "ie" "zh",
    "z",
    "y",
    "i",
    "yi",
    "y",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "r",
    "s",
    "t",
    "u",
    "f",
    "kh",
    "ts",
    "ch",
    "sh",
    "shch",
    "",
    "y",
    "",
    "e",
    "yu",
    "ya",
)

BAD_SYMBOLS = ("%", "*", " ", "-")

TRANS = {}

dict_search_result = {}


def unpack_archive(item: Path, cat: Path):
    archive_name = item.stem
    output_dir = cat / archive_name
    output_dir.mkdir(exist_ok=True)

    shutil.unpack_archive(str(item), str(output_dir))


def delete_empty_folders(path):
    path = Path(path)
    if not path.is_dir():
        return

    for item in path.iterdir():
        if item.is_dir():
            delete_empty_folders(item)
    if not any(True for _ in path.iterdir()):
        path.rmdir()


def delete_arch_files(path):
    path = Path(path)

    if path.is_dir():
        for item in path.iterdir():
            delete_arch_files(item)

    if path.is_file() and path.suffix.lower() in (".zip", ".tar", ".gz"):
        path.unlink()


def file_list():
    lst = []
    lst.append("|" + "=" * 50 + "|")
    for category, value in dict_search_result.items():
        lst.append("|{:^50}|".format(category))
        lst.append("|" + "=" * 50 + "|")
        ext = "Extensions: "
        for extension in value[1]:
            ext += extension + ", "
        ext = ext[:-2]
        lst.append("|{:<50}|".format(ext))
        lst.append("|" + "-" * 50 + "|")
        for element in value[0]:
            lst.append("|{:<50}|".format(element))
        lst.append("|" + "=" * 50 + "|")

    for i in lst:
        print(i)

    return lst


def normalize(name: str) -> str:
    for c, t in zip(list(CYRILLIC_SYMBOLS), TRANSLATION):
        TRANS[ord(c)] = t
        TRANS[ord(c.upper())] = t.upper()

    for i in BAD_SYMBOLS:
        TRANS[ord(i)] = "_"

        trans_name = name.translate(TRANS)
    return trans_name


def move_file(file: Path, root_dir: Path, categorie: str) -> None:
    target_dir = root_dir.joinpath(categorie)
    if not target_dir.exists():
        print(f"Створюємо {target_dir}")
        target_dir.mkdir()
    if file.suffix.lower() in (".zip", ".tar", ".gz"):
        try:
            unpack_archive(file, target_dir)
        except shutil.ReadError:
            return
    new_name = target_dir.joinpath(f"{normalize(file.stem)}{file.suffix}")
    if new_name.exists():
        new_name = new_name.with_name(f"{new_name.stem}-{uuid.uuid4()}{file.suffix}")
    file.rename(new_name)


def get_categories(file: Path, dict_search_result) -> str:
    ext = file.suffix.lower()

    for cat, exts in CATEGORIES.items():
        if ext in exts:
            if cat in dict_search_result:
                file_list = dict_search_result[cat][0]
                if file.name in file_list:
                    return cat
                file_list.append(file.name)
                dict_search_result[cat][1].add(ext)
            else:
                dict_search_result[cat] = [[file.name], {ext}]
            return cat

    return "Other"


def sort_folder(path: Path) -> None:
    global dict_search_result
    for item in path.glob("**/*"):
        # print(item)
        if item.is_dir() and item.name in EXCEPTION:
            return
        if item.is_file():
            cat = get_categories(item, dict_search_result)
            move_file(item, path, cat)


def main():
    try:
        path = Path(sys.argv[1])
        # path = Path("C:\\Testfolder")
        print(f"Папка для сортування ", {path})
    except IndexError:
        return "Не вказана папка для сортування"

    if not path.exists():
        return f"Папка з таким шляхом {path} не існує."

    sort_folder(path)
    delete_empty_folders(path)
    delete_arch_files(path)
    file_list()

    return print("Программа завершила роботу.")


if __name__ == "__main__":
    print(main())
