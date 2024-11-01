import numpy as np
import matplotlib.pyplot as plt
import time
from sortedcontainers import SortedList
dist = 99999.0*np.ones((30, 30))
obst = -1*np.ones((30, 30))
toRaise = np.zeros((30, 30))
sqrt_map = np.zeros((30, 30))
divider_map = -1*np.ones((30, 30))
voronoi_map = np.zeros((30, 30))
pop_index = 0  # 0 for pop front.-1 for pop back
isAnimationOn = False

# 生成距离表格
for i in range(30):
    for j in range(30):
        sqrt_map[i, j] = np.sqrt(i**2 + j**2)


class Voronoi:
    voronoiKeep = -4
    freeQueued = -3
    voronoiRetry = -2
    voronoiPrune = -1
    free = 0
    occupied = 1


class CmarkerMatchResult:
    pruned = 0
    keep = 1
    retry = 2


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
    voronoi_map[i, j] = Voronoi.occupied
    sorted_distance_list.add([i, j])


def RemoveObstacle(i, j):
    toRaise[i, j] = 1
    sorted_distance_list.add([i, j])


def isOccupied(i, j):
    obs_index = obst[i, j]
    obs_i, obs_j = S2IJ(obs_index)
    return (i == obs_i and j == obs_j)


def Raise(i, j):
    obs_index = obst[i, j]
    if isOccupied(i, j):
        for index_i in range(30):
            for index_j in range(30):
                if obst[index_i, index_j] == obs_index:
                    dist[index_i, index_j] = 99999.0
                    obst[index_i, index_j] = -1
                if divider_map[index_i, index_j] == obs_index:
                    sorted_distance_list.add([index_i, index_j])
    toRaise[i, j] = 0


def Lower(i, j):
    voronoi_map[i, j] = Voronoi.occupied
    si, sj = S2IJ(obst[i, j])
    for ni in [-1, 0, 1]:
        for nj in [-1, 0, 1]:
            if ni == 0 and nj == 0:
                continue

            xi = i + ni
            xj = j + nj
            if xi <= 0 or xi >= 30-1 or xj <= 0 or xj >= 30-1:
                continue

            d = sqrt_map[abs(si-xi), abs(sj-xj)]
            if ((d < dist[xi, xj]) or (obst[xi, xj] < 0)) and isOccupied(si, sj):
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
        else:
            if obst[i, j] >= 0:
                Lower(i, j)
        not_empty, s = Pops()
        if isAnimationOn:
            plt.clf()
            plt.imshow(dist, cmap='viridis', vmin=0, vmax=25)
            plt.pause(0.001)


def ShowDivider():
    for i in range(30):
        for j in range(30):
            if isVoronoi(i, j):
                dist[i, j] = 0
                plt.gca().add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, color='red'))


def isVoronoi(i, j):
    return voronoi_map[i, j] == Voronoi.free or voronoi_map[i, j] == Voronoi.voronoiKeep


def checkVoronoi(x, y, nx, ny):
    obsxy = obst[x, y]
    obsxy_i, obsxy_j = S2IJ(obsxy)
    obsn = obst[nx, ny]
    obsn_i, obsn_j = S2IJ(obsn)
    if (dist[x, y] > 1 or dist[nx, ny] > 1):
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

            if stability_xy <= stability_nxy and dist[x, y] > 2:
                if (voronoi_map[x, y] != Voronoi.free):
                    voronoi_map[x, y] = Voronoi.free
                    pruneQueue.add([x, y])

            if stability_nxy <= stability_xy and dist[nx, ny] > 2:
                if (voronoi_map[nx, ny] != Voronoi.free):
                    voronoi_map[nx, ny] = Voronoi.free
                    pruneQueue.add([nx, ny])


def prune():
    while (len(pruneQueue) > 0):
        max_element = pruneQueue.pop(pop_index)
        x = max_element[0]
        y = max_element[1]
        voronoi_map[x, y] = Voronoi.freeQueued
        sorted_distance_list.add([x, y])

        if ((x+2 < 30) and voronoi_map[x+1, y] == Voronoi.occupied):
            if (voronoi_map[x+1, y+1] != Voronoi.occupied and voronoi_map[x+1, y-1] != Voronoi.occupied and voronoi_map[x+2, y] != Voronoi.occupied):
                voronoi_map[x+1, y] = Voronoi.freeQueued
                sorted_distance_list.add([x+1, y])

        if ((x-2 >= 0) and voronoi_map[x-1, y] == Voronoi.occupied):
            if (voronoi_map[x-1, y+1] != Voronoi.occupied and voronoi_map[x-1, y-1] != Voronoi.occupied and voronoi_map[x-2, y] != Voronoi.occupied):
                voronoi_map[x-1, y] = Voronoi.freeQueued
                sorted_distance_list.add([x-1, y])

        if ((y-2 >= 0) and voronoi_map[x, y-1] == Voronoi.occupied):
            if (voronoi_map[x+1, y-1] != Voronoi.occupied and voronoi_map[x-1, y-1] != Voronoi.occupied and voronoi_map[x, y-2] != Voronoi.occupied):
                voronoi_map[x, y-1] = Voronoi.freeQueued
                sorted_distance_list.add([x, y-1])

        if ((y+2 < 30) and voronoi_map[x, y+1] == Voronoi.occupied):
            if (voronoi_map[x+1, y+1] != Voronoi.occupied and voronoi_map[x-1, y+1] != Voronoi.occupied and voronoi_map[x, y+2] != Voronoi.occupied):
                voronoi_map[x, y+1] = Voronoi.freeQueued
                sorted_distance_list.add([x, y+1])

    while (len(sorted_distance_list) > 0):
        max_element = sorted_distance_list.pop(pop_index)
        x = max_element[0]
        y = max_element[1]
        v = voronoi_map[x, y]
        if (v != Voronoi.freeQueued and v != Voronoi.voronoiRetry):
            continue
        markerMatchResult = markerMatch(x, y)
        if (markerMatchResult == CmarkerMatchResult.pruned):
            voronoi_map[x, y] = Voronoi.voronoiPrune
        elif (markerMatchResult == CmarkerMatchResult.keep):
            voronoi_map[x, y] = Voronoi.voronoiKeep
        else:
            voronoi_map[x, y] = Voronoi.voronoiRetry
            pruneQueue.add([x, y])

        if (len(sorted_distance_list) == 0):
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
                v = voronoi_map[nx, ny]
                b = (v <= Voronoi.free and v != Voronoi.voronoiPrune)
                f[i] = b
                if (b):
                    voroCount += 1
                    if (not (dx and dy)):
                        voroCountFour += 1
                i += 1
    if (voroCount < 3 and voroCountFour == 1):
        return CmarkerMatchResult.keep

    if (((not f[0]) and f[1] and f[3]) or ((not f[2]) and f[1] and f[4]) or ((not f[5]) and f[3] and f[6]) or ((not f[7]) and f[6] and f[4])):
        return CmarkerMatchResult.keep
    if ((f[3] and f[4] and (not f[1]) and (not f[6])) or (f[1] and f[6] and (not f[3]) and (not f[4]))):
        return CmarkerMatchResult.keep

    if (voroCount >= 5 and voroCountFour >= 3 and voronoi_map[x, y] != Voronoi.voronoiRetry):
        return CmarkerMatchResult.retry

    return CmarkerMatchResult.pruned


plt.ion()
StartTime = time.time()
SetObstacle(20, 20)
SetObstacle(19, 20)
SetObstacle(18, 20)
SetObstacle(17, 20)
SetObstacle(16, 20)
SetObstacle(15, 20)
SetObstacle(14, 20)
SetObstacle(13, 20)
SetObstacle(12, 20)
SetObstacle(11, 20)
SetObstacle(10, 20)
SetObstacle(9, 20)
SetObstacle(8, 20)
SetObstacle(7, 20)
SetObstacle(6, 20)
SetObstacle(5, 20)
SetObstacle(5, 19)
SetObstacle(5, 18)
SetObstacle(5, 17)
SetObstacle(5, 16)
SetObstacle(5, 15)
SetObstacle(5, 14)
SetObstacle(5, 13)
SetObstacle(5, 12)
SetObstacle(5, 11)
SetObstacle(5, 10)
SetObstacle(5, 9)
SetObstacle(5, 8)
SetObstacle(6, 8)
SetObstacle(7, 8)
SetObstacle(8, 8)
SetObstacle(9, 8)
SetObstacle(10, 8)
SetObstacle(11, 8)
SetObstacle(12, 8)
SetObstacle(13, 8)
SetObstacle(14, 8)
SetObstacle(15, 8)
SetObstacle(16, 8)
SetObstacle(17, 8)
SetObstacle(18, 8)
SetObstacle(19, 8)
SetObstacle(20, 8)
UpdateDistanceMap()
prune()
ShowDivider()


print("Time:", time.time() - StartTime, "seconds")

plt.imshow(dist)

plt.show()
plt.colorbar()
plt.pause(5)
