"""维基百科查询工具。

中文优先，失败自动回退英文。
代理优先级：127.0.0.1:10808 → 系统代理 → 直连。
"""

import re
import urllib.request
from functools import lru_cache
import requests
from tools.base import Tool
from config import WIKIPEDIA_TIMEOUT, WIKIPEDIA_PROXY

_HEADERS = {
    "User-Agent": "MiniAgent/1.0 (Educational Project)"
}


def _build_proxies_list():
    """构建代理列表，优先级：.env 手动配置 → 系统(IE)代理 → 直连。"""
    proxies = []

    # 1. 手动配置（.env 中的 WIKIPEDIA_PROXY）
    if WIKIPEDIA_PROXY:
        proxies.append({"http": WIKIPEDIA_PROXY, "https": WIKIPEDIA_PROXY})

    # 2. 自动读取系统（IE）代理
    try:
        sys_proxies = urllib.request.getproxies()
        proxy_url = sys_proxies.get("https") or sys_proxies.get("http")
        if proxy_url and {"http": proxy_url, "https": proxy_url} not in proxies:
            proxies.append({"http": proxy_url, "https": proxy_url})
    except Exception:
        pass

    # 3. 直连兜底
    proxies.append(None)
    return proxies

_PROXIES_LIST = _build_proxies_list()


def _get(url: str, params: dict) -> requests.Response | None:
    """依次尝试代理，返回第一个成功的响应，全部失败返回 None。"""
    for proxies in _PROXIES_LIST:
        try:
            r = requests.get(
                url, params=params, headers=_HEADERS,
                proxies=proxies, timeout=WIKIPEDIA_TIMEOUT
            )
            return r
        except Exception:
            continue
    return None


@lru_cache(maxsize=256)
def _query(lang: str, title: str) -> str | None:
    """
    用 MediaWiki API 查询词条介绍段落（纯文本）。
    找到返回文字，未找到返回 None，出错返回 None。
    """
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "exintro": 1,
        "explaintext": 1,
        "redirects": 1,
        "format": "json",
        "titles": title,
    }
    r = _get(url, params)
    if r is None or r.status_code != 200:
        return None

    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if page.get("pageid", -1) == -1:  # 词条不存在
            return None
        extract = page.get("extract", "").strip()
        if extract:
            # 去掉多余空行，限制 600 字
            extract = re.sub(r"\n{3,}", "\n\n", extract)
            return extract[:600]
    return None


class WikipediaTool(Tool):
    name = "wikipedia"
    description = "查询维基百科。输入一个查询词，返回该词条的摘要。"
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "查询词，如 '爱因斯坦' 或 'Alan Turing'"
            }
        },
        "required": ["query"],
    }

    def run(self, query: str) -> str:
        # 1. 中文 Wikipedia
        result = _query("zh", query)
        if result:
            return result

        # 2. 英文 Wikipedia
        result = _query("en", query)
        if result:
            return result

        return f"Error: 未找到「{query}」相关词条"
