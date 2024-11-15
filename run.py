from app import create_app
from app.extensions import db
from app.models.bicycle import Bicycle

app = create_app()

with app.app_context():
    db.create_all()
    print(Bicycle.query.all())

if __name__ == "__main__":
    app.run(debug=True)
