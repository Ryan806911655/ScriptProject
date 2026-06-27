"""
重复文件扫描 — 按 MD5 哈希找出重复文件，释放磁盘空间
"""

import os
import sys
import hashlib
from collections import defaultdict
from _utils import *


def md5_hash(filepath, chunk_size=8192):
    """计算文件 MD5"""
    h = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def scan_directory(root_path, progress_callback=None):
    """扫描目录，按文件大小 + MD5 找出重复文件"""
    # 第一步：按文件大小分组
    size_map = defaultdict(list)
    file_count = 0

    info(f"扫描目录：{root_path}")
    print()

    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                size = os.path.getsize(fpath)
                if size > 0:  # 跳过空文件
                    size_map[size].append(fpath)
                    file_count += 1
                    if progress_callback and file_count % 500 == 0:
                        progress_callback(file_count)
            except (OSError, PermissionError):
                pass

    info(f"扫描完成，共 {file_count} 个文件，{len(size_map)} 种大小")

    # 第二步：对大小相同的文件组，计算 MD5
    duplicates = []  # [(hash, [path1, path2, ...]), ...]
    groups_to_check = [g for g in size_map.values() if len(g) > 1]

    checked = 0
    total_check = sum(len(g) for g in groups_to_check)

    for group in groups_to_check:
        hash_map = defaultdict(list)
        for fpath in group:
            h = md5_hash(fpath)
            if h:
                hash_map[h].append(fpath)
            checked += 1
            if progress_callback and checked % 100 == 0:
                progress_callback(None, checked, total_check)

        for h, paths in hash_map.items():
            if len(paths) > 1:
                duplicates.append((h, paths))

    return duplicates


def format_file_info(path):
    """格式化文件信息"""
    try:
        size = os.path.getsize(path)
        mtime = datetime_from_ts(os.path.getmtime(path))
        return f"{format_bytes(size)} | {mtime.strftime('%Y-%m-%d %H:%M')}"
    except Exception:
        return "?"


def datetime_from_ts(ts):
    import datetime
    return datetime.datetime.fromtimestamp(ts)


def safe_delete_file(path):
    """安全删除文件"""
    try:
        os.remove(path)
        return True
    except (OSError, PermissionError):
        return False


# ---------- 主流程 ----------
def main():
    cprint(SEP, "lcyan")
    cprint("       重复文件扫描工具", "lwhite")
    cprint(SEP, "lcyan")
    print()

    # 选择目录
    print("  请输入要扫描的文件夹路径：")
    default = os.path.expanduser("~")
    print(f"  （直接回车 = {default}）")
    print()
    target = input("  > ").strip()
    if not target:
        target = default

    if not os.path.isdir(target):
        err(f"目录不存在：{target}")
        pause()
        return

    print()
    info("正在扫描，大目录可能需要几分钟...")
    print()

    duplicates = scan_directory(target)

    if not duplicates:
        print()
        ok("未发现重复文件！")
        pause()
        return

    # 统计
    total_wasted = 0
    for _, paths in duplicates:
        total_wasted += sum(os.path.getsize(p) for p in paths[1:])  # 保留第一个，其余是浪费的

    print()
    ok(f"发现 {len(duplicates)} 组重复文件")
    info(f"如全部清理，可释放约 {format_bytes(total_wasted)}")
    print()

    # 显示每组
    group_idx = 0
    for h, paths in duplicates:
        group_idx += 1
        group_size = os.path.getsize(paths[0])
        wasted = group_size * (len(paths) - 1)
        cprint(f"  --- 第 {group_idx} 组 [{format_bytes(group_size)} x {len(paths)}] 可释放 {format_bytes(wasted)} ---", "lyellow")
        for i, p in enumerate(paths):
            tag = "[保留]" if i == 0 else "[可删]"
            color = "lgreen" if i == 0 else "lred"
            cprint(f"    {tag} {p}", color)
        print()

    # 操作
    cprint("  " + SEP2, "lcyan")
    print("  [A] 自动清理 — 每组保留一个，删除其余（推荐）")
    print("  [D] 手动逐组选择")
    print("  [E] 导出重复文件列表到桌面")
    print("  [0] 返回")
    print()

    choice = input("  请选择: ").strip().lower()

    if choice == "0":
        return

    elif choice == "e":
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        fname = f"重复文件列表_{datetime_from_ts(os.path.getmtime(__file__)).strftime('%Y%m%d_%H%M%S')}.txt"
        import datetime
        fname = f"重复文件列表_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = os.path.join(desktop, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write("重复文件扫描报告\n")
            f.write(f"扫描目录：{target}\n")
            f.write("=" * 60 + "\n\n")
            for h, paths in duplicates:
                for i, p in enumerate(paths):
                    tag = "[保留]" if i == 0 else "[可删]"
                    f.write(f"{tag} {p}\n")
                f.write("\n")
        ok(f"已导出到：{path}")
        pause()
        return

    elif choice == "d":
        deleted = 0
        freed = 0
        for h, paths in duplicates:
            print()
            print(f"  文件：{os.path.basename(paths[0])}")
            print(f"  共 {len(paths)} 份，保留哪个？")
            for i, p in enumerate(paths, 1):
                info_str = format_file_info(p)
                print(f"  [{i}] {p}")
                print(f"      {info_str}")
            print("  [0] 全部保留，跳过")
            print()
            sel = input("  保留哪个（默认 1）: ").strip()
            try:
                keep = int(sel) - 1 if sel else 0
                if keep < 0:
                    continue
                for i, p in enumerate(paths):
                    if i != keep:
                        sz = os.path.getsize(p)
                        if safe_delete_file(p):
                            deleted += 1
                            freed += sz
                            ok(f"已删除：{os.path.basename(p)}")
                        else:
                            err(f"删除失败：{os.path.basename(p)}")
            except (ValueError, IndexError):
                continue
        print()
        ok(f"完成！删除 {deleted} 个文件，释放 {format_bytes(freed)}")
        pause()

    else:
        # 自动清理
        warn(f"将删除 {sum(len(p) - 1 for _, p in duplicates)} 个重复文件")
        print()
        if input("  确认？[Y/N]: ").strip().lower() not in ("y", "yes"):
            info("已取消")
            pause()
            return

        deleted = 0
        freed = 0
        for h, paths in duplicates:
            for p in paths[1:]:  # 保留第一个
                sz = os.path.getsize(p)
                if safe_delete_file(p):
                    deleted += 1
                    freed += sz
                    print(f"  已删除：{os.path.basename(p)}")
                else:
                    print(f"  失败：  {os.path.basename(p)}")

        print()
        ok(f"完成！删除 {deleted} 个文件，释放 {format_bytes(freed)}")
        pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
