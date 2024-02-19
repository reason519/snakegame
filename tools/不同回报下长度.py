import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd


df=pd.read_csv("../logs/back/snake.csv")
df1=pd.read_csv("../logs/back/snake_linefun1.csv")
df2=pd.read_csv("../logs/back/snake_fun1.csv")

x=df["elapse"]
y=df["snakelen"]
fig, ax = plt.subplots()
# ax.plot(x, y, linewidth=2.0)
y_sum=0
x1=[]
y1=[]
for i,data in enumerate(y):
    y_sum += data
    if i%20==0:
        y1.append(y_sum/20)
        y_sum=0
        x1.append(i)


ax.plot(x1, y1, linewidth=2.0,label="r=-2")

x=df1["elapse"]
y=df1["snakelen"]
# ax.plot(x, y, linewidth=2.0)
y_sum=0
x1=[]
y1=[]
for i,data in enumerate(y):
    y_sum += data
    if i%20==0:
        y1.append(y_sum/20)
        y_sum=0
        x1.append(i)
ax.plot(x1, y1, linewidth=2.0,label="r=$-(M-l(s))*0.1$")

x=df2["elapse"]
y=df2["snakelen"]
# ax.plot(x, y, linewidth=2.0)
y_sum=0
x2=[]
y2=[]
for i,data in enumerate(y):
    y_sum += data
    if i%20==0:
        y2.append(y_sum/20)
        y_sum=0
        x2.append(i)
ax.plot(x2, y2, linewidth=2.0,label="$r=-(M-l(s_{0}))^\\frac{M-l(s)}{M-l(s_{0})}*0.1$")
#
ax.legend()
plt.ylabel("Snake Length")
plt.xlabel("Number of game played")
plt.show()

