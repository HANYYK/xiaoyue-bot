#!/usr/bin/env python3
"""
XiaoYue - WeCom AI Girlfriend Bot
Powered by DeepSeek AI

Deploy: Railway, Render, or any cloud platform.
Local: python main.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import config
from src.wecom_server import app, setup_logging


def main():
    setup_logging()

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))

    print()
    print("=" * 50)
    print("  XiaoYue - WeCom AI Girlfriend Bot v3")
    print("  Powered by DeepSeek AI")
    print("=" * 50)
    print()
    print(f"  Local:  http://localhost:{port}")
    print(f"  Status: http://localhost:{port}/")
    print(f"  Health: http://localhost:{port}/health")
    print()

    if not config.wecom.corp_id:
        print("  WARN: WECOM_CORP_ID not set - callbacks won't work")
    if not config.wecom.token or not config.wecom.aes_key:
        print("  WARN: WECOM_TOKEN/WECOM_AES_KEY not set")
    if config.wecom.allowed_user:
        print(f"  Only replying to: {config.wecom.allowed_user}")
    print()

    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
