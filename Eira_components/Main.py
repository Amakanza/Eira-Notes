from src.database import init_db
from src.gui import EiraNotesApp


if __name__ == "__main__":
    app = EiraNotesApp()
    
    # Set window icon if available
    # app.iconbitmap("icon.ico")  # Uncomment and provide path to icon if available
    
    app.mainloop()