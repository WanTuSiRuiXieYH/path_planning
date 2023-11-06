import numpy as np
import matplotlib.pyplot as plt
import copy

## 初始化船舶参数
d = 3.5  # 航道标准宽度
W = 1.8  # 船舶宽度
L = 4.7  # 船舶长度

P0 = np.array([0, -d / 2, 1, 1])  # 起点位置，分别代表x,y,vx,vy
Pg = np.array([99, d / 2, 0, 0])  # 目标位置

# 障碍物位置
Pobs = np.array([
    [15, 7 / 4, 0, 0],
    [30, -3 / 2, 0, 0],
    [45, 3 / 2, 0, 0],
    [60, -3 / 4, 0, 0],
    [80, 3 / 2, 0, 0]
])

P = np.vstack((Pg, Pobs))  # 将目标位置和障碍物位置合并

Eta_att = 5  # 引力的增益系数
Eta_rep_ob = 15  # 斥力的增益系数
Eta_rep_edge = 50  # 道路边界斥力的增益系数
d0 = 20  # 障碍影响的最大距离
num = P.shape[0]  # 障碍与目标总数
len_step = 0.5  # 步长
n = 1  # 斥力公式中的幂次数
Num_iter = 300  # 最大循环迭代次数

path = []  # 保存船舶走过的每个点的坐标
delta = np.zeros((num, 2))  # 保存船舶当前位置与障碍物的方向向量，方向指向船舶；以及保存船舶当前位置与目标点的方向向量，方向指向目标点
dists = []  # 保存船舶当前位置与障碍物的距离以及船舶当前位置与目标点的距离
unite_vec = np.zeros((num, 2))  # 保存船舶当前位置与障碍物的单位方向向量，方向指向船舶；以及保存船舶当前位置与目标点的单位方向向量，方向指向目标点

F_rep_ob = np.zeros((len(Pobs), 2))  # 存储每一个障碍到船舶的斥力，带方向
v = np.linalg.norm(P0[2:4])  # 设船舶速度为常值

## 主循环
Pi = P0[0:2]  # 当前船舶位置

for i in range(Num_iter):
    if ((Pi[0] - Pg[0]) ** 2 + (Pi[1] - Pg[1]) ** 2) ** 0.5 < 1:
        break

    dists = []
    path.append(Pi)

    # 计算船舶当前位置与障碍物的单位方向向量
    for j in range(len(Pobs)):
        delta[j] = Pi[0:2] - Pobs[j, 0:2]
        dists.append(np.linalg.norm(delta[j]))
        unite_vec[j] = delta[j] / dists[j]

    # 计算船舶当前位置与目标的单位方向向量
    delta[len(Pobs)] = Pg[0:2] - Pi[0:2]
    dists.append(np.linalg.norm(delta[len(Pobs)]))
    unite_vec[len(Pobs)] = delta[len(Pobs)] / dists[len(Pobs)]

    ## 计算引力
    F_att = Eta_att * dists[len(Pobs)] * unite_vec[len(Pobs)]

    ## 计算斥力
    F_rep_ob = np.zeros((len(Pobs), 2))  # 重新初始化斥力
    for j in range(len(Pobs)):
        if dists[j] >= d0:
            F_rep_ob[j] = np.array([0, 0])
        else:
            # 障碍物的斥力1，方向由障碍物指向船舶
            F_rep_ob1_abs = Eta_rep_ob * (1 / dists[j] - 1 / d0) * (
                    dists[len(Pobs)]) ** n / dists[j] ** 2  # 斥力大小
            F_rep_ob1 = F_rep_ob1_abs * unite_vec[j]  # 斥力向量

            # 障碍物的斥力2，方向由船舶指向目标点
            F_rep_ob2_abs = n / 2 * Eta_rep_ob * (1 / dists[j] - 1 / d0) ** 2 * (
                    dists[len(Pobs)]) ** (n - 1)  # 斥力大小
            F_rep_ob2 = F_rep_ob2_abs * unite_vec[len(Pobs)]  # 斥力向量

            # 改进后的障碍物合斥力计算
            F_rep_ob[j] = F_rep_ob1 + F_rep_ob2

    # 增加道路边界斥力势场，根据船舶当前位置，选择对应的斥力函数
    if Pi[1] > -d + W / 2 and Pi[1] <= -d / 2:
        F_rep_edge = [0, Eta_rep_edge * v * np.exp(-d / 2 - Pi[1])]  # 下道路边界区域斥力势场，方向指向y轴正向
    elif Pi[1] > -d / 2 and Pi[1] <= -W / 2:
        F_rep_edge = np.array([0, 1 / 3 * Eta_rep_edge * Pi[1] ** 2])
    elif Pi[1] > W / 2 and Pi[1] <= d / 2:
        F_rep_edge = np.array([0, -1 / 3 * Eta_rep_edge * Pi[1] ** 2])
    elif Pi[1] > d / 2 and Pi[1] <= d - W / 2:
        F_rep_edge = np.array([0, Eta_rep_edge * v * (np.exp(Pi[1] - d / 2))])

    ## 计算合力和方向
    F_rep = np.sum(F_rep_ob, axis=0) + F_rep_edge
    F_sum = F_att + F_rep
    UnitVec_Fsum = 1 / np.linalg.norm(F_sum) * F_sum

    # 计算船舶的下一步位置
    Pi = copy.deepcopy(Pi + len_step * UnitVec_Fsum)

path.append(Pg[0:2])  # 最后把目标点也添加进路径中
path = np.array(path)  # 转为numpy

## 画图
plt.figure()
plt.xlim(-5, 105)
plt.ylim(-4, 4)

for i in range(len(path)):
    plt.plot(Pobs[:, 0], Pobs[:, 1], 'ro')  # 障碍物位置
    plt.plot(Pg[0], Pg[1], 'gv')  # 目标位置
    plt.plot(P0[0], P0[1], 'bs')  # 起点位置
    plt.plot(np.array([-5, 100]), np.array([0, 0]), 'w--')  # 画分界线
    plt.plot(np.array([-5, 100]), np.array([d, d]), 'w')
    plt.plot(np.array([-5, 100]), np.array([-d, -d]), 'w')
    plt.gca().set_aspect('equal')
    plt.plot(path[0:i, 0], path[0:i, 1], 'k')  # 路径点
    plt.pause(0.01)

plt.show()
