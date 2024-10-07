import numpy as np
import matplotlib.pyplot as plt
import time
from sortedcontainers import SortedList
open_list = []
dist = 99999.0*np.ones((30, 30))
obst = -1*np.ones((30, 30))
toRaise = np.zeros((30, 30))
process = np.zeros((30, 30))
count = 0


def distance_key(List_Element):
    i = List_Element[0]
    j = List_Element[1]
    return dist[i, j]


sorted_distance_list = SortedList(key=distance_key)


def S2IJ(s):
    i = int(s//30)
    j = int(s % 30)
    return i, j


def SetObstacle(i, j):
    obst[i, j] = i*30+j
    dist[i, j] = 0
    process[i, j] = 1
    sorted_distance_list.add([i, j])


def RemoveObstacle(i, j):
    obst[i, j] = -1
    toRaise[i, j] = 1
    dist[i, j] = 99999.0
    process[i, j] = 1
    sorted_distance_list.add([i, j])


def Raise(i, j):
    for ni in [-1, 0, 1]:
        for nj in [-1, 0, 1]:
            if ni == 0 and nj == 0:
                continue

            xi = i + ni
            xj = j + nj
            if xi < 0 or xi >= 30 or xj < 0 or xj >= 30:
                continue

            if (obst[xi, xj] >= 0) and (toRaise[xi, xj] == 0):
                oi, oj = S2IJ(obst[xi, xj])
                zl_oi, zl_oj = S2IJ(obst[oi, oj])
                if (obst[oi, oj] == -1 or (zl_oi != oi) or (zl_oj != oj)):
                    dist[xi, xj] = 99999.0
                    obst[xi, xj] = -1
                    toRaise[xi, xj] = 1

                process[xi, xj] = 1
                sorted_distance_list.add([xi, xj])
    toRaise[i, j] = 0


def Lower(i, j):
    si, sj = S2IJ(obst[i, j])
    for ni in [-1, 0, 1]:
        for nj in [-1, 0, 1]:
            if ni == 0 and nj == 0:
                continue

            xi = i + ni
            xj = j + nj
            if xi < 0 or xi >= 30 or xj < 0 or xj >= 30:
                continue
            if toRaise[xi, xj] == 0:
                zl_si, zl_sj = S2IJ(obst[si, sj])
                d = np.sqrt((si-xi)*(si-xi)+(sj-xj)*(sj-xj))
                if ((d < dist[xi, xj]) or (obst[xi, xj] < 0)) and (zl_si == si) and (zl_sj == sj):
                    dist[xi, xj] = d
                    obst[xi, xj] = si*30+sj
                    process[xi, xj] = 1
                    sorted_distance_list.add([xi, xj])


def Pops():  # get the element with max distance
    max_index = -1

    if len(sorted_distance_list) <= 0:
        return False, max_index
    else:
        max_element = sorted_distance_list.pop(-1)
        i = max_element[0]
        j = max_element[1]
        max_index = i*30+j
        return True, max_index


def UpdateDistanceMap():
    not_empty, s = Pops()
    while not_empty:
        i, j = S2IJ(s)
        if toRaise[i, j] == 1:
            Raise(i, j)
            # print("raise")
        else:
            if obst[i, j] >= 0:
                Lower(i, j)
                # print("lower")
        not_empty, s = Pops()
        # plt.clf()  # 清除当前图形，不再叠加图像
        # plt.imshow(dist, cmap='viridis', vmin=0, vmax=25)  # 可以设置不同的 colormap
        # plt.colorbar()  # 添加颜色条以便于理解距离值
        # plt.pause(0.001)  # 暂停以便查看更新的图像


plt.ion()  # 开启交互模式
StartTime = time.time()
SetObstacle(15, 15)
SetObstacle(16, 15)
SetObstacle(14, 15)
SetObstacle(14, 16)
SetObstacle(15, 16)
SetObstacle(16, 16)
SetObstacle(25, 15)
SetObstacle(10, 25)
SetObstacle(25, 25)
SetObstacle(5, 5)
UpdateDistanceMap()
RemoveObstacle(15, 15)
RemoveObstacle(14, 16)
RemoveObstacle(25, 25)
UpdateDistanceMap()

print("Time:", time.time() - StartTime, "seconds")

plt.imshow(dist)
plt.show()
plt.colorbar()
plt.pause(5)