#!/usr/bin/env python3
"""Read-only audit for a local ToonFlow project and script."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit ToonFlow prompt, track, asset, and file consistency.")
    parser.add_argument("--db", required=True, type=Path, help="Path to db2.sqlite")
    parser.add_argument("--project-id", required=True, type=int)
    parser.add_argument("--script-id", required=True, type=int)
    parser.add_argument("--unit", type=int, help="Only audit this storyboard index")
    parser.add_argument("--contains", action="append", default=[], help="Text that must exist in both prompt layers")
    parser.add_argument("--direct-video", action="store_true", help="Require shouldGenerateImage=0")
    parser.add_argument("--oss-root", type=Path, help="Override media root; defaults to DB sibling oss directory")
    return parser.parse_args()


def numeric(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def resolve_media_path(oss_root: Path, file_path: str | None) -> Path | None:
    if not file_path or file_path.startswith(("http://", "https://")):
        return None
    return oss_root / Path(file_path.lstrip("/\\"))


def main() -> int:
    args = parse_args()
    db_path = args.db.expanduser().resolve()
    if not db_path.is_file():
        print(f"ERROR database not found: {db_path}")
        return 2

    oss_root = (args.oss_root or db_path.parent / "oss").expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    connection = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        project = connection.execute(
            "select id,name,videoRatio,videoModel from o_project where id=?",
            (args.project_id,),
        ).fetchone()
        script = connection.execute(
            "select id,name,projectId from o_script where id=?",
            (args.script_id,),
        ).fetchone()
        if not project:
            errors.append(f"project {args.project_id} not found")
        if not script:
            errors.append(f"script {args.script_id} not found")
        elif script["projectId"] != args.project_id:
            errors.append(f"script {args.script_id} belongs to project {script['projectId']}")
        if errors:
            for message in errors:
                print(f"ERROR {message}")
            return 1

        params: list[object] = [args.project_id, args.script_id]
        unit_filter = ""
        if args.unit is not None:
            unit_filter = " and s.`index`=?"
            params.append(args.unit)
        rows = connection.execute(
            f"""
            select s.id storyboardId,s.`index` unitIndex,s.trackId,s.prompt storyboardPrompt,
                   s.videoDesc,s.duration storyboardDuration,s.state storyboardState,
                   s.shouldGenerateImage,s.filePath storyboardFilePath,
                   t.prompt trackPrompt,t.duration trackDuration,t.state trackState,
                   t.videoId,t.selectVideoId,t.reason trackReason
            from o_storyboard s
            left join o_videoTrack t on t.id=s.trackId
            where s.projectId=? and s.scriptId=?{unit_filter}
            order by s.`index`
            """,
            params,
        ).fetchall()
        if not rows:
            errors.append("no matching storyboards")

        indexes = [row["unitIndex"] for row in rows]
        if len(indexes) != len(set(indexes)):
            errors.append("duplicate storyboard indexes")

        print(
            f"PROJECT {project['id']} {project['name']} ratio={project['videoRatio']} "
            f"model={project['videoModel']}"
        )
        print(f"SCRIPT {script['id']} {script['name']} units={len(rows)}")

        all_bound_asset_ids: set[int] = set()
        for row in rows:
            label = f"U{row['unitIndex']:02d}"
            if row["trackPrompt"] is None:
                errors.append(f"{label} missing video track {row['trackId']}")
                continue
            if row["videoDesc"] != row["trackPrompt"]:
                errors.append(f"{label} videoDesc and video-track prompts differ")
            if args.direct_video and row["storyboardPrompt"] != row["trackPrompt"]:
                errors.append(f"{label} direct-video storyboard and video-track prompts differ")
            if numeric(row["storyboardDuration"]) != numeric(row["trackDuration"]):
                errors.append(
                    f"{label} duration differs: storyboard={row['storyboardDuration']} track={row['trackDuration']}"
                )
            if args.direct_video and row["shouldGenerateImage"] != 0:
                errors.append(f"{label} shouldGenerateImage={row['shouldGenerateImage']}, expected 0")
            for phrase in args.contains:
                prompt_layers = [row["videoDesc"] or "", row["trackPrompt"] or ""]
                if args.direct_video:
                    prompt_layers.append(row["storyboardPrompt"] or "")
                if any(phrase not in layer for layer in prompt_layers):
                    errors.append(f"{label} required text missing from one or more video prompt layers: {phrase}")

            assets = connection.execute(
                """
                select a.id,a.name,a.type,a.imageId,i.filePath,i.state imageState,i.errorReason
                from o_assets2Storyboard b
                join o_assets a on a.id=b.assetId
                left join o_image i on i.id=a.imageId
                where b.storyboardId=?
                order by a.id
                """,
                (row["storyboardId"],),
            ).fetchall()
            for asset in assets:
                all_bound_asset_ids.add(asset["id"])
                if asset["imageId"] is None:
                    errors.append(f"{label} asset has no imageId: {asset['name']} ({asset['id']})")
                    continue
                if not asset["filePath"]:
                    errors.append(f"{label} asset media row has no filePath: {asset['name']} ({asset['id']})")
                    continue
                media_path = resolve_media_path(oss_root, asset["filePath"])
                if media_path is not None and (not media_path.is_file() or media_path.stat().st_size == 0):
                    errors.append(f"{label} asset file missing or empty: {asset['name']} -> {media_path}")
                if asset["errorReason"]:
                    warnings.append(f"{label} asset {asset['name']} errorReason={asset['errorReason']}")

            result_marker = row["selectVideoId"] or row["videoId"] or "-"
            print(
                f"{label} storyboard={row['storyboardId']} track={row['trackId']} "
                f"duration={row['storyboardDuration']}/{row['trackDuration']} assets={len(assets)} "
                f"state={row['storyboardState']}/{row['trackState']} result={result_marker}"
            )
            if row["trackReason"]:
                warnings.append(f"{label} track reason={row['trackReason']}")

        if all_bound_asset_ids:
            placeholders = ",".join("?" for _ in all_bound_asset_ids)
            script_asset_ids = {
                item[0]
                for item in connection.execute(
                    f"select assetId from o_scriptAssets where scriptId=? and assetId in ({placeholders})",
                    [args.script_id, *sorted(all_bound_asset_ids)],
                )
            }
            for asset_id in sorted(all_bound_asset_ids - script_asset_ids):
                asset_name = connection.execute("select name from o_assets where id=?", (asset_id,)).fetchone()
                errors.append(
                    f"bound asset missing from script asset pool: {asset_name[0] if asset_name else asset_id} ({asset_id})"
                )

        audio_rows = connection.execute(
            """
            select role.name roleName,audio.id audioId,audio.name audioName,i.filePath,
                   exists(select 1 from o_scriptAssets sa where sa.scriptId=? and sa.assetId=audio.id) audioInScript
            from o_assetsRole2Audio b
            join o_assets role on role.id=b.assetsRoleId
            join o_assets audio on audio.id=b.assetsAudioId
            left join o_image i on i.id=audio.imageId
            where role.projectId=?
              and (
                exists(select 1 from o_scriptAssets sa where sa.scriptId=? and sa.assetId=role.id)
                or exists(
                  select 1 from o_assets2Storyboard bs
                  join o_storyboard ss on ss.id=bs.storyboardId
                  where ss.scriptId=? and bs.assetId=role.id
                )
              )
            order by role.id
            """,
            (args.script_id, args.project_id, args.script_id, args.script_id),
        ).fetchall()
        print(f"AUDIO_BINDINGS {len(audio_rows)}")
        for audio in audio_rows:
            media_path = resolve_media_path(oss_root, audio["filePath"])
            if not audio["filePath"] or (media_path is not None and not media_path.is_file()):
                errors.append(f"audio binding file missing: {audio['roleName']} -> {audio['audioName']}")
            if not audio["audioInScript"]:
                warnings.append(
                    f"audio asset not in script asset pool: {audio['roleName']} -> {audio['audioName']} ({audio['audioId']})"
                )

    finally:
        connection.close()

    for message in warnings:
        print(f"WARNING {message}")
    for message in errors:
        print(f"ERROR {message}")
    print(f"RESULT errors={len(errors)} warnings={len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
