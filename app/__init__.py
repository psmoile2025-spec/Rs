from flask import Flask

from .config import Config
from .repositories.supabase import (
    SupabaseUserRepository,
    SupabaseCategoryRepository,
    SupabaseMenuItemRepository,
    SupabaseOrderRepository,
    SupabaseOrderItemRepository,
)
from werkzeug.security import generate_password_hash
from .services import AuthService, POSService, MenuService, ReportService
from .routes.auth import auth_bp
from .routes.pos import pos_bp
from .routes.menu import menu_bp
from .routes.reports import reports_bp


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    _init_repositories(app)
    _init_services(app)
    _register_blueprints(app)
    _init_default_admin(app)

    return app


def _init_repositories(app: Flask) -> None:
    app.user_repo = SupabaseUserRepository()
    app.category_repo = SupabaseCategoryRepository()
    app.menu_item_repo = SupabaseMenuItemRepository()
    app.order_repo = SupabaseOrderRepository()
    app.order_item_repo = SupabaseOrderItemRepository()


def _init_services(app: Flask) -> None:
    app.auth_service = AuthService(app.user_repo)
    app.pos_service = POSService(
        order_repo=app.order_repo,
        order_item_repo=app.order_item_repo,
        menu_item_repo=app.menu_item_repo,
        category_repo=app.category_repo,
        tax_rate=app.config["TAX_RATE"],
    )
    app.menu_service = MenuService(
        category_repo=app.category_repo,
        menu_item_repo=app.menu_item_repo,
    )
    app.report_service = ReportService(
        order_repo=app.order_repo,
        order_item_repo=app.order_item_repo,
        menu_item_repo=app.menu_item_repo,
    )


def _register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(reports_bp)


def _init_default_admin(app: Flask) -> None:
    try:
        with app.app_context():
            repo = app.user_repo
            email = app.config["DEFAULT_ADMIN_EMAIL"]
            password = app.config["DEFAULT_ADMIN_PASSWORD"]
            hashed = generate_password_hash(password)
            existing = repo.get_by_email(email)
            if existing:
                repo.update(existing.id, password_hash=hashed)
            else:
                repo.create(email, hashed, "Admin")
    except Exception as e:
        import logging
        logging.warning("Could not initialize admin user: %s", e)
