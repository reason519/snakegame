import matplotlib.pyplot as plt
import math
import numpy as np

grid_size=64
snake_size=3
max_growth=grid_size-snake_size
reward=-math.pow(max_growth,(grid_size-snake_size)/max_growth)
y=[-math.pow(max_growth,(grid_size-i)/max_growth)*0.1 for i in range(3,grid_size+1)]
y1=[-(grid_size-i)*0.1 for i in range(3,grid_size+1)]
y2=[-2 for i in range(3,grid_size+1)]
x = np.linspace(0, grid_size-snake_size, grid_size+1-snake_size)

# plot
fig, ax = plt.subplots()
ax.plot(x, y2, linewidth=2.0,label="r=-2")
ax.plot(x, y1, linewidth=2.0,label="r=$-(M-l(s))*0.1$")
ax.plot(x, y, linewidth=2.0,label="$r=-(M-l(s_{0}))^\\frac{M-l(s)}{M-l(s_{0})}*0.1$")
ax.legend()
plt.xlabel("Grid Size")
plt.ylabel("Rewards")
# ax.plot(x, y1, linewidth=2.0)
plt.show()