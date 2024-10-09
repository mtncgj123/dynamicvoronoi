import numpy as np
import matplotlib.pyplot as plt
import time
import random
from sortedcontainers import SortedList

map_size = 50
dist = 99999.0*np.ones((map_size, map_size))
obst = -1*np.ones((map_size, map_size))
toRaise = np.zeros((map_size, map_size))
sqrt_map = np.zeros((map_size, map_size))
divider = []
divider_map = -1*np.ones((map_size, map_size))
pop_index = 0  # 0 for pop front.-1 for pop back

for i in range(map_size):
    for j in range(map_size):
        sqrt_map[i, j] = np.sqrt(i**2 + j**2)


def Reset():
    global dist, obst, toRaise, divider, divider_map
    dist = 99999.0*np.ones((map_size, map_size))
    obst = -1*np.ones((map_size, map_size))
    toRaise = np.zeros((map_size, map_size))
    divider = []
    divider_map = -1*np.ones((map_size, map_size))


def distance_key(List_Element):
    i = List_Element[0]
    j = List_Element[1]
    return dist[i, j]


sorted_distance_list = SortedList(key=distance_key)


def S2IJ(s):
    i = int(s//map_size)
    j = int(s % map_size)
    return i, j


def SetObstacle(i, j):
    obst[i, j] = i*map_size+j
    dist[i, j] = 0
    sorted_distance_list.add([i, j])


def RemoveObstacle(i, j):
    obst[i, j] = -1
    toRaise[i, j] = 1
    dist[i, j] = 99999.0
    sorted_distance_list.add([i, j])


def Raise(i, j):
    for ni in [-1, 0, 1]:
        for nj in [-1, 0, 1]:
            if ni == 0 and nj == 0:
                continue

            xi = i + ni
            xj = j + nj
            if xi < 0 or xi >= map_size or xj < 0 or xj >= map_size:
                continue

            if (obst[xi, xj] >= 0) and (toRaise[xi, xj] == 0):
                oi, oj = S2IJ(obst[xi, xj])
                zl_oi, zl_oj = S2IJ(obst[oi, oj])
                if (obst[oi, oj] == -1 or (zl_oi != oi) or (zl_oj != oj)):
                    dist[xi, xj] = 99999.0
                    obst[xi, xj] = -1
                    toRaise[xi, xj] = 1

                sorted_distance_list.add([xi, xj])
    toRaise[i, j] = 0


def RemoveObstacleWithDivider(i, j):
    # obst[i, j] = -1
    toRaise[i, j] = 1
    # dist[i, j] = 99999.0
    sorted_distance_list.add([i, j])


def RaiseWithDivider(i, j):
    obs_index = obst[i, j]
    obs_i, obs_j = S2IJ(obs_index)
    if i == obs_i and j == obs_j:
        for index_i in range(map_size):
            for index_j in range(map_size):
                if obst[index_i, index_j] == obs_index:
                    dist[index_i, index_j] = 99999.0
                    obst[index_i, index_j] = -1
                if divider_map[index_i, index_j] == obs_index:
                    sorted_distance_list.add([index_i, index_j])
    toRaise[i, j] = 0


def Lower(i, j):
    si, sj = S2IJ(obst[i, j])
    for ni in [-1, 0, 1]:
        for nj in [-1, 0, 1]:
            if ni == 0 and nj == 0:
                continue

            xi = i + ni
            xj = j + nj
            if xi < 0 or xi >= map_size or xj < 0 or xj >= map_size:
                continue
            # if toRaise[xi, xj] == 0:
            if True:
                zl_si, zl_sj = S2IJ(obst[si, sj])
                d = sqrt_map[int(abs(si-xi)), int(abs(sj-xj))]
                if ((d < dist[xi, xj]) or (obst[xi, xj] < 0)) and (zl_si == si) and (zl_sj == sj):
                    dist[xi, xj] = d
                    obst[xi, xj] = si*map_size+sj
                    sorted_distance_list.add([xi, xj])
                if (dist[xi, xj] < d):
                    divider_map[xi, xj] = obst[i, j]
                    divider_map[i, j] = obst[xi, xj]


def Pops():  # get the element with max distance
    max_index = -1

    if len(sorted_distance_list) <= 0:
        return False, max_index
    else:
        max_element = sorted_distance_list.pop(pop_index)
        i = max_element[0]
        j = max_element[1]
        max_index = i*map_size+j
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


def UpdateDistanceMapWithDivider():
    not_empty, s = Pops()
    while not_empty:
        i, j = S2IJ(s)
        if toRaise[i, j] == 1:
            RaiseWithDivider(i, j)
            # print("raise")
        else:
            if obst[i, j] >= 0:
                Lower(i, j)
                # print("lower")
        not_empty, s = Pops()


obstacle_num = 20
remove_obs_num = random.randint(0, obstacle_num-1)
remove_random_obs_num = 6
detect_time = []
detect_with_divider_time = []
repeat_time = 50

plt.ion()  # 开启交互模式
plt.figure(figsize=(10, 5))  # 创建新的图形窗口
for _ in range(repeat_time):

    obs_list = [(random.randint(0, map_size-1), random.randint(0, map_size-1))
                for _ in range(obstacle_num)]
    random_remove_obs_list = [(random.randint(0, map_size-1), random.randint(0, map_size-1))
                              for _ in range(remove_random_obs_num)]
    remove_obs_list = random.sample(obs_list, remove_obs_num)

    StartTime = time.time()

    for obs in obs_list:
        SetObstacle(obs[0], obs[1])
    UpdateDistanceMap()

    for obs in random_remove_obs_list:
        RemoveObstacle(obs[0], obs[1])

    for obs in remove_obs_list:
        RemoveObstacle(obs[0], obs[1])
    UpdateDistanceMap()

    detect_time.append(time.time() - StartTime)

    tmp_dist = dist

    Reset()

    StartTime = time.time()

    for obs in obs_list:
        SetObstacle(obs[0], obs[1])
    UpdateDistanceMapWithDivider()

    for obs in random_remove_obs_list:
        RemoveObstacleWithDivider(obs[0], obs[1])

    for obs in remove_obs_list:
        RemoveObstacleWithDivider(obs[0], obs[1])
    UpdateDistanceMapWithDivider()

    detect_with_divider_time.append(time.time() - StartTime)

    is_detection_equal = np.array_equal(tmp_dist, dist)
    print(is_detection_equal)

    if is_detection_equal != True:
        print(np.max(tmp_dist-dist))
        print(np.min(tmp_dist-dist))
        print(np.linalg.norm(tmp_dist - dist))
        # 在第一个子图中显示图像1
        plt.subplot(1, 2, 1)  # 第一个子图
        plt.imshow(tmp_dist)  # 使用 'viridis' 颜色映射

        # 在第二个子图中显示图像2
        plt.subplot(1, 2, 2)  # 第一个子图
        plt.imshow(dist)  # 使用 'viridis' 颜色映射

        # 调整布局，防止标题重叠
        plt.tight_layout()

        # 显示图形
        plt.show()
        plt.pause(10)
        plt.clf()  # 清除当前图形，不再叠加图像

    Reset()


times = range(repeat_time)
plt.plot(times, detect_time, label='before', marker='o')  # 绘制第一个数组的折线图
plt.plot(times, detect_with_divider_time,
         label='after', marker='s')     # 绘制第二个数组的折线图
plt.show()
plt.pause(3)

print("before time: ", sum(detect_time) / len(detect_time))
print("after time: ", sum(detect_with_divider_time) /
      len(detect_with_divider_time))
