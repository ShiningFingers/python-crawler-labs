# ============================================================
# 学生成绩管理系统 —— Python 内置 tkinter 版
# ------------------------------------------------------------
# 课程实验项目：单文件、零第三方库、Python 3.8+ 直接运行
#
# 【功能清单】
#   F1 添加数据：录入学号/姓名/三科成绩，自动计算总分与平均分
#   F2 查询数据：学号精确查询 + 姓名模糊查询，命中行黄色高亮并自动回填
#   F3 修改数据：双入口（点表格行 / 查询命中自动选中）→ 回填 → 提交更新
#   F4 删除数据：选中单行 → 二次确认 → 移除
#   F5 排序功能：按 总分/平均分/语文/数学/英语（附加：学号/姓名）升序或降序
#   F6 友好提示：所有操作均有 messagebox 反馈 + 底部状态栏文字
#   F7 演示数据：一键填充 5 条示例记录，方便录制讲解视频
#   F8 拓展功能：手动保存至 CSV / 从 CSV 加载（加分项）
#
# 【代码分层】（写实验报告 / 录视频时按这 6 层讲）
#   第 0 层  全局配置与常量
#   第 1 层  工具与校验函数层（纯函数，不依赖界面，可独立测试）
#   第 2 层  数据访问层（对 students 列表的增删改查，纯函数）
#   第 3 层  界面搭建层（StudentSystem.build_ui 及若干子函数）
#   第 4 层  事件处理层（按钮 / 表格回调）
#   第 5 层  拓展功能层（CSV 读写、演示数据）
#
# 【关键设计】
#   * 内存列表 self.students 是唯一数据源，表格只是它的"投影"。
#   * 学号作为主键，贯穿"高亮 / 选中 / 编辑"三处，
#     彻底避开 Treeview 行 id 刷新后失效的坑。
# ============================================================

import os
import csv
import math
import tkinter as tk
from tkinter import messagebox, ttk


# ============================================================
# 第 0 层：全局配置与常量（只改这里即可增减科目）
# ============================================================
COURSES = ['语文', '数学', '英语']        # 科目列表，可自由增删
SCORE_MIN = 0                             # 成绩下限
SCORE_MAX = 100                           # 成绩上限
SID_LENGTH = 8                            # 学号必须是 8 位纯数字
AVG_DIGITS = 2                            # 平均分保留小数位数
FILE_NAME = 'students.csv'                # 拓展功能保存的文件名

# 记录字段下标（依据科目数量自动推算，避免硬编码）
# 记录格式：[学号, 姓名, 科目1, 科目2, ..., 总分, 平均分]
IDX_SID = 0                               # 学号所在下标
IDX_NAME = 1                              # 姓名所在下标
SCORE_START = 2                           # 第一门成绩起始下标
TOTAL_IDX = SCORE_START + len(COURSES)    # 总分下标
AVG_IDX = TOTAL_IDX + 1                   # 平均分下标
N_FIELDS = AVG_IDX + 1                    # 一条记录的总字段数


# ============================================================
# 第 1 层：工具与校验函数层（纯逻辑，不依赖界面，方便测试）
# ============================================================

def validate_sid(text):
    """校验学号：非空 + 纯数字 + 恰好 SID_LENGTH 位。
    返回 (是否合法, 学号字符串 或 错误原因)。"""
    if text is None or str(text).strip() == '':
        return False, '学号不能为空！'
    sid = str(text).strip()
    if not sid.isdigit():
        return False, '学号必须是纯数字！'
    if len(sid) != SID_LENGTH:
        return False, f'学号必须是 {SID_LENGTH} 位数字（当前 {len(sid)} 位）！'
    return True, sid


def validate_score(text):
    """校验单个成绩输入。

    参数：text —— 输入框里的原始文本
    返回：(是否合法, 数值 或 错误原因字符串)

    规则：
      1) 不能为空
      2) 必须能转成浮点数
      3) 必须是有限数（挡住 nan / inf）
      4) 数值必须在 [SCORE_MIN, SCORE_MAX] 之间
    """
    if text is None or str(text).strip() == '':
        return False, '成绩不能为空！'
    try:
        value = float(text)
    except (TypeError, ValueError):
        return False, '成绩必须是数字！'
    # float('nan') 不报错、也不触发下面的范围判断，必须单独拦掉
    if not math.isfinite(value):
        return False, '成绩必须是有效数字（不能是 nan / inf）！'
    if value < SCORE_MIN or value > SCORE_MAX:
        return False, f'成绩必须在 {SCORE_MIN}~{SCORE_MAX} 之间！'
    return True, value


def calc_total_avg(scores):
    """根据各科成绩列表计算 (总分, 平均分)。

    参数：scores —— 每门课的成绩（float 列表）
    返回：(总分 float, 平均分 float，保留 AVG_DIGITS 位小数)
    """
    total = sum(scores)
    avg = round(total / len(scores), AVG_DIGITS)
    return total, avg


def make_record(sid, name, scores):
    """把 学号 + 姓名 + 各科成绩 拼成一条完整记录，自动算总分/平均分。

    返回：[学号, 姓名, 各科..., 总分, 平均分]
    """
    total, avg = calc_total_avg(scores)
    return [sid, name] + list(scores) + [total, avg]


def fmt_num(value, digits=None):
    """把数值格式化成表格/CSV 显示用的字符串。

    digits=None ：整数不带小数点（88.0 → '88'），小数原样（88.5 → '88.5'）—— 用于各科成绩、总分
    digits=2    ：固定保留 2 位小数（88 → '88.00'）                        —— 用于平均分
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)
    if digits is not None:
        return f'{num:.{digits}f}'
    if num == int(num):
        return str(int(num))
    return f'{num:g}'


def sid_sort_key(sid):
    """学号排序键。

    纯数字学号按数值大小排（避免 '10' < '2' 这种字符串排序错误）；
    非纯数字学号按字符串排。用元组第一位区分两类，互不干扰。
    """
    text = str(sid)
    if text.isdigit():
        return (0, int(text))
    return (1, text)


# ============================================================
# 第 2 层：数据访问层（对 students 列表的增删改查，纯函数）
# 这些函数不碰界面，方便单独测试，也让主类更清爽
# ============================================================

def find_index_by_sid(students, sid):
    """按学号查找记录下标，找不到返回 -1。"""
    for i, stu in enumerate(students):
        if stu[IDX_SID] == sid:
            return i
    return -1


def is_sid_exists(students, sid, exclude_sid=None):
    """判断学号是否已存在。

    exclude_sid：修改场景下排除"自己"，避免改自己时报重复。
    """
    for stu in students:
        if stu[IDX_SID] == sid and stu[IDX_SID] != exclude_sid:
            return True
    return False


# ============================================================
# 第 3~5 层：主界面类
# ============================================================

class StudentSystem:
    """学生成绩管理系统主类：负责界面搭建 + 事件响应 + 数据维护。"""

    # --------------------------------------------------------
    # 3.0 初始化
    # --------------------------------------------------------
    def __init__(self):
        # ---------- 主窗口 ----------
        self.window = tk.Tk()
        self.window.title('学生成绩管理系统')
        self.window.geometry('900x660')            # 固定窗口大小
        self.window.resizable(True, True)          # 允许自由缩放
        self.window.minsize(860, 620)              # 设置窗口最小尺寸

        # ---------- 核心数据 ----------
        self.students = []          # 内存列表，唯一数据源
        self.current_sid = None     # 当前正在编辑的学生学号（主键，不用行号）
        self._suppress_select = False   # 抑制 <<TreeviewSelect>> 回填的标志位

        # ---------- 排序字段 → 记录下标 的映射（只建一次） ----------
        self.sort_field_map = {'学号': IDX_SID, '姓名': IDX_NAME,
                               '总分': TOTAL_IDX, '平均分': AVG_IDX}
        for i, course in enumerate(COURSES):
            self.sort_field_map[course] = SCORE_START + i

        # ---------- 搭界面 + 首次刷新 ----------
        self.build_ui()
        self.refresh_table()

    # ========================================================
    # 3.1 界面搭建（拆成若干子函数，报告里好讲）
    # ========================================================
    def build_ui(self):
        """搭建整体界面：按 标题 → 输入区 → 按钮区 → 查询区 → 排序区 → 表格 → 状态栏 顺序组装。"""
        self._build_title()
        self._build_input_area()
        self._build_button_area()
        self._build_query_area()
        self._build_sort_area()
        self._build_table_area()
        self._build_status_bar()

    def _build_title(self):
        """顶部标题。"""
        tk.Label(self.window, text='学生成绩管理系统',
                 font=('微软雅黑', 18, 'bold'), fg='navy').pack(pady=6)

    def _build_input_area(self):
        """输入区：学号 / 姓名 / 各科成绩。"""
        frame = tk.LabelFrame(self.window, text=' 数据录入 / 编辑 ',
                              font=('微软雅黑', 10))
        frame.pack(fill=tk.X, padx=10, pady=4)

        # 用字典保存输入框，便于统一取值、清空
        self.entry_scores = {}      # key = 科目名, value = 该科目的 Entry

        # 学号 + 姓名
        tk.Label(frame, text='学号:').grid(row=0, column=0, padx=(6, 2), pady=8)
        self.entry_sid = tk.Entry(frame, width=10)
        self.entry_sid.grid(row=0, column=1, padx=(0, 10))

        tk.Label(frame, text='姓名:').grid(row=0, column=2, padx=(2, 2))
        self.entry_name = tk.Entry(frame, width=10)
        self.entry_name.grid(row=0, column=3, padx=(0, 10))

        # 各科成绩：从第 4 列开始，标签与输入框交替排布
        col = 4
        for course in COURSES:
            tk.Label(frame, text=f'{course}:').grid(row=0, column=col, padx=(2, 2))
            e = tk.Entry(frame, width=8)
            e.grid(row=0, column=col + 1, padx=(0, 8))
            self.entry_scores[course] = e
            col += 2

        # 回车快捷操作：在【顶部输入框】里按 Enter 相当于点"添加"。
        # 注意：必须有 return 'break' 阻断传播，且只能绑在输入框上，不能绑整窗，
        #       否则在查询框按 Enter 时会先触发"查询"再误触发"添加"。
        def _enter_add(_event):
            self.do_add()
            return 'break'

        for widget in ([self.entry_sid, self.entry_name]
                       + list(self.entry_scores.values())):
            widget.bind('<Return>', _enter_add)

    def _build_button_area(self):
        """按钮区：添加 / 修改 / 删除 / 清空输入 / 保存CSV / 加载CSV。"""
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.X, padx=10, pady=4)

        tk.Button(frame, text='➕ 添加', command=self.do_add,
                  width=10, bg='lightblue').pack(side=tk.LEFT, padx=3)
        tk.Button(frame, text='✏️ 修改', command=self.do_modify,
                  width=10, bg='lightyellow').pack(side=tk.LEFT, padx=3)
        tk.Button(frame, text='🗑️ 删除', command=self.do_delete,
                  width=10, bg='lightcoral').pack(side=tk.LEFT, padx=3)
        tk.Button(frame, text='🧹 清空输入', command=self.clear_input,
                  width=10).pack(side=tk.LEFT, padx=3)

        # CSV 拓展功能放右侧
        tk.Button(frame, text='💾 保存CSV', command=self.save_csv,
                  width=10).pack(side=tk.RIGHT, padx=3)
        tk.Button(frame, text='📂 加载CSV', command=self.load_csv,
                  width=10).pack(side=tk.RIGHT, padx=3)

    def _build_query_area(self):
        """查询区：一个输入框同时支持"学号精确"和"姓名模糊"。"""
        frame = tk.LabelFrame(self.window, text=' 查询 ',
                              font=('微软雅黑', 10))
        frame.pack(fill=tk.X, padx=10, pady=4)

        tk.Label(frame, text='输入学号或姓名:').pack(side=tk.LEFT, padx=(6, 4))
        self.entry_query = tk.Entry(frame, width=25)
        self.entry_query.pack(side=tk.LEFT, padx=4)

        # 查询框里按 Enter = 查询；return 'break' 阻断传播，避免误触发"添加"
        def _enter_query(_event):
            self.do_query()
            return 'break'

        self.entry_query.bind('<Return>', _enter_query)

        tk.Button(frame, text='🔍 查询', command=self.do_query,
                  bg='lightgreen', width=8).pack(side=tk.LEFT, padx=4)
        tk.Button(frame, text='💡 清除高亮', command=self.clear_highlight,
                  width=10).pack(side=tk.LEFT, padx=4)

    def _build_sort_area(self):
        """排序区：字段下拉 + 方向下拉 + 排序按钮 + 演示数据按钮。"""
        frame = tk.LabelFrame(self.window, text=' 排序 ',
                              font=('微软雅黑', 10))
        frame.pack(fill=tk.X, padx=10, pady=4)

        tk.Label(frame, text='按字段:').pack(side=tk.LEFT, padx=(6, 2))
        sort_fields = ['学号', '姓名'] + COURSES + ['总分', '平均分']
        self.cmb_field = ttk.Combobox(frame, values=sort_fields,
                                      state='readonly', width=8)
        self.cmb_field.current(0)
        self.cmb_field.pack(side=tk.LEFT, padx=4)

        tk.Label(frame, text='方向:').pack(side=tk.LEFT, padx=(8, 2))
        self.cmb_order = ttk.Combobox(frame, values=['升序', '降序'],
                                      state='readonly', width=6)
        self.cmb_order.current(0)
        self.cmb_order.pack(side=tk.LEFT, padx=4)

        tk.Button(frame, text='📊 排序', command=self.do_sort,
                  bg='lightcyan', width=8).pack(side=tk.LEFT, padx=4)
        tk.Button(frame, text='🎲 演示数据', command=self.fill_demo,
                  width=10).pack(side=tk.RIGHT, padx=4)

    def _build_table_area(self):
        """数据表格区：ttk.Treeview + 垂直滚动条。"""
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 表格列 = 学号 + 姓名 + 各科 + 总分 + 平均分
        columns = (('sid', 'name')
                   + tuple(f's{i}' for i in range(len(COURSES)))
                   + ('total', 'avg'))
        self.tree = ttk.Treeview(frame, columns=columns, show='headings',
                                 yscrollcommand=scrollbar.set, height=13,
                                 selectmode='browse')   # browse = 只允许单选
        scrollbar.config(command=self.tree.yview)

        # 列标题与列宽
        headings = ['学号', '姓名'] + COURSES + ['总分', '平均分']
        for col, hd in zip(columns, headings):
            self.tree.heading(col, text=hd, anchor=tk.CENTER)
            width = 110 if col == 'name' else 80
            self.tree.column(col, width=width, minwidth=60, anchor=tk.CENTER, stretch=True)

        self.tree.pack(fill=tk.BOTH, expand=True)
        # 点击某行 → 自动回填顶部输入框
        self.tree.bind('<<TreeviewSelect>>', self.on_select_row)

        # 高亮标签样式：亮黄色背景（只配置一次，放在搭建阶段）
        self.tree.tag_configure('highlight', background='yellow')

    def _build_status_bar(self):
        """底部状态栏：显示操作结果文字提示。"""
        self.status = tk.Label(
            self.window,
            text='提示：顶部输入信息 → 点"添加"；点击表格某行 → 自动回填后可修改。',
            fg='gray', anchor='w')
        self.status.pack(fill=tk.X, padx=10, pady=4)

    # ========================================================
    # 3.2 表格刷新 / 高亮（按【学号】高亮，不依赖易变的行 id）
    # ========================================================
    def _record_to_display(self, stu):
        """把一条内存记录转成表格显示用的字符串列表。"""
        values = [stu[IDX_SID], stu[IDX_NAME]]
        values += [fmt_num(v) for v in stu[SCORE_START:TOTAL_IDX]]   # 各科成绩
        values += [fmt_num(stu[TOTAL_IDX]),                          # 总分（整数不带 .0）
                   fmt_num(stu[AVG_IDX], AVG_DIGITS)]                # 平均分（固定 2 位）
        return values

    def _select_item(self, item_id):
        """选中指定行并滚动到可见区域（会触发 <<TreeviewSelect>> → 回填）。"""
        self.tree.selection_set(item_id)
        self.tree.focus(item_id)
        self.tree.see(item_id)

    def refresh_table(self, highlight_sids=None, keep_sid=None):
        """重绘表格。

        参数：
          highlight_sids —— 需要黄色高亮的【学号】集合（默认不高亮）
          keep_sid       —— 重绘后仍要保持选中的【学号】（默认不选中）
        """
        # 清空旧数据
        self.tree.delete(*self.tree.get_children())

        highlight_sids = highlight_sids or set()
        target_item = None

        for stu in self.students:
            item_id = self.tree.insert('', tk.END, values=self._record_to_display(stu))
            # 按学号高亮：与行 id 无关，刷新多少次都稳定
            if stu[IDX_SID] in highlight_sids:
                self.tree.item(item_id, tags=('highlight',))
            # 记录需要恢复选中的那一行
            if keep_sid is not None and stu[IDX_SID] == keep_sid:
                target_item = item_id

        if target_item is not None:
            self._select_item(target_item)

    def clear_highlight(self):
        """清除所有高亮，并清空查询框。"""
        self.entry_query.delete(0, tk.END)
        self.refresh_table(keep_sid=self.current_sid)
        self.status.config(text='已清除高亮显示。')

    # ========================================================
    # 4.1 输入框取值 / 清空
    # ========================================================
    def collect_input(self):
        """读取输入框内容，返回 (学号, 姓名, 科目成绩列表)。

        若任一字段非法，弹窗提示并返回 (None, None, None)。
        注意：这里只做"格式/范围"校验，学号唯一性由 添加/修改 各自判断。
        """
        sid = self.entry_sid.get().strip()
        name = self.entry_name.get().strip()

        ok, result = validate_sid(self.entry_sid.get())
        if not ok:
            messagebox.showerror('错误', result)
            return None, None, None
        sid = result
        if not name:
            messagebox.showerror('错误', '姓名不能为空！')
            return None, None, None

        scores = []
        for course in COURSES:
            ok, result = validate_score(self.entry_scores[course].get().strip())
            if not ok:
                messagebox.showerror('错误', f'【{course}】{result}')
                return None, None, None
            scores.append(result)
        return sid, name, scores

    def clear_input(self):
        """清空顶部所有输入框，取消当前编辑状态与表格选中。"""
        self.entry_sid.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        for e in self.entry_scores.values():
            e.delete(0, tk.END)
        self.current_sid = None

        # 取消表格选中；用标志位屏蔽事件，避免触发无意义的回填
        self._suppress_select = True
        sel = self.tree.selection()
        if sel:
            self.tree.selection_remove(*sel)
        self._suppress_select = False

        self.status.config(text='输入内容已清空。')

    # ========================================================
    # 4.2 选中行回填（修改的"入口 1"）
    # ========================================================
    def on_select_row(self, _event=None):
        """表格选中某行时，把该行内容回填到顶部输入框，便于直接修改。"""
        if self._suppress_select:
            return
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], 'values')
        if not values or len(values) < N_FIELDS:
            return

        sid = str(values[IDX_SID])
        name = str(values[IDX_NAME])

        self.entry_sid.delete(0, tk.END)
        self.entry_sid.insert(0, sid)
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, name)
        # 只回填各科成绩，总分/平均分由系统重算
        for i, course in enumerate(COURSES):
            e = self.entry_scores[course]
            e.delete(0, tk.END)
            e.insert(0, str(values[SCORE_START + i]))

        self.current_sid = sid       # 记住正在编辑的学号
        self.status.config(text=f'已选中 {name}（学号 {sid}），可直接修改后点"修改"。')

    # ========================================================
    # 4.3 添加数据（F1）
    # ========================================================
    def do_add(self):
        """读取输入 → 校验 → 学号唯一则追加记录并刷新表格。"""
        sid, name, scores = self.collect_input()
        if sid is None:
            return                                  # 输入非法，已弹窗

        if is_sid_exists(self.students, sid):
            messagebox.showerror('错误', f'学号 {sid} 已存在，不能重复添加！')
            return

        self.students.append(make_record(sid, name, scores))
        self.refresh_table()
        self.clear_input()
        messagebox.showinfo('成功', f'已添加学生：{name}（学号 {sid}），总分/平均分已自动计算。')
        self.status.config(text=f'成功添加 {name}（学号 {sid}）。')

    # ========================================================
    # 4.4 修改数据（F3）
    # ========================================================
    def do_modify(self):
        """把输入框内容更新到当前选中的学生记录上（复用添加时的校验逻辑）。"""
        if self.current_sid is None:
            messagebox.showerror('提示', '请先点击表格选中要修改的学生，或先用查询定位！')
            return

        sid, name, scores = self.collect_input()
        if sid is None:
            return

        idx = find_index_by_sid(self.students, self.current_sid)
        if idx == -1:
            messagebox.showerror('错误', '原记录不存在，可能已被删除，请刷新后重试！')
            self.current_sid = None
            return

        # 学号唯一性：允许与自己相同的学号，但不能撞其他学生
        if is_sid_exists(self.students, sid, exclude_sid=self.current_sid):
            messagebox.showerror('错误', f'学号 {sid} 已被其他学生使用！')
            return

        self.students[idx] = make_record(sid, name, scores)
        self.refresh_table()
        self.clear_input()
        messagebox.showinfo('成功', f'学生 {name}（学号 {sid}）信息已更新！')
        self.status.config(text=f'已更新 {name}（学号 {sid}）。')

    # ========================================================
    # 4.5 删除数据（F4）
    # ========================================================
    def do_delete(self):
        """删除表格当前选中的一行（带确认弹窗防误删）。"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror('提示', '请先在表格中选中要删除的学生！')
            return

        values = self.tree.item(selected[0], 'values')
        sid, name = str(values[IDX_SID]), str(values[IDX_NAME])

        if not messagebox.askyesno('确认删除',
                                   f'确定要删除学生【{name}】（学号 {sid}）吗？\n删除后不可恢复！'):
            return

        self.students = [s for s in self.students if s[IDX_SID] != sid]
        self.clear_input()
        self.refresh_table()
        messagebox.showinfo('成功', f'学生 {name}（学号 {sid}）已删除。')
        self.status.config(text=f'已删除 {name}（学号 {sid}）。')

    # ========================================================
    # 4.6 查询数据（F2）：学号精确 + 姓名模糊
    # ========================================================
    def do_query(self):
        """根据关键字查询：学号精确匹配 或 姓名包含关键字。

        命中后：黄色高亮所有命中行 + 自动选中第一条（触发回填，方便直接改）。
        数据源统一用 self.students，不再读 Treeview。
        """
        key = self.entry_query.get().strip()
        if not key:
            messagebox.showerror('提示', '请输入学号或姓名！')
            return
        if not self.students:
            messagebox.showinfo('提示', '当前没有任何学生数据！')
            return

        # 收集命中的学号（学号精确 或 姓名模糊）
        hit_sids = [stu[IDX_SID] for stu in self.students
                    if stu[IDX_SID] == key or key in stu[IDX_NAME]]

        if not hit_sids:
            messagebox.showinfo('未找到',
                                f'没有找到与 "{key}" 匹配的学生。\n（学号精确匹配 / 姓名模糊匹配）')
            self.status.config(text=f'未查询到 "{key}"。')
            return

        # 高亮 + 选中第一条 → 自动回填输入框（修改的第二入口）
        self.refresh_table(highlight_sids=set(hit_sids), keep_sid=hit_sids[0])
        self.status.config(text=f'查询到 {len(hit_sids)} 条匹配记录，已高亮并选中第一条。')

    # ========================================================
    # 4.7 排序（F5）
    # ========================================================
    def do_sort(self):
        """按所选字段与方向排序，一键刷新表格（排序后保持原选中行）。"""
        if not self.students:
            messagebox.showinfo('提示', '当前没有学生数据，无法排序！')
            return

        field = self.cmb_field.get()
        reverse = (self.cmb_order.get() == '降序')
        index = self.sort_field_map[field]

        if field == '学号':
            key_func = lambda stu: sid_sort_key(stu[index])
        elif field == '姓名':
            key_func = lambda stu: str(stu[index])
        else:
            key_func = lambda stu: float(stu[index])

        self.students.sort(key=key_func, reverse=reverse)

        # 排序后仍选中原来那一行（学号不变，所以能定位到）
        self.refresh_table(keep_sid=self.current_sid)
        self.status.config(
            text=f'已按【{field}】【{"降序" if reverse else "升序"}】排序。')

    # ========================================================
    # 5.1 演示数据（F7，录视频用）
    # ========================================================
    def fill_demo(self):
        """一键填充 5 条示例数据，便于快速演示增删改查与排序。"""
        if self.students:
            messagebox.showinfo('提示', '当前已有数据，为避免学号冲突已跳过填充。')
            return

        demo = [
            ('20210001', '张三',   [88, 92, 85]),
            ('20210002', '李四',   [75, 68, 90]),
            ('20210003', '王五',   [95, 88, 96]),
            ('20210004', '赵六',   [60, 72, 58]),
            ('20210005', '王小明', [70, 80, 66]),
        ]
        for sid, name, scores in demo:
            if not is_sid_exists(self.students, sid):
                self.students.append(make_record(sid, name, [float(s) for s in scores]))

        self.refresh_table()
        self.status.config(text='已填充 5 条演示数据。')

    # ========================================================
    # 5.2 拓展：保存到 CSV / 从 CSV 加载（F8）
    # ========================================================
    def save_csv(self):
        """把内存数据保存到 CSV 文件（与 py 同级目录），可用 Excel/记事本打开。"""
        if not self.students:
            messagebox.showinfo('提示', '当前没有数据可保存！')
            return
        try:
            header = ['学号', '姓名'] + COURSES + ['总分', '平均分']
            with open(FILE_NAME, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for stu in self.students:
                    writer.writerow(self._record_to_display(stu))
            messagebox.showinfo('成功', f'已保存到文件：\n{os.path.abspath(FILE_NAME)}')
            self.status.config(text=f'数据已保存到 {FILE_NAME}。')
        except Exception as e:
            messagebox.showerror('错误', f'保存失败：{e}')

    def load_csv(self):
        """从 CSV 文件读取学生数据并追加显示（学号重复或成绩非法则跳过该行）。

        CSV 属于"外部输入"，这里同样走 validate_score 做 0~100 校验，
        避免手工改过的文件把非法数据带进内存。
        """
        if not os.path.exists(FILE_NAME):
            messagebox.showerror('错误', f'文件 {FILE_NAME} 不存在，请先执行"保存CSV"！')
            return

        min_cols = SCORE_START + len(COURSES)   # 至少要有 学号+姓名+各科
        try:
            new_list = self.students[:]
            existing = {s[IDX_SID] for s in new_list}
            loaded = skipped = 0

            with open(FILE_NAME, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or len(row) < min_cols:
                        continue
                    sid = row[IDX_SID].strip()
                    name = row[IDX_NAME].strip()
                    if row[IDX_SID].strip() == '学号':          # 跳过表头
                        continue
                    ok, result = validate_sid(row[IDX_SID])
                    if not ok or not name or result in existing:
                        skipped += 1
                        continue
                    sid = result
                    # 逐科校验范围
                    scores, ok_all = [], True
                    for i in range(len(COURSES)):
                        ok, val = validate_score(row[SCORE_START + i])
                        if not ok:
                            ok_all = False
                            break
                        scores.append(val)
                    if not ok_all:
                        skipped += 1
                        continue

                    new_list.append(make_record(sid, name, scores))
                    existing.add(sid)
                    loaded += 1

            self.students = new_list
            self.refresh_table()
            messagebox.showinfo('成功', f'从 CSV 加载了 {loaded} 条新记录（跳过 {skipped} 行）。')
            self.status.config(text=f'已从 {FILE_NAME} 加载 {loaded} 条记录。')
        except Exception as e:
            messagebox.showerror('错误', f'加载失败：{e}')

    # ========================================================
    # 3.3 启动
    # ========================================================
    def run(self):
        """启动应用主循环。"""
        self.window.mainloop()


# ============================================================
# 程序入口
# ============================================================
if __name__ == '__main__':
    app = StudentSystem()
    app.run()