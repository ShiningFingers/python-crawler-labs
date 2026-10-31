#显示文字
import tkinter                       # ① 搬工具箱
top = tkinter.Tk()                   # ② 创建空白窗口
label1 = tkinter.Label(top,          # ③ 创建一个"标签"（文字）
                       text='在窗体中显示输出内容!')
label1.pack()                        # ④ 把标签放到窗口上
top.mainloop()                       # ⑤ 保持窗口显示

#显示图片
import tkinter                       # ① 搬工具箱
top = tkinter.Tk()                   # ② 创建空白窗口
img = tkinter.PhotoImage(file='dog.gif')  # ③ 加载图片（仅支持GIF！）
label1 = tkinter.Label(top,          # ④ 创建一个"标签"，里面放图片
                       image=img,
                       height=390,
                       width=330)
label1.pack()                        # ⑤ 把标签（图片）摆上去
top.mainloop()                       # ⑥ 保持窗口显示