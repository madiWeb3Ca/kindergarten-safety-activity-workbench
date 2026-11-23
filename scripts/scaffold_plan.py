#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按背景参数生成园所三防安全活动骨架（方案稿 / 总结稿）。

用法：
    python scaffold_plan.py --title "防震避险疏散演练方案" --branch 防震
    python scaffold_plan.py --title "防拐情景教育活动" --branch 防拐 --focus 宣教为主
    python scaffold_plan.py --mode summary --title "防火疏散演练活动总结"
    python scaffold_plan.py --title "综合活动方案" --format md

默认输出 HTML；需要纯文本底稿时用 --format md。
占位分两类：【待填】为对话必问项，出稿前由引导采集填入、正文不留空；
【待核实】为现场盘点与政策核对项，允许保留并归集到文末清单。
字段分类见 references/data-checklist.md。
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_html import render_markdown  # noqa: E402

BRANCHES = ["防火", "防震", "防拐"]
FOCUSES = ["宣教认知为主", "演练为主", "综合一场"]


def _plan_head(title, window, branch, focus, target_lines):
    return f"""# {title}

**时间窗口**：{window}　**分支**：{branch}　**主办 / 负责人**：【待填：姓名 / 岗位】
**参与对象**：【待填：幼儿 / 教职工 / 安保志愿力量 / 家长代表 / 外部单位】　**本场侧重**：{focus}

> 本稿为活动组织初稿，供对内汇报与迎检材料准备；园名、日期、人数、分工、器材与场地条件须人工核定后再定稿。本稿不替代隐患台账、应急预案与设施维护；不下"达标 / 零隐患"结论。当年主题与属地要求以官方通知为准。

## 一、背景与目标

- **时间窗口 / 主题**：{window}；当年主题【待核实：以当年官方通知为准，不沿用往年】。
- **参与对象**：【待填：全园幼儿、教职工、安保 / 志愿力量；家长代表、外部单位视情邀请】。
- **本场目标**：
{target_lines}
"""


def _plan_tail(branch, extra_redline=""):
    redlines = [
        "**幼儿只参与认知、观摩与教师带领的演练**；成人专项环节与幼儿队伍分开。",
        "**防踩踏优先**：演练前讲明规则，通道分流向，不在楼梯口停留或围观。",
        "**条件以现场为准**：器材完好性、通道畅通、值守配置以现场核查为准；人数、器材数量、场地条件【待核实】，不预设。",
        "**不写结论性表述**：不出现「零隐患」「全部达标」「保证不出事」「百分百安全」；问题进整改闭环，不在本方案下结论。",
        "**方案不替代制度文件**：本件是活动组织稿；日常检查巡查、应急预案、设施维护按园所既有制度和属地要求执行。",
    ]
    if extra_redline:
        redlines.insert(0, extra_redline)
    redline_md = "\n".join(f"{i}. {r}" for i, r in enumerate(redlines, 1))
    return f"""
## 二、活动板块安排

| 板块 | 内容 | 对象 | 时间 / 时长 | 负责人 | 物料 | 留痕材料 |
|---|---|---|---|---|---|---|
| 宣教认知 | 绘本 / 儿歌 / 图卡 / 动画，主题谈话 | 各班幼儿 | 【待填：每班 1 次】 | 各班教师【待填】 | 绘本、动画、图卡 | 教案、课堂照片 |
| 演练 / 情景 | 见第三节流程 | 全体幼儿＋教职工 | 【待填日期】 | 总指挥【待填】 | 广播 / 警报、签到表、集合点标识 | 方案、签到、照片、清点记录、小结 |
| 家园宣传 | 群安全提示、园内海报、亲子任务 | 在读家庭 | 活动期内 | 宣传对接人【待填】 | 海报、群通知模板 | 群截图、亲子作品 |

## 三、活动流程

| 时段 | 环节 | 负责人 | 要点 |
|---|---|---|---|
| 【待填】 | 动员：讲清信号、路线 / 规则、集合点 | 各班教师 | 幼儿知道跟着老师行动，不喧哗不推挤 |
| 【待填】 | 主体环节 | 引导员【待填】 | 按分支口径执行（见 references/activity-seeds.md） |
| 【待填】 | 集合 / 小结 | 清点员、总指挥 | 与名册核对，缺员立即上报；只记事实与改进点 |
| 【待填】 | 有序带回 | 各班教师 | — |

## 四、分工与物料

- **分工**：总指挥【待填】；引导员【待填】；班级清点员【待填】；医务 / 联络【待填】；器材保障【待填】；拍照留痕【待填】。
- **物料清单**：广播 / 警报、路线图、集合点标识、签到表、班级名册、拍照设备、海报与群通知模板；器材数量【待核实】。

## 五、量力校验

| 维度 | 状态（现成 / 待补 / 待核） | 缺口处置 |
|---|---|---|
| 人手 | 【待填】 | 角色凑不齐先缩规模、分批进行；角色不能空 |
| 时间 | 【待填】 | 倒排筹备节点；活动日期待排期 |
| 物料 | 【待填】 | 先盘点复用，缺项列补充；不编数量 |
| 场地 | 【待填】 | 路线、集合点、容量待现场确认；不满足分批或换场地 |
| 通知渠道 | 【待填】 | 园内通知、家园群覆盖；外联接洽时确认 |
| 外联条件 | 【待填】 | 外部单位联系不上，降级为园内活动 |

**能不能做**：【待填：可执行 / 补缺口后可执行 / 降级或缩规模】

## 六、安全注意事项与红线

{redline_md}

## 七、留痕清单

| 序号 | 材料 | 状态 |
|---|---|---|
| 1 | 活动方案（定稿、签字 / 盖章版） | 本稿待核定 |
| 2 | 活动通知 / 班级教案 | 【待补】 |
| 3 | 演练签到表、人数清点记录 | 【待补】 |
| 4 | 活动过程照片（动员、主体、集合、小结） | 【待补】 |
| 5 | 专项培训 / 情景活动记录 | 【待补】 |
| 6 | 家园群通知截图、亲子作品 | 【待补】 |
| 7 | 活动小结 | 【待补】 |

## 八、待核定 / 待核实项

- 【待填：园所全称、活动具体日期与时段；参演人数、各班分工与负责人姓名】
- 【待核实：器材数量、场地条件、人员配置；外部单位 / 家长代表接洽结果；属地教育 / 应急 / 公安部门通知要求与报送时限】
"""


def build_plan(branch, title, window, focus):
    if branch == "防火":
        target = """  1. 幼儿认识火灾危险、听懂疏散警报、知道 119，能在教师带领下按路线撤离；
  2. 教职工熟悉报警、初起处置与疏散分工，安保与志愿力量会用手边器材；
  3. 组织一次疏散演练，留存通知、照片、签到、小结等记录备检。"""
        tail_extra = "**幼儿不参与明火与器材实操**：灭火器、消火栓操作仅限教职工、安保与志愿力量；幼儿环节为认知、观摩与疏散演练。"
        body = _plan_head(title, window, branch, focus, target)
        body += _plan_tail(branch, tail_extra)
        # 防火补触发响应行（发现—上报—启动通报），见 drill-sop.md
        body = body.replace(
            "| 【待填】 | 主体环节 | 引导员【待填】 | 按分支口径执行（见 references/activity-seeds.md） |",
            "| 【待填】 | 触发响应：模拟起火点示警 → 报总指挥 → 宣布启动 → 通报各组就位 | 总指挥 / 发现人【待填】 | 情境设定，不点明火；见 references/drill-sop.md |\n| 【待填】 | 主体环节 | 引导员【待填】 | 按分支口径执行（见 references/activity-seeds.md） |"
        )
        # 防火补成人专项行
        body = body.replace(
            "| 家园宣传 |",
            "| 器材实操 | 灭火器、消火栓、防烟面具要领与实操；幼儿只观摩、不参与明火操作 | 教职工、安保、志愿力量 | 【待填】 | 器材保障人【待填】 | 训练器材 | 实操签到、照片 |\n| 家园宣传 |"
        )
        return body

    if branch == "防震":
        target = """  1. 幼儿认识地震是自然现象，记住"伏地、遮挡、手抓牢"避险动作；
  2. 震动停止后能在教师带领下护头、按路线有序撤离到空旷集结点；
  3. 教职工熟悉避险口令、撤离引导与清点分工。"""
        tail_extra = "**震时避险、震后疏散**：避险时不跳窗、不乘电梯、不盲目冲出；震动停止后再撤离；室外集结点远离楼房、围墙、电杆、大树。"
        body = _plan_head(title, window, branch, focus, target)
        body += _plan_tail(branch, tail_extra)
        body = body.replace(
            "| 演练 / 情景 | 见第三节流程 |",
            "| 避险疏散演练 | 就近避险 → 震动停止后护头疏散 → 集合清点小结 |"
        )
        # 防震补避险疏散链占位行（信号 → 避险 → 保持 → 疏散），见 drill-sop.md
        body = body.replace(
            "| 【待填】 | 主体环节 | 引导员【待填】 | 按分支口径执行（见 references/activity-seeds.md） |",
            "| 【待填】 | 避险信号 | 各班教师 | 就近躲桌下 / 墙角，伏地、遮挡、手抓牢；见 references/drill-sop.md |\n"
            "| 【待填】 | 保持避险 | 各班教师 | 护头蜷曲保持到停止口令；不奔跑出门、不跳窗 |\n"
            "| 【待填】 | 震后疏散 | 引导员【待填】 | 停止口令后护头快走，按预定路线到空旷集结点 |"
        )
        return body

    # 防拐
    target = """  1. 幼儿记住不跟陌生人走、不接陌生人食物玩具、不说家庭信息、不上陌生人车；
  2. 知道走失时原地等候或向老师、保安、穿制服人员求助；
  3. 通过情景游戏与口诀巩固拒绝、呼救、求助三步。"""
    tail_extra = "**情景温和、不恐吓**：不使用恐怖陌生人形象，不演暴力情节；不用「警察抓人」类话语；不组织撤离演练；不展开具体骗术细节。"
    body = _plan_head(title, window, branch, focus, target)
    body += _plan_tail(branch, tail_extra)
    body = body.replace(
        "| 演练 / 情景 | 见第三节流程 |",
        "| 情景认知 / 角色扮演 | 班级情景游戏、口诀巩固、情绪安抚 |"
    )
    # 防拐补情景活动链占位行（导入 → 设置 → 角色扮演 → 巩固安抚），不套撤离流程
    body = body.replace(
        "| 【待填】 | 主体环节 | 引导员【待填】 | 按分支口径执行（见 references/activity-seeds.md） |",
        "| 【待填】 | 认知导入 | 各班教师 | 绘本图卡讲拒绝要点、求助对象与口诀 |\n"
        "| 【待填】 | 情境设置 | 主持 / 配合教师【待填】 | 讲明是安全游戏；角色就位，情景限定熟悉场地 |\n"
        "| 【待填】 | 角色扮演 | 各班教师 | 拒绝、呼救、求助三步练习；观察幼儿反应 |"
    )
    body = body.replace(
        "| 【待填】 | 集合 / 小结 | 清点员、总指挥 | 与名册核对，缺员立即上报；只记事实与改进点 |",
        "| 【待填】 | 口诀巩固与安抚 | 各班教师 | 口诀儿歌、正强化；情绪安抚收尾，不批评犹豫表现 |"
    )
    return body


def build_summary(title):
    return f"""# {title}

**活动类型**：【待填：防火 / 防震 / 防拐】　**活动日期**：【待填】　**地点**：【待填】
**负责人**：【待填：姓名 / 岗位】　**参与对象**：【待填：班级、幼儿、教职工 / 安保】

## 一、基本信息

- 活动类型：【待填】
- 活动日期、地点：【待填】
- 负责人：【待填】
- 参与班级与对象：【待填】

## 二、定量记录

- 参与幼儿：【待核实：以签到名册为准】人；教职工 / 安保：【待核实】人；涉及班级：【待核实】个。
- 演练 / 情景用时：【待核实】；环节完成情况：【待填：按方案完成 / 部分调整，写明调整】。
- 签到与清点：名册核对情况；缺员及处置（无则写"无"）。

## 三、过程简述

- 宣教内容：【待填】
- 演练 / 情景过程：【待填：按时间顺序写经过】
- 外联 / 家园环节：【待填；未到场不写成已参与】

## 四、顺畅点

- 【待填：组织秩序、动作掌握、配合情况等观察事实】

## 五、问题与改进

- 【待填：现场问题与不足；对应改进措施；不写整体合格 / 达标结论】

## 六、留痕材料归档

| 序号 | 材料 | 归档位置 / 状态 |
|---|---|---|
| 1 | 活动方案 / 通知 | 【待补】 |
| 2 | 教案 / 情景记录 | 【待补】 |
| 3 | 签到表、清点记录 | 【待补】 |
| 4 | 现场照片 | 见第七节 |
| 5 | 家园材料 | 【待补】 |

## 七、现场照片

![照片说明：环节与拍摄时间](【待填：照片文件路径】)

## 八、待核实项

- 【待核实：人数、班级、用时等待名册 / 记录补齐的项目，注明核实人】
"""


def main():
    parser = argparse.ArgumentParser(description="生成园所三防安全活动骨架")
    parser.add_argument("--title", required=True, help="活动名称")
    parser.add_argument("--mode", choices=["plan", "summary"], default="plan", help="方案稿（默认）或总结稿")
    parser.add_argument("--branch", choices=BRANCHES, default="防火", help="分支：防火 / 防震 / 防拐（方案模式）")
    parser.add_argument("--window", default="园内自排", help="时间窗口")
    parser.add_argument("--focus", choices=FOCUSES, default="综合一场", help="本场侧重（方案模式）")
    parser.add_argument("--out", default=None, help="输出路径（默认 名称.html）")
    parser.add_argument("--format", choices=["html", "md"], default="html",
                        help="输出格式：html（默认）或 md（纯文本底稿）")
    args = parser.parse_args()

    if not args.title.strip():
        print("[错误] 请用 --title 提供活动名称（不能为空）", file=sys.stderr)
        return 2

    if args.mode == "summary":
        content = build_summary(args.title.strip())
        note = "总结稿"
    else:
        content = build_plan(args.branch, args.title.strip(), args.window, args.focus)
        note = f"方案稿（{args.branch}）"

    ext = ".html" if args.format == "html" else ".md"
    base = args.out or args.title.strip()
    root, given = os.path.splitext(base)
    if given.lower() in (".md", ".html"):
        base = root
    out = base + ext

    out_dir = os.path.dirname(os.path.abspath(out))
    try:
        os.makedirs(out_dir, exist_ok=True)
        payload = render_markdown(content) if args.format == "html" else content
        with open(out, "w", encoding="utf-8") as f:
            f.write(payload)
    except OSError as e:
        print(f"[错误] 输出文件写入失败：{e}", file=sys.stderr)
        return 2

    print(f"[完成] 已生成骨架：{out}（{note}）")
    if args.format == "html":
        print("[提示] HTML 可直接双击阅读、Ctrl+P 打印或存 PDF；黄色高亮为待填/待核实处")
    print("[下一步] 按 references/ 填充园所事实，再跑 check_plan.py 自检")
    return 0


if __name__ == "__main__":
    sys.exit(main())
