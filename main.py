from cli import OtakuCLI
from constants import DATA_DIR, EXPORT_DIR

def main():
    DATA_DIR.mkdir(exist_ok=True)
    EXPORT_DIR.mkdir(exist_ok=True)

    app = OtakuCLI()
    app.run()

if __name__ == "__main__":
    main()
