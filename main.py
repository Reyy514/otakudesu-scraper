# otakudesu_cli/main.py
"""
File ini adalah titik masuk (entry point) utama untuk aplikasi.
Tugasnya sederhana: mengimpor kelas CLI dan menjalankannya.
"""
from cli import OtakuCLI
from constants import DATA_DIR, EXPORT_DIR

def main():
    DATA_DIR.mkdir(exist_ok=True)
    EXPORT_DIR.mkdir(exist_ok=True)

    app = OtakuCLI()
    app.run()

if __name__ == "__main__":
    main()
