"""게시글 본문에 쓰는 아주 작은 마크다운 문법을 안전한 HTML로 바꿔주는 함수.

전문 마크다운 라이브러리(markdown, mistune 등)를 새로 추가하는 대신, 지원할 문법 몇 개만
골라서 직접 변환하기로 했다. 이유는 두 가지: (1) 패키지를 하나 더 늘리고 싶지 않았고,
(2) "사용자가 입력한 텍스트를 그대로 HTML로 바꿔서 보여준다"는 기능은 잘못 만들면
XSS(악성 스크립트 삽입) 구멍이 생기기 딱 좋은데, 직접 만들면 어떤 문법을 어떤 태그로만
바꾸는지 전부 내가 통제할 수 있어서 오히려 더 믿음이 갔다.

원칙은 간단하다: 사용자가 실제로 타이핑한 텍스트 조각은 태그로 감싸기 직전에 항상
html.escape()를 거친다. 그래서 사용자가 본문에 <script>alert(1)</script> 같은 걸
그대로 입력해도, 화면에는 그 글자 그대로("&lt;script&gt;...")만 보이고 실제로
실행되는 일은 없다. 우리가 만든 <strong>, <h1> 같은 태그만 진짜 태그로 남는다.
"""
import html
import re

_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_BOLD_RE = re.compile(r"\*\*([^*\n]+)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_LINK_RE = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")
_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$")
_UL_RE = re.compile(r"^[-*]\s+(.*)$")
_OL_RE = re.compile(r"^\d+\.\s+(.*)$")
_QUOTE_RE = re.compile(r"^>\s?(.*)$")


def _safe_href(raw_url: str):
    """http(s)로 시작하는 주소만 링크로 허용한다. javascript: 같은 위험한 스킴은 걸러낸다."""
    if raw_url.startswith("http://") or raw_url.startswith("https://"):
        return raw_url
    return None


def _inline(escaped_text: str) -> str:
    """이미 html.escape()가 끝난 한 줄짜리 텍스트에 굵게/기울임/코드/링크 문법을 입힌다."""
    text = _BOLD_RE.sub(r"<strong>\1</strong>", escaped_text)
    text = _ITALIC_RE.sub(r"<em>\1</em>", text)
    text = _INLINE_CODE_RE.sub(r"<code>\1</code>", text)

    def _link_sub(m):
        label, escaped_url = m.group(1), m.group(2)
        safe_url = _safe_href(html.unescape(escaped_url))
        if safe_url is None:
            return m.group(0)  # 안전하지 않은 링크면 링크로 안 만들고 원래 글자 그대로 둔다
        return f'<a href="{html.escape(safe_url, quote=True)}" target="_blank" rel="noopener noreferrer">{label}</a>'

    return _LINK_RE.sub(_link_sub, text)


def render_markdown(raw_text: str) -> str:
    """게시글 본문(마크다운 문법이 섞인 일반 텍스트)을 안전한 HTML 문자열로 바꾼다."""
    lines = (raw_text or "").replace("\r\n", "\n").split("\n")

    parts = []
    paragraph_lines = []
    list_items = []
    list_tag = None
    in_code_block = False
    code_lines = []

    def flush_paragraph():
        if paragraph_lines:
            joined = "<br>".join(_inline(html.escape(line)) for line in paragraph_lines)
            parts.append(f"<p>{joined}</p>")
            paragraph_lines.clear()

    def flush_list():
        nonlocal list_tag
        if list_items:
            items_html = "".join(f"<li>{_inline(html.escape(item))}</li>" for item in list_items)
            parts.append(f"<{list_tag}>{items_html}</{list_tag}>")
            list_items.clear()
            list_tag = None

    for line in lines:
        stripped = line.strip()

        if stripped == "```":
            if in_code_block:
                parts.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code_block = False
            else:
                flush_paragraph()
                flush_list()
                in_code_block = True
            continue
        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        heading_match = _HEADING_RE.match(stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            parts.append(f"<h{level}>{_inline(html.escape(heading_match.group(2)))}</h{level}>")
            continue

        quote_match = _QUOTE_RE.match(stripped)
        if quote_match:
            flush_paragraph()
            flush_list()
            parts.append(f"<blockquote>{_inline(html.escape(quote_match.group(1)))}</blockquote>")
            continue

        ul_match = _UL_RE.match(stripped)
        ol_match = None if ul_match else _OL_RE.match(stripped)
        if ul_match or ol_match:
            flush_paragraph()
            wanted_tag = "ul" if ul_match else "ol"
            if list_tag and list_tag != wanted_tag:
                flush_list()
            list_tag = wanted_tag
            list_items.append((ul_match or ol_match).group(1))
            continue

        flush_list()
        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    if in_code_block and code_lines:
        parts.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")

    return "\n".join(parts)
