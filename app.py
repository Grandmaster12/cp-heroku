from website import create_app
from flask_sqlalchemy import SQLAlchemy

CP = create_app()
# with CP.app_context():
#     db = SQLAlchemy(CP)

if __name__ == "__main__":
    CP.run(debug=True, port=5001)

    