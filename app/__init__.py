from flask import Flask, jsonify
from werkzeug.security import generate_password_hash

from .config import Config
from .repositories.supabase import SupabaseConfigError


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    _init_repositories(app)
    _init_services(app)
    _register_blueprints(app)
    _init_default_admin(app)
    _register_error_handlers(app)
    _register_template_filters(app)

    return app


def _init_repositories(app: Flask) -> None:
    from .repositories.supabase import (
        SupabaseUserRepository,
        SupabaseCategoryRepository,
        SupabaseMenuItemRepository,
        SupabaseOrderRepository,
        SupabaseOrderItemRepository,
        SupabaseSettingRepository,
    )
    app.user_repo = SupabaseUserRepository()
    app.category_repo = SupabaseCategoryRepository()
    app.menu_item_repo = SupabaseMenuItemRepository()
    app.order_repo = SupabaseOrderRepository()
    app.order_item_repo = SupabaseOrderItemRepository()
    app.settings_repo = SupabaseSettingRepository()


def _init_services(app: Flask) -> None:
    from .services import AuthService, POSService, MenuService, ReportService
    app.auth_service = AuthService(app.user_repo)
    app.pos_service = POSService(
        order_repo=app.order_repo,
        order_item_repo=app.order_item_repo,
        menu_item_repo=app.menu_item_repo,
        category_repo=app.category_repo,
        settings_repo=app.settings_repo,
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
    from .routes.auth import auth_bp
    from .routes.pos import pos_bp
    from .routes.menu import menu_bp
    from .routes.reports import reports_bp
    from .routes.settings import settings_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)


def _init_default_admin(app: Flask) -> None:
    try:
        with app.app_context():
            if not app.config.get("SUPABASE_URL") or not app.config.get("SUPABASE_KEY"):
                return
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


def _register_template_filters(app: Flask) -> None:
    @app.template_filter("kyat")
    def kyat_filter(value):
        if value is None:
            return "---"
        try:
            num = int(round(float(value)))
            return "Ks " + "{:,}".format(num)
        except (ValueError, TypeError):
            return "---"


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(SupabaseConfigError)
    def handle_supabase_config_error(e):
        return jsonify({"error": str(e)}), 500

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({"error": "Internal server error"}), 500
