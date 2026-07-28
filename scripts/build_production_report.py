#!/usr/bin/env python3
"""Build a standalone Chinese HTML production report from project.json."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 binbinskill HTML生产报告")
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def esc(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    return html.escape(str(value))


def table(title: str, columns: list[tuple[str, str]], rows: list[dict]) -> str:
    head = "".join(f"<th>{esc(label)}</th>" for _, label in columns)
    body = []
    for row in rows:
        cells = "".join(f"<td>{esc(row.get(key, ''))}</td>" for key, _ in columns)
        body.append(f"<tr>{cells}</tr>")
    empty = f'<tr><td colspan="{len(columns)}">暂无数据</td></tr>'
    return f'<h2>{esc(title)}</h2><div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body) or empty}</tbody></table></div>'


def build_content(data: dict) -> str:
    cards = [
        ("项目ID", data.get("project_id")),
        ("画幅", data.get("aspect_ratio")),
        ("目标时长", f'{data.get("target_duration_s", "")} 秒'),
        ("平台", data.get("platform")),
    ]
    parts = ['<div class="cards">' + "".join(f'<div class="card"><b>{esc(k)}</b>{esc(v)}</div>' for k, v in cards) + "</div>"]
    facts = data.get("immutable_facts", [])
    if facts:
        parts.append("<h2>不可改变事实</h2><ul>" + "".join(f"<li>{esc(x)}</li>" for x in facts) + "</ul>")
    parts.append(table("资产", [("id", "Asset ID"), ("type", "类型"), ("name", "名称"), ("primary_role", "主要用途"), ("hard_locks", "硬锁定"), ("valid_range", "有效时段")], data.get("assets", [])))
    parts.append(table("剧情节拍", [("id", "Beat"), ("goal", "目标"), ("obstacle", "障碍"), ("attempt", "尝试"), ("actual_result", "结果"), ("value_change", "价值变化"), ("budget_s", "预算秒数")], data.get("beats", [])))
    parts.append(table("镜头", [("id", "Shot"), ("beat_id", "Beat"), ("duration_s", "秒"), ("visual_task", "画面任务"), ("director_intent", "导演意图"), ("shot_design", "景别机位"), ("primary_action", "主体动作"), ("camera_move", "主运镜"), ("exit_anchor", "出口锚点")], data.get("shots", [])))
    parts.append(table("生成片段", [("id", "Clip"), ("shot_ids", "Shot顺序"), ("mode", "模式"), ("duration_s", "秒"), ("prompt_version", "版本"), ("status", "状态"), ("must_happen", "必须发生"), ("must_not_happen", "不得发生"), ("actual_end_state", "实际终点")], data.get("clips", [])))
    parts.append(table("对白覆盖", [("id", "对白ID"), ("speaker", "说话人"), ("text", "内容"), ("preserve", "必须保留")], data.get("source_dialogue", [])))
    return "\n".join(parts)


def main() -> int:
    args = parse_args()
    with args.project.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    template_path = Path(__file__).resolve().parent.parent / "assets" / "production-report-template.html"
    template = template_path.read_text(encoding="utf-8")
    title = f'binbinskill生产报告｜{data.get("title", "未命名项目")}'
    page = template.replace("{{TITLE}}", esc(title))
    page = page.replace("{{GENERATED_AT}}", esc(datetime.now().astimezone().isoformat(timespec="seconds")))
    page = page.replace("{{CONTENT}}", build_content(data))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page, encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
