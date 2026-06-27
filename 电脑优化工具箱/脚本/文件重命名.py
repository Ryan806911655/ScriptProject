"""
文件批量重命名 — 序号/前缀后缀/替换文本/正则/扩展名
"""

import os
import sys
import re
from _utils import *


def preview_rename(directory, new_names_map):
    """预览重命名结果"""
    print()
    cprint("  预览（前 10 个）：", "lcyan")
    for i, (old, new) in enumerate(new_names_map.items()):
        if i >= 10:
            print(f"  ... 还有 {len(new_names_map) - 10} 个文件")
            break
        print(f"  {old}")
        cprint(f"  → {new}", "lgreen")
    print()

    # 检查冲突
    all_new = list(new_names_map.values())
    conflicts = [n for n in all_new if all_new.count(n) > 1]
    if conflicts:
        warn(f"有 {len(set(conflicts))} 个文件名会冲突！请调整规则")


def apply_rename(directory, new_names_map):
    """执行重命名"""
    count = 0
    failed = 0
    for old, new in new_names_map.items():
        old_path = os.path.join(directory, old)
        new_path = os.path.join(directory, new)
        try:
            os.rename(old_path, new_path)
            count += 1
        except (OSError, PermissionError) as e:
            err(f"重命名失败：{old} → {new}（{e}）")
            failed += 1
    return count, failed


def scan_files(directory, pattern=None):
    """扫描目录中的文件"""
    files = []
    try:
        for fname in os.listdir(directory):
            fpath = os.path.join(directory, fname)
            if os.path.isfile(fpath):
                if pattern is None or pattern.lower() in fname.lower():
                    files.append(fname)
    except (PermissionError, FileNotFoundError):
        pass
    return sorted(files)


# ---------- 主流程 ----------
def main():
    cprint(SEP, "lcyan")
    cprint("       文件批量重命名", "lwhite")
    cprint(SEP, "lcyan")
    print()

    # 选择目录
    print("  请输入文件夹路径：")
    default = os.path.join(os.path.expanduser("~"), "Desktop")
    print(f"  （直接回车 = 桌面）")
    print()
    target = input("  > ").strip()
    if not target:
        target = default

    if not os.path.isdir(target):
        err(f"目录不存在：{target}")
        pause()
        return

    while True:
        print()
        files = scan_files(target)
        info(f"目录：{target}（{len(files)} 个文件）")

        if files:
            print()
            print("  文件列表（前 15 个）：")
            for f in files[:15]:
                print(f"    {f}")
            if len(files) > 15:
                print(f"    ... 还有 {len(files) - 15} 个")

        print()
        print("  [1] 添加序号前缀（如 001_xxx.txt）")
        print("  [2] 添加文本前缀/后缀")
        print("  [3] 替换文件名中的文本")
        print("  [4] 删除文件名中的文本")
        print("  [5] 正则替换")
        print("  [6] 修改扩展名")
        print("  [7] 筛选特定文件（再以上操作）")
        print("  [8] 切换目录")
        print("  [0] 返回上级")
        print()

        choice = input("  请选择: ").strip()

        if choice == "0":
            return
        elif choice == "8":
            new_dir = input("  新目录路径: ").strip()
            if new_dir and os.path.isdir(new_dir):
                target = new_dir
            else:
                err("目录无效")
            continue

        # 需要筛选的情况
        filtered_files = files
        if choice == "7":
            pattern = input("  筛选关键词（留空=全部）: ").strip()
            if pattern:
                filtered_files = scan_files(target, pattern)
                info(f"筛选出 {len(filtered_files)} 个文件")
            else:
                filtered_files = files

        if not filtered_files:
            info("没有匹配的文件")
            continue

        new_names = {}

        if choice == "1":
            # 序号前缀
            digits = input("  序号位数（默认 3，如 001）: ").strip() or "3"
            sep = input("  分隔符（默认 _，为空则不添加）: ").strip()
            start = input("  起始序号（默认 1）: ").strip() or "1"

            for i, fname in enumerate(filtered_files, int(start)):
                num = str(i).zfill(int(digits))
                if sep:
                    new_names[fname] = f"{num}{sep}{fname}"
                else:
                    new_names[fname] = f"{num}{fname}"

            preview_rename(target, new_names)

        elif choice == "2":
            # 添加前缀/后缀
            prefix = input("  添加前缀（留空=不添加）: ").strip()
            suffix_input = input("  添加后缀（留空=不添加，将加在扩展名前）: ").strip()

            for fname in filtered_files:
                name, ext = os.path.splitext(fname)
                new_name = f"{prefix}{name}{suffix_input}{ext}"
                new_names[fname] = new_name

            preview_rename(target, new_names)

        elif choice == "3":
            # 替换文本
            old_text = input("  要替换的文本: ").strip()
            new_text = input("  替换为: ").strip()
            if not old_text:
                info("未输入要替换的文本")
                continue

            for fname in filtered_files:
                new_names[fname] = fname.replace(old_text, new_text)

            preview_rename(target, new_names)

        elif choice == "4":
            # 删除文本
            del_text = input("  要删除的文本: ").strip()
            if not del_text:
                continue

            for fname in filtered_files:
                new_names[fname] = fname.replace(del_text, "")

            preview_rename(target, new_names)

        elif choice == "5":
            # 正则替换
            print("  例：把 (1) (2) 等序号去掉 →  pattern: \\(\\d+\\)  replace: (留空)")
            pattern_str = input("  正则 pattern: ").strip()
            replace_str = input("  替换为: ").strip()
            if not pattern_str:
                continue

            try:
                compiled = re.compile(pattern_str)
                for fname in filtered_files:
                    new_names[fname] = compiled.sub(replace_str, fname)
                preview_rename(target, new_names)
            except re.error as e:
                err(f"正则错误：{e}")
                continue

        elif choice == "6":
            # 修改扩展名
            new_ext = input("  新扩展名（不含点，如 txt）: ").strip()
            if not new_ext:
                continue

            for fname in filtered_files:
                name, _ = os.path.splitext(fname)
                new_names[fname] = f"{name}.{new_ext}"

            preview_rename(target, new_names)

        else:
            continue

        # 确认执行
        if new_names and input("\n  确认执行重命名？[Y/N]: ").strip().lower() in ("y", "yes"):
            ok_count, fail_count = apply_rename(target, new_names)
            ok(f"完成！成功 {ok_count} 个，失败 {fail_count} 个")
        else:
            info("已取消")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。")
    except Exception as e:
        err(f"程序异常：{e}")
        input("\n  按回车退出...")
