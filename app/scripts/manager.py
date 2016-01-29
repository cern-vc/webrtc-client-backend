from app.config import BaseConfig
from app.app_factory import create_app
from flask_assets import ManageAssets, Environment
from app.extensions import db

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = create_app(BaseConfig)

assets = Environment(app)

manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    manager.run()

