import click
import yaml
from pathlib import Path
import os 

@click.group()
@click.pass_context
def app(ctx):
    """
    Take a single kubernetes manifest containing multiple resources and split it to many files with a kustomization file
    """


@click.command()
@click.option("--file_path", "-f", type=click.Path(resolve_path=True), required=True, help="Path to your k8s manifest")
def kustomize_file():
    file_path = Path(file_path)
    assert file_path.exists(), "File does not exist"
    assert file_path.is_file(), "File is not a file"
    assert file_path.suffix == ".yaml", "File is not a yaml file"

    saved_files = {}
    with open(file_path, "r") as f:
        docs = yaml.load_all(f, yaml.FullLoader)
        # doc = next(docs)
        for doc in docs:
            new_file_index = f"{doc['kind'].lower()}"
            if not new_file_index in saved_files:
                saved_files[new_file_index] = []
                idx = 0
            else:
                idx = len(saved_files[new_file_index])
            new_file = f"{os.path.join(*file_path.parts[:-1])}/{doc['kind'].lower()}-{idx}.yaml"
            
            with open(new_file, "w") as f:
                yaml.dump(doc, f)
            saved_files[new_file_index].append(new_file)

    with open(f"{os.path.join(*file_path.parts[:-1])}/kustomization.yaml", "w") as f:
        yaml.dump({"apiVersion": "kustomize.config.k8s.io/v1beta1", "kind": "Kustomization", "resources": [v for k, v_list in saved_files.items() for v in v_list]}, f)


if __name__ == "__main__":
    app()