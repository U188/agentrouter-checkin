#!/usr/bin/env python3
"""agentrouter.org 自动签到 - GitHub Actions 版（沿用 AnyRouter 成熟方案）"""
import os, sys, json, time
import requests
import traceback
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

SITE_URL = os.getenv("SITE_URL", "https://agentrouter.org")
SESSION  = os.getenv("SESSION", "")       # 登录后 cookie 的 session 值
USER_ID  = os.getenv("USER_ID", "")       # 用户ID（可选，动态获取）
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID   = os.getenv("TG_CHAT_ID", "")
SESSION_TTL_DAYS = 30
SESSION_THRESHOLD_DAYS = 3
WAF_COOKIE_NAMES = ["acw_tc", "cdn_sec_tc", "acw_sc__v2"]
DOMAIN = SITE_URL.replace("https://","").replace("http://","").split("/")[0]

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"

def log(level, msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}", flush=True)

def send_tg(message):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        log("WARN", "TG 未配置，跳过")
        print(f"--- 消息 ---\n{message}\n----------")
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                      json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=30)
        log("INFO", "TG 发送成功")
    except Exception as e:
        log("ERROR", f"TG 失败: {e}")

def get_waf_cookies():
    """Playwright 访问登录页，尝试拿 WAF 放行 cookie (acw_sc__v2 等)"""
    log("INFO", f"Playwright 获取 WAF cookie: {SITE_URL}/login")
    waf={}
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--disable-blink-features=AutomationControlled"])
        ctx=b.new_context(viewport={"width":1280,"height":720}, user_agent=UA)
        page=ctx.new_page()
        page.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        try:
            page.goto(f"{SITE_URL}/login", wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            log("WARN", f"访问登录页失败: {e}")
        # 等待 WAF JS 生成 cookie
        for _ in range(4):
            page.wait_for_timeout(2500)
            for c in ctx.cookies():
                if c["name"] in WAF_COOKIE_NAMES and c.get("value"):
                    waf[c["name"]]=c["value"]
            if waf:
                break
        b.close()
    if waf:
        log("INFO", f"获取到 WAF cookie: {list(waf.keys())}")
    else:
        log("WARN", "未获取到 WAF cookie（可能滑块强制）")
    return waf

def build_headers(sid):
    h={
        "User-Agent":UA,
        "Accept":"application/json, text/plain, */*",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Referer":SITE_URL,"Origin":SITE_URL,
        "X-Requested-With":"XMLHttpRequest",
    }
    if sid is not None:
        h["new-api-user"]=str(sid)
    return h

def get_user_info(sess, headers):
    try:
        r=sess.get(f"{SITE_URL}/api/user/self", headers=headers, timeout=30)
        if r.headers.get("content-type","").startswith("text/html"):
            log("WARN", f"self 返回 WAF HTML (HTTP {r.status_code})")
            return None
        d=r.json()
        if d.get("success"):
            ud=d.get("data",{})
            return {"quota":ud.get("quota",0),"used":ud.get("used_quota",0),
                    "username":ud.get("username",""),"id":ud.get("id",0),"raw":ud}
        log("WARN", f"self 非成功: {d}")
    except Exception as e:
        log("WARN", f"self 异常: {e}")
    return None

def do_checkin(sess, headers):
    try:
        r=sess.post(f"{SITE_URL}/api/user/checkin", headers=headers, timeout=30)
        if r.headers.get("content-type","").startswith("text/html"):
            log("WARN", "checkin 返回 WAF HTML")
            return "WAF"
        d=r.json()
        log("INFO", f"checkin 响应: {json.dumps(d, ensure_ascii=False)[:300]}")
        if d.get("success"):
            return "SUCCESS"
        msg=str(d.get("message",""))
        if any(k in msg for k in ["已经签到","已签到","重复签到","already"]):
            return "DONE"
        return f"FAIL:{msg}"
    except Exception as e:
        log("ERROR", f"checkin 异常: {e}")
        return f"ERR:{e}"

def run():
    log("INFO","="*40)
    log("INFO","agentrouter 自动签到启动")
    if not SESSION:
        log("ERROR","SESSION 未配置")
        send_tg("❌ agentrouter 签到失败：SESSION 未配置")
        return 1

    waf=get_waf_cookies()
    sess=requests.Session()
    for n,v in waf.items():
        sess.cookies.set(n,v,domain=DOMAIN,path="/")
    sess.cookies.set("session",SESSION,domain=DOMAIN,path="/")
    if USER_ID:
        sess.cookies.set("user_id",USER_ID,domain=DOMAIN,path="/")

    headers=build_headers(None)
    ui=get_user_info(sess,headers)
    if not ui:
        log("ERROR","API 验证失败：WAF 滑块未通过 或 session 过期")
        send_tg("❌ agentrouter 签到失败：WAF 滑块未通过 / session 过期，需手动过滑块")
        return 1
    log("INFO",f"登录成功: {ui['username']} (id={ui['id']})")
    sid=ui["id"]
    headers=build_headers(sid)

    res=do_checkin(sess, headers)
    log("INFO",f"签到结果: {res}")
    send_tg(f"🎁 agentrouter 签到\n👤 {ui['username']} (id={sid})\n📋 {res}")
    log("INFO","执行完毕")
    return 0

def main():
    try:
        return run()
    except Exception as e:
        log("ERROR", f"{type(e).__name__}: {e}")
        traceback.print_exc()
        send_tg(f"❌ agentrouter 脚本异常\n📝 {type(e).__name__}: {e}")
        return 1

if __name__=="__main__":
    sys.exit(main())
