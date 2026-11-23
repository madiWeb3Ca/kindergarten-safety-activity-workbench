#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冒烟测试：验证 scaffold、render_html 与 check 三个脚本的行为符合规范。

用法：python selftest.py
退出码：0 = 全部通过；1 = 有用例失败。
"""

import base64
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCAFFOLD = os.path.join(HERE, "scaffold_plan.py")
CHECK = os.path.join(HERE, "check_plan.py")
RENDER = os.path.join(HERE, "render_html.py")

GOOD = """# 安全综合活动方案（示例）

**时间窗口**：安全教育日　**主办 / 负责人**：后勤老师
**参与对象**：全园幼儿、教职工、安保志愿力量　**本场侧重**：综合一场

## 一、背景与目标

- 时间窗口：安全教育日；当年主题【待核实：以官方通知为准】。
- 参与对象：全园幼儿、教职工、安保志愿力量；家长代表【待核实】。
- 目标：幼儿认识危险、听懂信号、跟随撤离；教职工熟悉报警与疏散分工。

## 二、活动板块安排

| 板块 | 内容 | 对象 | 时间 | 负责人 | 物料 | 留痕材料 |
|---|---|---|---|---|---|---|
| 宣教认知 | 绘本、标志认知 | 各班幼儿 | 每班 1 次 | 各班教师 | 图卡 | 教案、照片 |
| 疏散演练 | 警报撤离、集合清点 | 全体幼儿＋教职工 | 11 月中旬上午（草稿） | 总指挥：副园长 | 广播、签到表 | 签到、照片、清点记录 |
| 器材实操 | 灭火器、消火栓要领 | 教职工、安保、志愿力量 | 演练同日下午 | 器材保障：安保主任 | 训练罐 | 实操签到、照片 |

## 三、演练日流程

| 时段 | 环节 | 负责人 | 要点 |
|---|---|---|---|
| 0—5' | 动员 | 各班教师 | 讲清信号路线，防踩踏 |
| 5—10' | 撤离 | 引导员 | 教师前后带队 |
| 10—18' | 清点报数 | 清点员 | 与名册核对 |

## 四、分工与物料

- 分工：总指挥副园长、引导员配班老师、清点员班主任、医务联络保健医、器材保障安保主任、拍照行政。
- 物料：广播警报、路线图、训练器材、签到名册；器材数量【待核实】。

## 五、量力校验

| 维度 | 状态 | 缺口处置 |
|---|---|---|
| 人手 | 待补 | 凑不齐分批演练 |
| 场地 | 待核 | 集合点现场确认 |

能不能做：补缺口后可执行

## 六、安全注意事项与红线

1. 幼儿不参与明火与器材实操，只认知、观摩、疏散演练。
2. 防踩踏，通道分流向。
3. 器材与通道以现场核查为准。
4. 不写结论性表述；本稿不替代制度文件。

## 七、留痕清单

| 序号 | 材料 | 状态 |
|---|---|---|
| 1 | 方案定稿 | 待核定 |
| 2 | 演练签到与清点 | 【待补】 |
| 3 | 照片 | 【待补】 |

## 八、待核定 / 待核实项

- 【待核实：器材数量、场地条件、外联对象、属地通知要求】集中在此清单核定。
"""

BAD = """# 安全活动

## 一、背景与目标

- 保证不出事，做到零隐患、全部达标。

## 二、活动板块安排

| 板块 | 内容 | 对象 |
|---|---|---|
| 器材实操 | 幼儿使用灭火器实操 | 幼儿 |
"""

GOOD_SUMMARY = """# 防火疏散演练活动总结

**活动日期**：11 月 12 日　**地点**：园内操场　**负责人**：后勤老师
**参与对象**：大班、中班共 4 个班，幼儿 112 人，教职工 14 人

## 一、基本信息

- 活动类型：防火；日期：11 月 12 日；地点：园内操场；负责人：后勤老师。
- 参与班级：大班 2 个、中班 2 个。

## 二、定量记录

- 参与幼儿 112 人；教职工 / 安保 14 人；涉及班级 4 个。
- 演练用时 9 分 20 秒；环节按方案完成。
- 签到与清点：名册核对一致，无缺员。

## 三、过程简述

- 宣教：班级先讲 119 与疏散信号。
- 演练：警报后带队撤离，集合点清点报数。
- 家园：群内发布家庭防火提示。

## 四、顺畅点

- 撤离秩序顺畅，教师前后带队到位；幼儿能跟随队伍。

## 五、问题与改进

- 中二班路线在楼梯口短暂停留；下次提前安排转角引导员。

## 六、留痕材料归档

| 序号 | 材料 | 状态 |
|---|---|---|
| 1 | 方案与通知 | 已归档 |
| 2 | 签到清点表 | 已归档 |
| 3 | 过程照片 | 见第七节 |

## 七、现场照片

![集合点清点](shot.png)

## 八、待核实项

- 【待核实：照片拍摄人记录待补】
"""

BAD_SUMMARY = """# 活动总结

## 三、过程简述

- 活动全部达标，圆满成功。
"""

GOOD_YEARLY = """# 一学年三防安全活动年度排期表

## 一、排期背景

- 覆盖防火、防震、防拐；当年主题【待核实：以官方通知为准】。

## 二、年度轮换安排

| 时段 | 分支 | 侧重 |
|---|---|---|
| 秋季 | 防火 | 宣教认知＋疏散演练 |
| 春季 | 防震 | 避险动作＋震后疏散 |
| 学期内 | 防拐 | 情景认知与角色扮演 |

## 三、场间衔接

- 上一场改进项带入下一场；旧场数字、路线、联系人不沿用。

## 附：待核实项

- 【待核实：具体日期、负责人与场地安排】
"""

PNG_1PX = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR42mNk+M9QDw"
           "ADhgGAWjR9awAAAABJRU5ErkJggg==")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def case(name, cond, detail=""):
    if cond:
        print(f"[通过] {name}")
        return True
    print(f"[失败] {name}　{detail}")
    return False


def main():
    results = []
    tmp = tempfile.mkdtemp(prefix="kaw_selftest_")

    # 用例 1：合格方案应通过校验
    good_path = os.path.join(tmp, "good.md")
    with open(good_path, "w", encoding="utf-8") as f:
        f.write(GOOD)
    r = run([sys.executable, CHECK, good_path])
    results.append(case("1 合格方案通过校验", r.returncode == 0 and "[通过]" in r.stdout,
                        r.stdout[-200:]))

    # 用例 2：缺陷方案（结论词＋幼儿实操＋缺段）应判不通过
    bad_path = os.path.join(tmp, "bad.md")
    with open(bad_path, "w", encoding="utf-8") as f:
        f.write(BAD)
    r = run([sys.executable, CHECK, bad_path])
    results.append(case("2 缺陷方案被拦截", r.returncode == 1 and "[错误]" in r.stdout,
                        r.stdout[-200:]))

    # 用例 3：三分支方案骨架均可生成且可被校验读取
    branch_ok = True
    detail = []
    for branch in ("防火", "防震", "防拐"):
        out = os.path.join(tmp, f"{branch}.html")
        r = run([sys.executable, SCAFFOLD, "--title", f"{branch}方案", "--branch", branch,
                 "--out", out])
        ok = r.returncode == 0 and os.path.exists(out)
        if ok:
            r2 = run([sys.executable, CHECK, out])
            ok = r2.returncode != 2
        if not ok:
            branch_ok = False
            detail.append(branch)
    results.append(case("3 三分支骨架生成且可读", branch_ok, "; ".join(detail)))

    # 用例 4：缺必填参数（--title）应报错退出
    r = run([sys.executable, SCAFFOLD])
    results.append(case("4 缺必填参数报错", r.returncode != 0, r.stderr[:200]))

    # 用例 5：骨架 md 不含红线词（红线说明行引用违禁词除外），且可被校验读取
    md_out = os.path.join(tmp, "骨架.md")
    r = run([sys.executable, SCAFFOLD, "--title", "疏散演练安排", "--branch", "防震",
             "--focus", "演练为主", "--format", "md", "--out", md_out])
    ok = r.returncode == 0 and os.path.exists(md_out)
    if ok:
        with open(md_out, "r", encoding="utf-8") as f:
            md_text = f.read()
        banned = ["零隐患", "保证不出事", "全部达标", "零事故"]
        ctx = ("不出现", "不写", "不下", "红线", "禁止", "结论性", "「")
        leaked = [w for w in banned
                  for line in md_text.splitlines()
                  if w in line and not any(c in line for c in ctx)]
        ok = not leaked
        r2 = run([sys.executable, CHECK, md_out])
        ok = ok and r2.returncode != 2
    results.append(case("5 骨架 md 无红线词且可读", ok, r.stderr[:200]))

    # 用例 6：缺陷件转成 HTML 后仍必须被拦截（HTML 路径不能空转）
    html_path = os.path.join(tmp, "bad.html")
    r = run([sys.executable, RENDER, bad_path, "-o", html_path])
    ok = r.returncode == 0 and os.path.exists(html_path)
    if ok:
        r = run([sys.executable, CHECK, html_path])
        ok = r.returncode == 1 and "[错误]" in r.stdout
    results.append(case("6 HTML 缺陷件同样被拦截", ok,
                        r.stdout[-200:] if r.stdout else r.stderr[:200]))

    # 用例 7：包内 examples 全部 md 应通过校验
    examples_dir = os.path.join(os.path.dirname(HERE), "examples")
    sample_mds = sorted(f for f in os.listdir(examples_dir) if f.endswith(".md"))
    sample_ok = len(sample_mds) >= 3
    sample_detail = []
    for fname in sample_mds:
        sp = os.path.join(examples_dir, fname)
        r = run([sys.executable, CHECK, sp])
        if r.returncode != 0 or "[通过]" not in r.stdout:
            sample_ok = False
            sample_detail.append(f"{fname}: rc={r.returncode}")
    results.append(case("7 examples 示例均通过校验", sample_ok, "; ".join(sample_detail)))

    # 用例 8：合格总结稿通过总结模式校验
    sum_path = os.path.join(tmp, "good_summary.md")
    with open(sum_path, "w", encoding="utf-8") as f:
        f.write(GOOD_SUMMARY)
    r = run([sys.executable, CHECK, sum_path])
    results.append(case("8 合格总结稿通过校验", r.returncode == 0 and "[通过]" in r.stdout,
                        r.stdout[-200:]))

    # 用例 9：缺陷总结稿（承诺词＋缺段）被拦截
    bsum_path = os.path.join(tmp, "bad_summary.md")
    with open(bsum_path, "w", encoding="utf-8") as f:
        f.write(BAD_SUMMARY)
    r = run([sys.executable, CHECK, bsum_path])
    results.append(case("9 缺陷总结稿被拦截", r.returncode == 1 and "[错误]" in r.stdout,
                        r.stdout[-200:]))

    # 用例 10：本地照片 base64 内嵌进 HTML，无外部路径残留
    png_path = os.path.join(tmp, "shot.png")
    with open(png_path, "wb") as f:
        f.write(base64.b64decode(PNG_1PX))
    sum_md = os.path.join(tmp, "photo_summary.md")
    with open(sum_md, "w", encoding="utf-8") as f:
        f.write(GOOD_SUMMARY)
    r = run([sys.executable, RENDER, sum_md])
    ok = r.returncode == 0
    if ok:
        with open(os.path.splitext(sum_md)[0] + ".html", "r", encoding="utf-8") as f:
            html_doc = f.read()
        ok = ("data:image/png;base64" in html_doc) and ("shot.png" not in html_doc)
    results.append(case("10 照片内嵌且无外部路径", ok, r.stderr[:200]))

    # 用例 11：总结骨架可生成、可校验
    sum_out = os.path.join(tmp, "summary_skeleton.html")
    r = run([sys.executable, SCAFFOLD, "--mode", "summary", "--title", "活动总结",
             "--out", sum_out])
    ok = r.returncode == 0 and os.path.exists(sum_out)
    if ok:
        r2 = run([sys.executable, CHECK, sum_out])
        ok = r2.returncode != 2
    results.append(case("11 总结骨架生成且可读", ok, r.stderr[:200]))

    # 用例 12：年度排期表识别为 yearly 模式，不套方案缺段规则，通过校验
    yearly_path = os.path.join(tmp, "yearly.md")
    with open(yearly_path, "w", encoding="utf-8") as f:
        f.write(GOOD_YEARLY)
    r = run([sys.executable, CHECK, yearly_path])
    results.append(case("12 年度排期表通过校验且不误判缺段",
                        r.returncode == 0 and "年度排期" in r.stdout and "[通过]" in r.stdout,
                        r.stdout[-200:]))

    # 用例 13：正文残留口述等采集过程标记 → 给出警告（不拦稿）
    marker_path = os.path.join(tmp, "marker.md")
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(GOOD.replace("## 四、分工与物料",
                             "## 四、分工与物料\n\n- 班级分布（口述）：一层 2 个班。"))
    r = run([sys.executable, CHECK, marker_path])
    results.append(case("13 过程标记被警告提示",
                        r.returncode == 0 and "过程标记" in r.stdout,
                        r.stdout[-200:]))

    # 用例 14：钟点与「到点后」相对时点混用 → 给出警告
    mix_path = os.path.join(tmp, "timemix.md")
    with open(mix_path, "w", encoding="utf-8") as f:
        f.write(GOOD.replace("| 10—18' | 清点报数 | 清点员 | 与名册核对 |",
                              "| 9:30 | 清点报数 | 清点员 | 到点后与名册核对 |"))
    r = run([sys.executable, CHECK, mix_path])
    results.append(case("14 时段标签混用被警告提示",
                        r.returncode == 0 and "标签混用" in r.stdout,
                        r.stdout[-200:]))

    # 用例 15：防火方案缺触发响应链（发现—上报—启动通报）→ 给出警告
    trig_path = os.path.join(tmp, "trigger.md")
    with open(trig_path, "w", encoding="utf-8") as f:
        f.write(GOOD.replace("缺员立即上报总指挥", "缺员立即告知总指挥"))
    r = run([sys.executable, CHECK, trig_path])
    results.append(case("15 防火触发链缺失被警告提示",
                        r.returncode == 0 and "触发响应" in r.stdout,
                        r.stdout[-200:]))

    # 用例 16：防震方案缺避险动作环节（避险 / 伏地 / 护头 / 停止口令等）→ 给出警告
    eq_path = os.path.join(tmp, "earthquake.md")
    with open(eq_path, "w", encoding="utf-8") as f:
        f.write(GOOD.replace("**时间窗口**：安全教育日",
                             "**时间窗口**：安全教育日\n- 分支：防震避险疏散演练"))
    r = run([sys.executable, CHECK, eq_path])
    results.append(case("16 防震避险链缺失被警告提示",
                        r.returncode == 0 and "避险动作" in r.stdout,
                        r.stdout[-200:]))

    # 用例 17：防拐方案误写撤离演练 / 强行带走模拟 → 给出边界警告
    abd_path = os.path.join(tmp, "abduction.md")
    with open(abd_path, "w", encoding="utf-8") as f:
        f.write("# 防拐情景教育活动方案\n\n## 一、背景与目标\n\n- 防拐防走失教育，陌生人情景练习。\n\n## 三、活动流程\n\n| 环节 | 动作 |\n|---|---|\n| 撤离演练 | 陌生人把孩子带出门疏散 |\n")
    r = run([sys.executable, CHECK, abd_path])
    results.append(case("17 防拐误写撤离被警告提示",
                        "撤离演练" in r.stdout and "防拐" in r.stdout,
                        r.stdout[-200:]))

    print(f"\n=== {sum(results)}/{len(results)} 用例通过 ===")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
