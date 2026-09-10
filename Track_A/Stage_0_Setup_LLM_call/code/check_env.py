import sys, importlib
print("python:", sys.version.split()[0])
for pkg in ("anthropic", "dotenv"):
    m = importlib.import_module(pkg)
    print(f"{pkg}:", getattr(m, "__version__", "(no __version__)"))