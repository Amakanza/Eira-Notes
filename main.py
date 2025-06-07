from src.database import init_db
from src.gui import EiraNotesApp


if __name__ == "__main__":
    init_db()
    app = EiraNotesApp()
    # app.iconbitmap("icon.ico")  # Uncomment to set window icon
    app.mainloop()
