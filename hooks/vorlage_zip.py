"""MkDocs-Hook: packt den Ordner projekt-vorlage/ beim Bauen als downloads/yolo-projekt-vorlage.zip in die Seite."""
import io
import zipfile
from pathlib import Path

from mkdocs.structure.files import File

AUSLASSEN = {".venv", "__pycache__", ".ipynb_checkpoints", "1_rohbilder", "2_bilder", "3_labelstudio_export",
             "4_datensatz", "drive_ersatz", "_colab_daten"}
DATEIEN_AUSLASSEN = {"labelstudio.log", ".labelstudio.pid", "katalog.csv", "projekt.yaml"}


def on_files(files, config):
    vorlage = Path(config["config_file_path"]).parent / "projekt-vorlage"
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(vorlage.rglob("*")):
            rel = p.relative_to(vorlage)
            if not p.is_file() or set(rel.parts) & AUSLASSEN or p.name in DATEIEN_AUSLASSEN or p.suffix == ".pt":
                continue
            z.write(p, (Path("yolo-projekt") / rel).as_posix())
    files.append(File.generated(config, "downloads/yolo-projekt-vorlage.zip", content=puffer.getvalue()))
    return files
