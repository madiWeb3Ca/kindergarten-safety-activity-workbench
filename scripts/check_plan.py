#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验园所三防安全活动稿子：方案稿 / 活动总结稿 / 年度排期表三类规则。

支持 .md 与 .html 两种文件（HTML 会先转成纯文本再走同一套规则）。
年度排期表只跑通用红线检查（承诺表述、幼儿实操、外联冒写、占位归集），
不套方案 / 总结的必需段落。

用法：
    python check_plan.py 方案稿.html
    python check_plan.py 总结稿.md --strict   # 警告也按错误处理

退出码：0 = 通过（可含警告）；1 = 有错误（缺段/红线硬伤）；2 = 文件读取失败。
"""

import argparse
import html as html_mod
import os
import re
import sys

# ---------- 两套必需段落 ----------

PLAN_SECTIONS = [
    ("背景与目标", r"^\s*#+\s*.*(背景与目标|先说清|定背景)"),
    ("活动板块安排", r"^\s*#+\s*.*(活动板块|板块安排|选组合)"),
    ("活动流程", r"^\s*#+\s*.*(演练日流程|流程环节|活动流程|当日流程|撤离|避险|情景)"),
    ("分工与物料", r"^\s*#+\s*.*(分工与物料|物料|分工)"),
    ("量力校验", r"^\s*#+\s*.*(量力校验|掂量够不够)"),
    ("安全红线", r"^\s*#+\s*.*(安全.*红线|注意事项|安全)"),
    ("留痕清单", r"^\s*#+\s*.*(迎检|留痕|材料包|归档)"),
    ("待核定项", r"^\s*#+\s*.*(待核定|待填|待核实清单)"),
]

SUMMARY_SECTIONS = [
    ("基本信息", r"^\s*#+\s*.*(基本信息|场次)"),
    ("定量记录", r"^\s*#+\s*.*(定量|人数|班级|用时)"),
    ("过程简述", r"^\s*#+\s*.*(过程简述|经过|过程)"),
    ("顺畅点", r"^\s*#+\s*.*(顺畅|亮点|正面)"),
    ("问题与改进", r"^\s*#+\s*.*(问题|不足|改进)"),
    ("留痕归档", r"^\s*#+\s*.*(留痕|归档|材料)"),
    ("现场照片", r"^\s*#+\s*.*(照片|影像)"),
    ("待核实项", r"^\s*#+\s*.*(待核实|待补)"),
]

# 结论性 / 承诺性表述（红线，出现即错误）
PROMISE_PATTERNS = [
    r"零隐患", r"全部达标", r"保证不出事", r"百分百安全", r"100%\s*安全",
    r"零事故", r"保证安全", r"人人掌握", r"全部合格", r"完全达标", r"圆满成功",
]

# 幼儿不应参与的实操动作（逐行排除否定/边界语境）
KID_OPERATE_PATTERNS = [
    r"幼儿(使用|操作|上手|动手|实操)\s*(灭火器|消火栓|水带|灭火)",
    r"孩子(使用|操作|上手|动手|实操)\s*(灭火器|消火栓|水带|灭火)",
    r"幼儿(参与|进行)\s*灭火(器)?实操",
]

NEGATIVE_HINTS = ["不参与", "不碰", "只观摩", "不操作", "不递", "不在", "仅限",
                  "排除", "边界", "不安排", "远距离", "不出现", "不写", "不下",
                  "禁止", "红线", "结论性"]

# 未确认外联写成既定事实
UNCONFIRMED_OUTREACH = [r"已邀请消防站", r"消防站已到场", r"民警已到场",
                        r"家长已确定参加"]


def in_negative_context(line, patterns):
    """行内是否同时含否定/边界语境；边界说明不算违规。"""
    return any(h in line for h in NEGATIVE_HINTS)


def html_to_text(src):
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", src)
    s = re.sub(r"(?is)<h1[^>]*>", "\n\n# ", s)
    s = re.sub(r"(?is)<h2[^>]*>", "\n\n## ", s)
    s = re.sub(r"(?is)<h3[^>]*>", "\n\n### ", s)
    s = re.sub(r"(?is)</h[123]>", "\n", s)
    s = re.sub(r"(?is)<tr[^>]*>", "\n| ", s)
    s = re.sub(r"(?is)</tr>", " |", s)
    s = re.sub(r"(?is)<t[dh][^>]*>", "", s)
    s = re.sub(r"(?is)</t[dh]>", " | ", s)
    s = re.sub(r"(?is)<li[^>]*>", "\n- ", s)
    s = re.sub(r"(?is)</li>", "", s)
    s = re.sub(r"(?is)<br[^>]*>", "\n", s)
    s = re.sub(r"(?is)<(p|div|section|header|footer|main|ul|table|thead|tbody)[^>]*>", "\n", s)
    s = re.sub(r"(?is)</(p|div|section|header|footer|main|ul|table|thead|tbody)>", "\n", s)
    s = re.sub(r"(?is)<figure[^>]*>", "\n", s)
    s = re.sub(r"(?is)</figure>", "\n", s)
    s = re.sub(r"(?is)<[^>]+>", "", s)
    s = html_mod.unescape(s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s


def find_section(text, pattern):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            body = []
            for j in range(i + 1, len(lines)):
                if re.match(r"^\s*#{1,2}\s", lines[j]):
                    break
                body.append(lines[j])
            return i, "\n".join(body)
    return -1, ""


def detect_mode(text):
    head = "\n".join(text.splitlines()[:6])
    if "总结" in head:
        return "summary"
    if re.search(r"年度排期|年度安排|学期安排|季度轮换|排期表", head):
        return "yearly"
    return "plan"


def main():
    parser = argparse.ArgumentParser(description="校验园所安全活动方案稿 / 总结稿")
    parser.add_argument("path", help="稿子文件（.md 或 .html）")
    parser.add_argument("--strict", action="store_true", help="警告也按错误处理")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"[错误] 文件不存在：{args.path}", file=sys.stderr)
        return 2
    if os.path.isdir(args.path):
        print(f"[错误] 传入的是文件夹，请指定具体的稿子文件：{args.path}", file=sys.stderr)
        return 2

    try:
        with open(args.path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        print("[错误] 文件编码无法识别，请另存为 UTF-8 编码后再校验", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"[错误] 文件读取失败：{e}", file=sys.stderr)
        return 2

    if not text.strip():
        print("[错误] 文件内容为空，请先填写稿子再校验", file=sys.stderr)
        return 2

    if os.path.splitext(args.path)[1].lower() in (".html", ".htm"):
        text = html_to_text(text)

    mode = detect_mode(text)
    if mode == "summary":
        sections = SUMMARY_SECTIONS
        label = "活动总结稿"
    elif mode == "yearly":
        sections = []
        label = "年度排期参考表"
    else:
        sections = PLAN_SECTIONS
        label = "活动方案稿"
    errors, warnings = [], []

    # 1. 章节齐全
    bodies = {}
    for name, pattern in sections:
        idx, body = find_section(text, pattern)
        if idx < 0:
            errors.append(f"缺少必需段落「{name}」")
        else:
            bodies[name] = body

    # 2. 结论性 / 承诺红线（逐行排除红线说明 / 否定语境）
    for line in text.splitlines():
        for pat in PROMISE_PATTERNS:
            m = re.search(pat, line)
            if m and not in_negative_context(line, PROMISE_PATTERNS):
                errors.append(f"出现结论性 / 承诺表述：「{m.group(0)}」；稿子不下合规结论，只记过程事实")

    # 3. 幼儿参与器材实操（逐行排除否定语境）
    for line in text.splitlines():
        for pat in KID_OPERATE_PATTERNS:
            m = re.search(pat, line)
            if m and not in_negative_context(line, KID_OPERATE_PATTERNS):
                errors.append(f"幼儿不得参与明火与器材实操：「{m.group(0)}」；实操对象仅限成人在岗人员")

    # 4. 方案稿：板块对象是否分清成人 / 幼儿（纯宣教、明确不含演练实操的场次豁免）
    if mode == "plan":
        scope_excluded = bool(re.search(r"本场不组织|本场不含|不安排.{0,4}实操|演练另行安排", text))
        adult_terms = r"教职工|安保|志愿|教师|保健医|后勤|配班|工作人员|保育员"
        kid_terms = r"幼儿|各班|儿童|孩子|学生"
        if not scope_excluded and ("疏散演练" in text or "避险疏散" in text or "器材实操" in text):
            if not re.search(adult_terms, text):
                warnings.append("未写明成人环节对象（教职工 / 教师 / 安保 / 保健医等在岗成人）")
            if not re.search(kid_terms, text):
                warnings.append("未写明幼儿参与环节（认知 / 观摩 / 演练）")

    # 5. 外联未确认写成既定事实
    for pat in UNCONFIRMED_OUTREACH:
        m = re.search(pat, text)
        if m:
            warnings.append(f"外联对象未确认不宜写成既定事实：「{m.group(0)}」；联系不上降级为园内活动")

    # 6. 占位分类：【待填】= 对话必问项未采集（成稿应清零）；【待核实】= 现场/政策项，允许但须归集清单
    if "待填" in text:
        warnings.append("正文仍有【待填】占位：对话必问项未采集完，出稿前应逐项问清填入（见 data-checklist A 类）；定不下来的角色写进待核定清单，不留正文空")
    if "待核实" in text:
        _idx, settle_body = find_section(text, r"^\s*#+\s*.*(待核定|待填项|待核实|待补)")
        if _idx < 0 or "待核实" not in settle_body and "待补" not in settle_body:
            warnings.append("【待核实】项未收进文末清单：现场盘点与政策核对项应集中列出，不散落在正文")

    # 7. 总结稿：定量章节应有可核对的数字或待核实标注
    if mode == "summary":
        qbody = bodies.get("定量记录", "")
        if qbody and not re.search(r"\d+|待核实", qbody):
            warnings.append("定量记录章节未出现人数 / 班级 / 用时等数字；取不到的项目记【待核实】，不要留空")

    # 汇总输出
    print(f"=== 校验结果：{args.path}（{label}）===")
    if errors:
        print(f"\n[错误] {len(errors)} 项（必须修）")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print(f"\n[警告] {len(warnings)} 项（建议修）")
        for w in warnings:
            print(f"  ! {w}")
    if not errors and not warnings:
        print("\n[通过] 结构完整，红线项无告警")
    elif not errors:
        print("\n[通过] 结构完整（有警告，建议修改后再交付）")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
