from enum import Enum
from pathlib import Path
from typing import Tuple

from src.discourse import create_discourse
from src.docs_directory import read as read_docs_directory
from src.reconcile import _local_only

DOCS_FOLDER = "docs"


class DocumentationType(str, Enum):
    TUTORIAL = "tutorial"
    HOWTO = "how-to"
    EXPLANATION = "explanation"
    REFERENCE = "reference"


def table_path_to_type(table_path: str) -> Tuple[DocumentationType, str]:
    for _type in DocumentationType:
        v = _type.value
        prefix = f"{v}-{v[0]}-"
        if table_path.startswith(prefix):
            return DocumentationType(v), table_path.removeprefix(prefix)
    raise ValueError("Malformatted input")


def create_title(prefix: str, table_path: str):
    document_type, title = table_path_to_type(table_path)

    formatted_title = " ".join(word.capitalize() for word in title.split("-"))

    return f"{prefix} {document_type.value.capitalize()} - {formatted_title}"


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--user", required=True)
    parser.add_argument("--access-key", required=True)
    parser.add_argument("--repo-path", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--discourse-url", default="discourse.charmhub.io")
    parser.add_argument("--group-id", default="41")
    parser.add_argument("--doc-folder", default=DOCS_FOLDER)
    parser.add_argument('--tags', nargs='*', default=[])

    args = parser.parse_args()

    print("Creating Discourse bindings...")

    discourse = create_discourse(args.discourse_url, args.group_id, args.user, args.access_key)

    repo_path = Path(args.repo_path)

    path_infos = read_docs_directory(docs_path=repo_path / args.doc_folder)

    print("Creating topics...")

    import csv

    discourse._tags = args.tags

    with open(f'{args.prefix}_links.csv', 'w', newline='') as csvfile:
        writer = csv.writer(
            csvfile, delimiter=';',
            quotechar='|', quoting=csv.QUOTE_MINIMAL
        )

        for path in path_infos:
            if path.level == 2:
                action = _local_only(path)
                title = create_title(args.prefix, path.table_path)

                _type, _title = table_path_to_type(path.table_path)

                print(action.content)

                # url = "url"
                discourse._tags = tuple(list(args.tags) + [_type.value])
                url = discourse.create_topic(title, action.content)
                writer.writerow([f"{_type.value[0]}-{_title}", url])
