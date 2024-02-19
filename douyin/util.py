flag=True
def color_little_change(color, i):
    global flag
    if flag:
        if color[0]+i > 255:
            if color[1]+i > 255:
                if color[2]+i > 255:
                    flag=False
                    color[0]-=i
                else:
                    color[2] += i
            else:
                color[1] += i
        else:
            color[0] += i
        return color
    else:
        if color[0]-i<0:
            if color[1]-i<0:
                if color[2]-i<0:
                    flag = True
                    color[0]+=i
                else:
                    color[2] -= i
            else:
                color[1] -= i
        else:
            color[0] -= i

        return color