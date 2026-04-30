import sys
from pathlib import Path

# Ensure the 'src' directory is in the Python path
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import QApplication
from sikulipy.gui.main_window import SikuliPyMainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set global application style
    app.setStyle("Fusion")
    
    window = SikuliPyMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
