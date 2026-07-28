#!/usr/bin/env python3
"""Validate a binbinskill project.json using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


ID_PATTERNS = {
    "beat": re.compile(r"^B\d{2,}$"),
    "shot": re.compile(r"^S\d{2,}$"),
    "clip": re.compile(r"^C\d{2,}$"),
    "asset": re.compile(r"^A-[A-Z]+-\d{2,}$"),
    "dialogue": re.compile(r"^D\d{3,}$"),
}
STATUSES = {"planned", "prompt_ready", "generated", "accepted", "rejected", "post_fix"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验 binbinskill 项目状态JSON")
    parser.add_argument("project", type=Path, help="project.json 路径")
    parser.add_argument("--json-output", action="store_true", help="以JSON输出检查结果")
    return parser.parse_args()


def load_project(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("项目根节点必须是对象")
    return data


def validate(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    def require_text(obj: dict, field: str, where: str) -> None:
        if not isinstance(obj.get(field), str) or not obj[field].strip():
            errors.append(f"{where}: 缺少非空字段 {field}")

    for field in ("schema_version", "project_id", "title", "aspect_ratio", "platform"):
        require_text(data, field, "project")

    collections = {}
    for field in ("assets", "beats", "shots", "clips"):
        value = data.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"project: {field} 必须是非空数组")
            value = []
        collections[field] = value

    dialogues = data.get("source_dialogue", [])
    if not isinstance(dialogues, list):
        errors.append("project: source_dialogue 必须是数组")
        dialogues = []

    def index(items: list, kind: str) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for pos, item in enumerate(items, 1):
            where = f"{kind}[{pos}]"
            if not isinstance(item, dict):
                errors.append(f"{where}: 必须是对象")
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not ID_PATTERNS[kind].match(item_id):
                errors.append(f"{where}: ID格式错误: {item_id!r}")
                continue
            if item_id in result:
                errors.append(f"{where}: ID重复: {item_id}")
            result[item_id] = item
        return result

    asset_map = index(collections["assets"], "asset")
    beat_map = index(collections["beats"], "beat")
    shot_map = index(collections["shots"], "shot")
    clip_map = index(collections["clips"], "clip")
    dialogue_map = index(dialogues, "dialogue") if dialogues else {}

    for beat_id, beat in beat_map.items():
        for field in ("goal", "obstacle", "attempt", "actual_result", "value_change"):
            require_text(beat, field, beat_id)
        budget = beat.get("budget_s")
        if not isinstance(budget, (int, float)) or budget <= 0:
            warnings.append(f"{beat_id}: budget_s 未设置为正数")

    dialogue_use: Counter[str] = Counter()
    schema_version = data.get("schema_version")
    require_viewpoint_contract = schema_version in {"2.1", "2.2"}
    require_prompt_bible_contract = schema_version == "2.2"
    for shot_id, shot in shot_map.items():
        beat_id = shot.get("beat_id")
        if beat_id not in beat_map:
            errors.append(f"{shot_id}: beat_id 不存在: {beat_id!r}")
        for field in (
            "visual_task", "director_intent", "shot_design", "blocking_axis",
            "primary_action", "camera_move", "start_state", "end_state",
            "entry_anchor", "exit_anchor",
        ):
            require_text(shot, field, shot_id)
        if require_viewpoint_contract:
            for field in (
                "viewpoint_type", "viewpoint_owner", "camera_story_identity",
                "gaze_target", "viewpoint_evidence",
            ):
                require_text(shot, field, shot_id)
        duration = shot.get("duration_s")
        if not isinstance(duration, (int, float)) or duration <= 0:
            errors.append(f"{shot_id}: duration_s 必须为正数")
        for asset_id in shot.get("asset_ids", []):
            if asset_id not in asset_map:
                errors.append(f"{shot_id}: 引用了不存在的资产 {asset_id}")
        for dialogue_id in shot.get("dialogue_ids", []):
            dialogue_use[dialogue_id] += 1
            if dialogue_id not in dialogue_map:
                errors.append(f"{shot_id}: 引用了不存在的对白 {dialogue_id}")

    for dialogue_id, dialogue in dialogue_map.items():
        count = dialogue_use[dialogue_id]
        if dialogue.get("preserve", False) and count != 1:
            errors.append(f"{dialogue_id}: 要求保留的对白应覆盖一次，当前 {count} 次")
        elif count > 1:
            warnings.append(f"{dialogue_id}: 被多个Shot重复引用 {count} 次")

    shot_clip_use: Counter[str] = Counter()
    max_duration = data.get("platform_profile", {}).get("max_clip_duration_s")
    for clip_id, clip in clip_map.items():
        shot_ids = clip.get("shot_ids")
        if not isinstance(shot_ids, list) or not shot_ids:
            errors.append(f"{clip_id}: shot_ids 必须是非空数组")
            shot_ids = []
        for shot_id in shot_ids:
            shot_clip_use[shot_id] += 1
            if shot_id not in shot_map:
                errors.append(f"{clip_id}: 引用了不存在的Shot {shot_id}")
        for field in ("mode", "must_happen", "must_not_happen", "prompt_version", "status"):
            require_text(clip, field, clip_id)
        if require_prompt_bible_contract:
            require_text(clip, "final_frame", clip_id)
            reference_schedule = clip.get("reference_schedule")
            if not isinstance(reference_schedule, list) or not reference_schedule:
                errors.append(f"{clip_id}: reference_schedule 必须是非空数组")
            else:
                for pos, item in enumerate(reference_schedule, 1):
                    where = f"{clip_id}.reference_schedule[{pos}]"
                    if not isinstance(item, dict):
                        errors.append(f"{where}: 必须是对象")
                        continue
                    for field in ("asset_id", "role", "active_range"):
                        require_text(item, field, where)
                    if item.get("asset_id") not in asset_map:
                        errors.append(f"{where}: 引用了不存在的资产 {item.get('asset_id')}")
            timeline = clip.get("timeline")
            if not isinstance(timeline, list) or not timeline:
                errors.append(f"{clip_id}: timeline 必须是非空数组")
            else:
                for pos, item in enumerate(timeline, 1):
                    where = f"{clip_id}.timeline[{pos}]"
                    if not isinstance(item, dict):
                        errors.append(f"{where}: 必须是对象")
                        continue
                    for field in (
                        "range", "shot_id", "subject_space", "action_phase",
                        "viewpoint_camera", "sound", "end_state",
                    ):
                        require_text(item, field, where)
                    if item.get("shot_id") not in shot_map:
                        errors.append(f"{where}: 引用了不存在的Shot {item.get('shot_id')}")
            constraints = clip.get("stability_constraints")
            if not isinstance(constraints, list):
                errors.append(f"{clip_id}: stability_constraints 必须是数组")
            elif len(constraints) > 3:
                errors.append(f"{clip_id}: stability_constraints 不得超过3条")
            elif any(not isinstance(item, str) or not item.strip() for item in constraints):
                errors.append(f"{clip_id}: stability_constraints 必须全部为非空文本")
        if clip.get("status") not in STATUSES:
            errors.append(f"{clip_id}: 非法状态 {clip.get('status')!r}")
        duration = clip.get("duration_s")
        if not isinstance(duration, (int, float)) or duration <= 0:
            errors.append(f"{clip_id}: duration_s 必须为正数")
        else:
            internal = sum(
                shot_map[s].get("duration_s", 0)
                for s in shot_ids if s in shot_map and isinstance(shot_map[s].get("duration_s"), (int, float))
            )
            if abs(internal - duration) > 0.25:
                errors.append(f"{clip_id}: 内部Shot时长 {internal:g}s 与Clip时长 {duration:g}s 不一致")
            if isinstance(max_duration, (int, float)) and duration > max_duration:
                errors.append(f"{clip_id}: 时长 {duration:g}s 超过平台上限 {max_duration:g}s")
        if clip.get("status") == "accepted" and not clip.get("actual_end_state"):
            errors.append(f"{clip_id}: accepted 状态必须记录 actual_end_state")

    for shot_id in shot_map:
        count = shot_clip_use[shot_id]
        if count == 0:
            errors.append(f"{shot_id}: 未分配到任何Clip")
        elif count > 1:
            errors.append(f"{shot_id}: 被重复分配到 {count} 个Clip")

    if data.get("platform") != "neutral":
        profile = data.get("platform_profile", {})
        if not profile.get("last_verified"):
            warnings.append("指定了生成平台，但 platform_profile.last_verified 为空")

    return errors, warnings


def main() -> int:
    args = parse_args()
    try:
        data = load_project(args.project)
        errors, warnings = validate(data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors, warnings = [str(exc)], []

    result = {"valid": not errors, "errors": errors, "warnings": warnings}
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("VALID" if result["valid"] else "INVALID")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARN: {item}")
        print(f"errors={len(errors)} warnings={len(warnings)}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
