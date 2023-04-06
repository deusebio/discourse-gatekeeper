from src.discourse import create_discourse
from src.metadata import get
from pathlib import Path
from src.index import get as get_index
from src.index import contents_from_page
from src.navigation_table import from_page
from src.migration import _validate_table_rows, _get_docs_metadata, _run_one

DOCS_FOLDER="docs"

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--user", required=True)
    parser.add_argument("--access-key", required=True)
    parser.add_argument("--repo-path", required=True)
    parser.add_argument("--from-index-url", required=False)
    parser.add_argument("--discourse-url", default="discourse.charmhub.io")
    parser.add_argument("--group-id", default="41")
    parser.add_argument("--doc-folder", default=DOCS_FOLDER)
    
    args = parser.parse_args()

    print("Creating Discourse bindings...")

    discourse = create_discourse(args.discourse_url, args.group_id, args.user, args.access_key)

    repo_path = Path(args.repo_path)

    if args.from_index_url is None:

        metadata = get(repo_path)

        index = get_index(metadata, repo_path, discourse)
        server_content = index.server.content
    else:
        server_content = discourse.retrieve_topic(args.from_index_url)

    print("Parse table...")

    index_content = contents_from_page(server_content)

    table_rows = from_page(page=server_content, discourse=discourse)
    
    lst_table_rows = list(table_rows)
    
    valid_table_rows = _validate_table_rows(table_rows=lst_table_rows)
    document_metadata = _get_docs_metadata(table_rows=valid_table_rows, index_content=index_content)
    
    docs_path = repo_path / args.doc_folder

    print(f"Importing to path {docs_path}")

    for document in document_metadata:
        print(f"Creating {document.path}")
        _run_one(file_meta=document, discourse=discourse, docs_path=docs_path)

    
    
    
    


