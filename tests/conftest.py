import os

os.environ.setdefault("ENVIRONMENT", "test" if False else "dev")
os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/datilera_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("MEDIA_DIR", "tmp/test-media")
os.environ.setdefault("PDF_DIR", "tmp/test-pdfs")
os.environ.setdefault("STATIC_DIR", "app/interfaces/web/static")
os.environ.setdefault("TEMPLATES_DIR", "app/interfaces/web/templates")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("JWT_SECRET", "test-secret-with-at-least-thirty-two-characters")
