from app import create_app
from app.database import init_db
import os

os.makedirs('uploads', exist_ok=True)

app = create_app()
init_db()

if __name__ == '__main__':
    app.run(debug=True)
