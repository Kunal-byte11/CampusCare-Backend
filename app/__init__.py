from flask import Flask
from flask_cors import CORS
from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.routes.booking import booking_bp
    from app.routes.forum import forum_bp
    from app.routes.ai_chat import ai_chat_bp
    from app.routes.video_call import video_call_bp
    from app.routes.counselors import counselors_bp

    app.register_blueprint(booking_bp, url_prefix="/api/booking")
    app.register_blueprint(forum_bp, url_prefix="/api/forum")
    app.register_blueprint(ai_chat_bp, url_prefix="/api/ai")
    app.register_blueprint(video_call_bp, url_prefix="/api/video")
    app.register_blueprint(counselors_bp, url_prefix="/api/counselors")

    @app.route("/health")
    def health():
        return {"status": "ok", "service": "campuscare-backend"}, 200

    return app
