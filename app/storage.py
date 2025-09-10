
import os, shutil, tempfile

ROOT = tempfile.gettempdir()
NAMESPACE = "compliance_api"

def namespace_dir():
    path = os.path.join(ROOT, NAMESPACE)
    os.makedirs(path, exist_ok=True)
    return path

def save_temp(key: str, upload_file) -> str:
    path = os.path.join(namespace_dir(), key)
    filename = getattr(upload_file, "filename", None) or "upload.bin"
    ext = os.path.splitext(filename)[1]
    full = path + ext
    with open(full, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
    return full

def get_temp_path(key: str) -> str:
    p = os.path.join(namespace_dir(), key)
    if os.path.exists(p):
        return p
    for fn in os.listdir(namespace_dir()):
        if fn.startswith(key):
            return os.path.join(namespace_dir(), fn)
    raise FileNotFoundError(key)
