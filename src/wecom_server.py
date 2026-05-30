"""
WeCom (企业微信) Callback Server - FastAPI
"""
import asyncio
import logging
import time
import sys

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse

from .config import config
from .wecom_crypto import WXBizMsgCrypt
from .wecom_api import WeComAPI
from .message_handler import MessageHandler

logger = logging.getLogger(__name__)
start_time = time.time()

# Lazy init - fails gracefully if WeCom not configured
_crypto = None
_api = None
_handler = None


def _get_crypto():
    global _crypto
    if _crypto is None:
        _crypto = WXBizMsgCrypt(
            token=config.wecom.token,
            encoding_aes_key=config.wecom.aes_key,
            corp_id=config.wecom.corp_id,
        )
    return _crypto


def _get_api():
    global _api
    if _api is None:
        _api = WeComAPI()
    return _api


def _get_handler():
    global _handler
    if _handler is None:
        _handler = MessageHandler()
    return _handler


app = FastAPI(title="XiaoYue Bot", version="3.0.0")


@app.get("/")
async def index():
    uptime = int(time.time() - start_time)
    h, m = divmod(uptime // 60, 60)
    d, h = divmod(h, 24)
    handler = _get_handler()
    active = handler.human.is_active_now()
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head><meta charset="utf-8"><title>XiaoYue</title>
<style>
  body{{font-family:-apple-system,sans-serif;max-width:480px;margin:40px auto;padding:20px}}
  h1{{color:#e91e63}}.card{{background:#f5f5f5;border-radius:12px;padding:16px;margin:12px 0}}
  .on{{background:#c8e6c9;color:#2e7d32;padding:2px 8px;border-radius:4px;font-size:12px}}
  .off{{background:#ffcdd2;color:#c62828;padding:2px 8px;border-radius:4px;font-size:12px}}
</style></head>
<body>
<h1>XiaoYue Bot</h1>
<p>WeCom AI Girlfriend Bot</p>
<div class="card">
  <strong>Status:</strong> <span class="{'on' if active else 'off'}">{'ONLINE' if active else 'SLEEPING'}</span><br>
  <strong>Uptime:</strong> {d}d {h}h {m}m<br>
  <strong>Model:</strong> {config.ai.model}<br>
  <strong>Active:</strong> {config.human.active_hours_start}:00-{config.human.active_hours_end}:00<br>
  <strong>Reply rate:</strong> {config.human.reply_probability*100:.0f}%
</div>
<p style="color:#999;font-size:11px">Powered by DeepSeek AI · Railway</p>
</body></html>"""
    return HTMLResponse(html)


@app.get("/health")
async def health():
    return {"status": "ok", "uptime": int(time.time() - start_time)}


@app.get("/callback")
async def verify_callback(
    msg_signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...),
    echostr: str = Query(...),
):
    try:
        logger.info("URL verification request")
        crypto = _get_crypto()
        decrypted = crypto.verify_url(msg_signature, timestamp, nonce, echostr)
        logger.info("URL verification OK")
        return PlainTextResponse(decrypted)
    except Exception as e:
        logger.error("URL verification failed: %s", e)
        raise HTTPException(status_code=403, detail=str(e))


@app.post("/callback")
async def message_callback(
    request: Request,
    msg_signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...),
):
    try:
        body = await request.body()
        crypto = _get_crypto()
        msg = crypto.decrypt_message(msg_signature, timestamp, nonce, body)

        from_user = msg.get("FromUserName", "")
        msg_type = msg.get("MsgType", "")
        content = msg.get("Content", "")

        logger.info("MSG [%s] %s: %s", from_user[:16], msg_type, content[:60])

        asyncio.create_task(_process_and_reply(from_user, content))
        return PlainTextResponse("")

    except Exception as e:
        logger.error("Callback error: %s", e, exc_info=True)
        return PlainTextResponse("")


async def _process_and_reply(from_user: str, content: str) -> None:
    try:
        handler = _get_handler()
        api = _get_api()
        reply, user_id = handler.process_message(from_user, content)
        if reply:
            delay = handler.get_delay_for(len(content))
            logger.info("Wait %.1fs before reply to %s...", delay, from_user[:16])
            await asyncio.sleep(delay)
            success = api.send_text_safe(from_user, reply)
            if success:
                handler.record_reply_sent(from_user)
                logger.info("REPLY [->%s] %s", user_id[:16], reply[:50])
            else:
                logger.error("Send failed -> %s", from_user[:16])
        else:
            logger.info("Skip reply to %s", from_user[:16])
    except Exception as e:
        logger.error("Async reply error: %s", e, exc_info=True)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)],
    )
