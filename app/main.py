from app.config import BaseConfig
from app.app_factory import create_app

app = create_app(BaseConfig)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=app.config.get('APP_PORT', 8080), debug=app.config.get('DEBUG', False),
            ssl_context=app.config.get('SSL_CONTEXT', None))
