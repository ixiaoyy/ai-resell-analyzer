"""
多平台登录 + Cookies 导出工具 + 商品提取。

支持: 闲鱼 / 拼多多 / 1688

使用方法：
1. python export_cookies.py --platform xianyu    # 打开浏览器，手动登录闲鱼
2. python export_cookies.py --platform pinduoduo # 打开浏览器，手动登录拼多多
3. python export_cookies.py --platform 1688      # 打开浏览器，手动登录1688
4. python export_cookies.py --test                # 测试所有 cookies

登录成功后按 Enter，cookies 保存到 .cookies/ 目录。
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

COOKIES_DIR = Path(".cookies")
COOKIES_DIR.mkdir(exist_ok=True)

YEN = "\xa5"

PLATFORM_CONFIGS = {
    "xianyu": {
        "name": "闲鱼",
        "home_url": "https://www.goofish.com",
        "search_keyword": "收纳",
    },
    "pinduoduo": {
        "name": "拼多多",
        "home_url": "https://m.pinduoduo.com/",
        "search_keyword": "收纳盒",
    },
    "1688": {
        "name": "1688",
        "home_url": "https://www.1688.com",
        "search_keyword": "收纳箱",
    },
}


def export_cookies(platform: str) -> bool:
    """打开浏览器让用户手动登录，然后导出 cookies。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("错误: playwright 未安装")
        return False

    config = PLATFORM_CONFIGS.get(platform)
    if not config:
        print(f"未知平台: {platform}")
        return False

    cookies_file = COOKIES_DIR / f"{platform}_cookies.json"

    print(f"\n{'=' * 60}")
    print(f"导出 {config['name']} 的登录态 cookies")
    print(f"{'=' * 60}")
    print(f"请在打开的浏览器中完成登录。")
    print(f"登录成功后，按 Enter 继续...")
    print(f"要取消请按 Ctrl+C")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()

        page.goto(config["home_url"], timeout=60000)
        print(f"[{config['name']}] 当前 URL: {page.url}")

        print(f"\n[{config['name']}] 请完成登录后按 Enter ...")
        input()

        cookies = context.cookies()
        cookies_file.write_text(
            json.dumps(cookies, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print(f"\n  Cookies 已保存到: {cookies_file}")
        print(f"  共 {len(cookies)} 个 cookie")

        browser.close()

    return True


def load_cookies(platform: str) -> list[dict]:
    """加载已保存的 cookies。"""
    cookies_file = COOKIES_DIR / f"{platform}_cookies.json"
    if not cookies_file.exists():
        return []
    try:
        with open(cookies_file, encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"加载 cookies 失败: {exc}")
        return []


def test_with_cookies(platform: str) -> dict:
    """使用 cookies 测试抓取。"""
    cookies = load_cookies(platform)
    config = PLATFORM_CONFIGS.get(platform, {})
    keyword = config.get("search_keyword", "收纳")

    result = {
        "platform": platform,
        "name": config.get("name", platform),
        "raw_text_len": 0,
        "product_count": 0,
        "products": [],
        "error": None,
    }

    if not cookies:
        result["error"] = "未找到 cookies"
        return result

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        result["error"] = "playwright 未安装"
        return result

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1440, "height": 900},
                locale="zh-CN",
            )
            context.add_cookies(cookies)
            page = context.new_page()
            page.set_default_timeout(30000)

            if platform == "xianyu":
                url = f"https://www.goofish.com/search?q={keyword}"
            elif platform == "pinduoduo":
                url = f"https://m.pinduoduo.com/search?q={keyword}"
            elif platform == "1688":
                url = f"https://s.1688.com/youyuan/index.htm?keywords={keyword}"
            else:
                url = config.get("home_url", "")

            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            text = page.locator("body").inner_text(timeout=15000).strip()
            result["raw_text_len"] = len(text)

            if platform == "xianyu":
                result["products"] = _extract_xianyu_products(text)
            elif platform == "pinduoduo":
                result["products"] = _extract_pinduoduo_products(text)
            elif platform == "1688":
                result["products"] = _extract_1688_products(text)

            result["product_count"] = len(result["products"])

            browser.close()

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def _extract_xianyu_products(text: str) -> list[dict]:
    """从闲鱼页面文本提取商品。"""
    lines = text.splitlines()
    records = []

    skip_start = [
        "搜索", "综合", "新降价", "新发布", "价格", "区域", "确定",
        "个人闲置", "验货宝", "验号担保", "包邮", "超赞鱼小铺", "全新", "严选", "转卖",
        "订单", "发闲置", "消息", "APP", "反馈", "客服", "回顶部",
        "登录", "注册",
    ]
    skip_contains = [
        "许可证", "备案", "版权", "阿里", "淘宝", "天猫", "1688",
        "ICP", "广播电视", "集邮", "隐私政策", "用户协议", "算法备案",
        "公安网安", "软件许可", "推动绿色", "促进绿色", "废旧物资",
        "社会信用", "增值电信", "营业性演出", "统一社会信用",
    ]

    i = 0
    total_lines = len(lines)

    while i < total_lines and len(records) < 30:
        line = lines[i].strip()

        if line != YEN:
            i += 1
            continue

        # Found Yen line, extract price
        price_parts = []
        end_j = i + 4
        if end_j > total_lines:
            end_j = total_lines

        for j in range(i + 1, end_j):
            part = lines[j].strip()
            if not part:
                continue
            if re.match(r"^[\d.]+$", part):
                price_parts.append(part)
                if "." in part:
                    break
            else:
                break

        if not price_parts:
            i += 1
            continue

        price_str = "".join(price_parts)
        try:
            price = float(price_str)
        except ValueError:
            i += 1
            continue

        if price <= 0.5 or price > 9999:
            i += 1
            continue

        # Extract title - search backwards from Yen line
        title = ""
        start_search = i - 5
        if start_search < 0:
            start_search = 0

        for j in range(i - 1, start_search - 1, -1):
            if j < 0:
                break
            prev = lines[j].strip()
            if not prev:
                continue
            if prev in skip_start:
                continue
            if any(p in prev for p in skip_contains):
                continue
            if prev.startswith("tbNick_") or prev.startswith("http"):
                continue
            title = prev.strip(" :|")
            if len(title) >= 4:
                break
            title = ""

        if not title:
            i += 1
            continue

        # Extract "want" count
        want_count = None
        want_end = i + 5
        if want_end > total_lines:
            want_end = total_lines
        for j in range(i + 1, want_end):
            next_line = lines[j].strip()
            m = re.search(r"(\d+)\s*人想要", next_line)
            if m:
                want_count = int(m.group(1))
                break

        # Extract location
        location = None
        cities = ["北京", "上海", "广东", "浙江", "江苏", "四川", "湖北", "湖南", "河北", "河南",
                "山东", "福建", "安徽", "陕西", "辽宁", "吉林", "黑龙江", "江西", "云南", "贵州", "山西", "重庆", "天津"]
        loc_end = i + 8
        if loc_end > total_lines:
            loc_end = total_lines
        for j in range(i + 1, loc_end):
            loc = lines[j].strip()
            if loc in cities:
                location = loc
                break

        records.append({
            "title": title[:80],
            "price": price,
            "want_count": want_count,
            "location": location,
        })

        i += 1

    return records


def _extract_pinduoduo_products(text: str) -> list[dict]:
    """从拼多多页面文本提取商品。"""
    return []


def _extract_1688_products(text: str) -> list[dict]:
    """从1688页面文本提取商品。"""
    return []


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="多平台登录态导出工具")
    parser.add_argument(
        "--platform", "-p",
        choices=["xianyu", "pinduoduo", "1688", "all"],
        default="all",
        help="选择平台",
    )
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="使用现有 cookies 测试抓取",
    )
    args = parser.parse_args()

    if args.test:
        platforms = ["xianyu", "pinduoduo", "1688"]
    elif args.platform == "all":
        platforms = ["xianyu", "pinduoduo", "1688"]
    else:
        platforms = [args.platform]

    if not args.test:
        for p in platforms:
            export_cookies(p)

    print("\n" + "=" * 60)
    print("测试抓取结果")
    print("=" * 60)

    for p in platforms:
        r = test_with_cookies(p)
        status = "OK" if r["error"] is None and r["product_count"] > 0 else "WAIT"
        print(f"\n{status} [{r['name']}] ({p})")
        print(f"  文本长度: {r['raw_text_len']}")
        print(f"  商品数:   {r['product_count']}")
        print(f"  错误:     {r['error'] or 'none'}")

        if r["products"]:
            print(f"  前5个商品:")
            for prod in r["products"][:5]:
                want = f", {prod.get('want_count', '?')}人想要" if prod.get("want_count") else ""
                loc = f", {prod.get('location', '')}" if prod.get("location") else ""
                print(f"    - {prod['title'][:40]} | Y{prod['price']}{want}{loc}")

    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())