import numpy as np
import matplotlib.pyplot as plt
import time
from sortedcontainers import SortedList
open_list = []
dist = 99999.0*np.ones((30, 30))
obst = -1*np.ones((30, 30))
toRaise = np.zeros((30, 30))
sqrt_map = np.zeros((30, 30))
divider = []
divider_map = -1*np.ones((30, 30))
voronoi_map = np.zeros((30, 30))
pop_index = 0  # 0 for pop front.-1 for pop back

for i in range(30):
    for j in range(30):
        sqrt_map[i, j] = np.sqrt(i**2 + j**2)


def distance_key(List_Element):
    i = List_Element[0]
    j = List_Element[1]
    return dist[i, j]


sorted_distance_list = SortedList(key=distance_key)
pruneQueue = SortedList(key=distance_key)


def S2IJ(s):
    i = int(s//30)
    j = int(s % 30)
    return i, j


def SetObstacle(i, j):
    obst[i, j] = i*30+j
    dist[i, j] = 0
    voronoi_map[i, j] = 1
    sorted_distance_list.add([i, j])


# def RemoveObstacle(i, j):
#     obst[i, j] = -1
#     toRaise[i, j] = 1
#     dist[i, j] = 99999.0
#     sorted_distance_list.add([i, j])


# def Raise(i, j):
#     for ni in [-1, 0, 1]:
#         for nj in [-1, 0, 1]:
#             if ni == 0 and nj == 0:
#                 continue

#             xi = i + ni
#             xj = j + nj
#             if xi < 0 or xi >= 30 or xj < 0 or xj >= 30:
#                 continue

#             if (obst[xi, xj] >= 0) and (toRaise[xi, xj] == 0):
#                 oi, oj = S2IJ(obst[xi, xj])
#                 zl_oi, zl_oj = S2IJ(obst[oi, oj])
#                 if (obst[oi, oj] == -1 or (zl_oi != oi) or (zl_oj != oj)):
#                     dist[xi, xj] = 99999.0
#                     obst[xi, xj] = -1
#                     toRaise[xi, xj] = 1

#                 sorted_distance_list.add([xi, xj])
#     toRaise[i, j] = 0

def RemoveObstacle(i, j):
    # obst[i, j] = -1
    toRaise[i, j] = 1
    # dist[i, j] = 99999.0
    sorted_distance_list.add([i, j])


def Raise(i, j):
    obs_index = obst[i, j]
    obs_i, obs_j = S2IJ(obs_index)
    if i == obs_i and j == obs_j:
        for index_i in range(30):
            for index_j in range(30):
                if obst[index_i, index_j] == obs_index:
                    dist[index_i, index_j] = 99999.0
                    obst[index_i, index_j] = -1
                if divider_map[index_i, index_j] == obs_index:
                    sorted_distance_list.add([index_i, index_j])
    toRaise[i, j] = 0


def Lower(i, j):
    voronoi_map[i, j] = 1
    si, sj = S2IJ(obst[i, j])
    for ni in [-1, 0, 1]:
        for nj in [-1, 0, 1]:
            if ni == 0 and nj == 0:
                continue

            xi = i + ni
            xj = j + nj
            if xi < 0 or xi >= 30 or xj < 0 or xj >= 30:
                continue
            # if toRaise[xi, xj] == 0:
            if True:
                zl_si, zl_sj = S2IJ(obst[si, sj])
                d = sqrt_map[int(abs(si-xi)), int(abs(sj-xj))]
                if ((d < dist[xi, xj]) or (obst[xi, xj] < 0)) and (zl_si == si) and (zl_sj == sj):
                    dist[xi, xj] = d
                    obst[xi, xj] = si*30+sj
                    sorted_distance_list.add([xi, xj])
                if (dist[xi, xj] < d):
                    divider_map[xi, xj] = obst[i, j]
                    divider_map[i, j] = obst[xi, xj]
                    checkVoronoi(xi, xj, i, j)


def Pops():  # get the element with max distance
    max_index = -1

    if len(sorted_distance_list) <= 0:
        return False, max_index
    else:
        max_element = sorted_distance_list.pop(pop_index)
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

    # for i in range(30):
    #     for j in range(30):
    #         for ni in [-1, 0, 1]:
    #             for nj in [-1, 0, 1]:
    #                 xi = i + ni
    #                 xj = j + nj
    #                 if xi < 0 or xi >= 30 or xj < 0 or xj >= 30:
    #                     continue
    #                 if (obst[xi, xj] != obst[i, j]):
    #                     divider.append([i, j])
    #                     divider.append([xi, xj])


def ShowDivider():
    for i in range(30):
        for j in range(30):
            if isVoronoi(i, j):
                # dist[i, j] = 0
                plt.gca().add_patch(plt.Rectangle((j, i), 1, 1, color='red'))


def isVoronoi(i, j):
    return voronoi_map[i, j] == 0 or voronoi_map[i, j] == -4


def checkVoronoi(x, y, nx, ny):
    obsxy = obst[x, y]
    obsxy_i, obsxy_j = S2IJ(obsxy)
    obsn = obst[nx, ny]
    obsn_i, obsn_j = S2IJ(obsn)
    if (dist[x, y] > 1 or dist[nx, ny] > 1) and dist[nx, ny] >= 0:
        if (abs(obsxy_i-obsn_i) > 1 or abs(obsxy_j-obsn_j) > 1):
            dxy_x = abs(x-obsn_i)
            dxy_y = abs(y-obsn_j)
            sqdxy = sqrt_map[dxy_x, dxy_y]
            stability_xy = sqdxy-dist[x, y]
            if stability_xy < 0:
                return
            dnxy_x = abs(nx-obsxy_i)
            dnxy_y = abs(ny-obsxy_j)
            sqdnxy = sqrt_map[dnxy_x, dnxy_y]
            stability_nxy = sqdnxy-dist[nx, ny]
            if stability_nxy < 0:
                return
            if stability_xy <= stability_nxy and dist[x, y] > 2:
                if (voronoi_map[x, y] != 0):
                    voronoi_map[x, y] = 0
                    pruneQueue.add([x, y])

            if stability_nxy <= stability_xy and dist[nx, ny] > 2:
                if (voronoi_map[nx, ny] != 0):
                    voronoi_map[nx, ny] = 0
                    pruneQueue.add([nx, ny])


def prune():
    while (len(pruneQueue) > 0):
        max_element = pruneQueue.pop(pop_index)
        x = max_element[0]
        y = max_element[1]
        voronoi_map[x, y] = -3
        sorted_distance_list.add([x, y])

        if ((x+2 < 30) and voronoi_map[x+1, y] == 1 and (y+1) < 30 and (y-1) >= 0):
            if (voronoi_map[x+1, y+1] != 1 and voronoi_map[x+1, y-1] != 1 and voronoi_map[x+2, y] != 1):
                voronoi_map[x+1, y] = -3
                sorted_distance_list.add([x+1, y])

        if ((x-2 >= 0) and voronoi_map[x-1, y] == 1 and (y+1) < 30 and (y-1) >= 0):
            if (voronoi_map[x+1, y+1] != 1 and voronoi_map[x-1, y-1] != 1 and voronoi_map[x-2, y] != 1):
                voronoi_map[x-1, y] = -3
                sorted_distance_list.add([x-1, y])

        if ((y-2 >= 0) and voronoi_map[x, y-1] == 1 and (x-1) >= 0 and (x+1) < 30):
            if (voronoi_map[x+1, y-1] != 1 and voronoi_map[x-1, y-1] != 1 and voronoi_map[x, y-2] != 1):
                voronoi_map[x, y-1] = -3
                sorted_distance_list.add([x, y-1])

        if ((y+2 < 30) and voronoi_map[x, y+1] == 1 and (x-1) >= 0 and (x+1) < 30):
            if (voronoi_map[x+1, y+1] != 1 and voronoi_map[x-1, y+1] != 1 and voronoi_map[x, y+2] != 1):
                voronoi_map[x, y+1] = -3
                sorted_distance_list.add([x, y+1])

    while (len(sorted_distance_list) > 0):
        max_element = sorted_distance_list.pop(pop_index)
        x = max_element[0]
        y = max_element[1]
        v = voronoi_map[x, y]
        if (v != - 3 and v != -2):
            continue
        markerMatchResult = markerMatch(x, y)
        if (markerMatchResult == 0):
            voronoi_map[x, y] = -1
        elif (markerMatchResult == 1):
            voronoi_map[x, y] = -4
        else:
            voronoi_map[x, y] = -2
            pruneQueue.add([x, y])

        if (len(sorted_distance_list) > 0):
            while (len(pruneQueue) > 0):
                p = pruneQueue.pop(pop_index)
                sorted_distance_list.add([p[0], p[1]])


def markerMatch(x, y):
    i = 0
    f = [0]*8
    voroCount = 0
    voroCountFour = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if (dx or dy):
                nx = x+dx
                ny = y+dy
                if (nx >= 0 and nx < 30 and ny >= 0 and ny < 30):
                    v = voronoi_map[nx, ny]
                    b = (v <= 0 and v != -1)
                    f[i] = b
                    if (b):
                        voroCount += 1
                        if (not (dx and dy)):
                            voroCountFour += 1
                    i += 1
    if (voroCount < 3 and voroCountFour == 1):
        return 1

    if (((not f[0]) and f[1] and f[3]) or ((not f[2]) and f[1] and f[4]) or ((not f[5]) and f[3] and f[6]) or ((not f[7]) and f[6] and f[4])):
        return 1
    if ((f[3] and f[4] and (not f[1] and (not f[6]))) or (f[1] and f[6] and (not f[3] and (not f[4])))):
        return 1

    if (voroCount >= 0 and voroCountFour >= 3 and voronoi_map[x, y] != -2):
        return 2

    return 0


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
RemoveObstacle(16, 16)
RemoveObstacle(15, 16)
RemoveObstacle(5, 5)
UpdateDistanceMap()
SetObstacle(25, 28)
SetObstacle(10, 28)
UpdateDistanceMap()
RemoveObstacle(10, 28)
RemoveObstacle(10, 25)
UpdateDistanceMap()
prune()
ShowDivider()


print("Time:", time.time() - StartTime, "seconds")

plt.imshow(dist)


plt.show()
plt.colorbar()
plt.pause(10)
