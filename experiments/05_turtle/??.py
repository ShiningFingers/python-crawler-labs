# 姓名：刘浩宇
import turtle

# 设置窗口
turtle.title("奥运五环 - 刘浩宇")
turtle.bgcolor("white")
turtle.pensize(8)
turtle.speed(5)

# 1. 蓝色环
turtle.pencolor("blue")
turtle.penup()
turtle.goto(-110, 0)
turtle.pendown()
turtle.circle(50)

# 2. 黑色环
turtle.pencolor("black")
turtle.penup()
turtle.goto(0, 0)
turtle.pendown()
turtle.circle(50)

# 3. 红色环
turtle.pencolor("red")
turtle.penup()
turtle.goto(110, 0)
turtle.pendown()
turtle.circle(50)

# 4. 黄色环
turtle.pencolor("yellow")
turtle.penup()
turtle.goto(-55, -50)
turtle.pendown()
turtle.circle(50)

# 5. 绿色环
turtle.pencolor("green")
turtle.penup()
turtle.goto(55, -50)
turtle.pendown()
turtle.circle(50)

# ✨ 写上名字
turtle.pencolor("black")
turtle.penup()
turtle.goto(0, -130)              # 定位到五环下方中央
turtle.pendown()
turtle.write("刘浩宇", align="center",
             font=("微软雅黑", 24, "bold"))

# 完成
turtle.hideturtle()
turtle.done()