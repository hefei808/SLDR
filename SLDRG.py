import decimal
import multiprocessing
import math
import copy
import time
import os
import sys


class solution:  # 定义对象
    def __init__(self, nodes, neighbors):
        self.nodes = nodes
        self.M = 0
        self.S = 0
        self.I = 0
        self.O = 0
        self.Ix = 0
        self.N = []
        self.dict = neighbors

    def __eq__(self, other):
        return self.nodes == other.nodes

    def __hash__(self):
        return hash(self.nodes)


class Graph():
    def __init__(self):
        self.nodes = {}
        self.graph = {}


def GetNetwork(f1, f2):
    G = Graph()
    with open(f2) as f:
        lines = f.readlines()
        for line in lines:
            curLine = line.strip().split(" ")
            G.nodes.update({int(curLine[0]): [float(curLine[1]), float(curLine[2])]})
    with open(f1) as ef:
        elines = ef.readlines()
        for line in elines:
            cureline = line.strip().split(" ")
            if (len(cureline) > 1):
                temp = []
                for i in range(1, len(cureline)):
                    temp.append(int(cureline[i]))
                G.graph.update({int(cureline[0]): temp})
            else:
                G.graph.update({int(cureline[0]): []})
    return G


def Isoutarchive(W, archive):  # 判断解W是否在archive里
    for i in archive:
        if (W.nodes == i.nodes):
            return False
    return True


def computeDistance(p1, p2):  # 计算两点之间距离
    p3 = p2 - p1
    p4 = math.hypot(p3[0], p3[1])
    return p4


def Findneighbors(G, W):  # 寻找解W对应的节点集在网络中的邻居节点
    N = set()
    for i in W.nodes:
        N.update(set(G.graph[i]))
    return N - W.nodes


def getIO(G, nodes):
    In = set()
    Out = set()
    s = set()
    for node in nodes:
        s.update((node, i) for i in G.graph[node])
    for (i, j) in s:
        if (i in nodes and j in nodes):
            In.add((i, j))
        else:
            Out.add((i, j))
    return len(In) / 2, len(Out)


def computems(nodes, G, W):  # 根据增量计算节点集P的模块度M和空间内聚度S
    """
    计算M值
    """
    # neighbor=set()
    # for i in nodes:
    #     neighbor.update(set(G.graph[i]))
    # sum1,sum2=0,0
    # for i in nodes:
    #     N=set(G.graph[i])
    #     num1=len(N&W.nodes)
    #     num2=len(N&nodes)
    #     sum1+=num1
    #     sum2+=num2
    # Out=neighbor-W.nodes-nodes
    # I = W.I+sum1+sum2/2
    # O = W.O+len(Out)-sum1
    I, O = getIO(G, W.nodes - nodes)
    if (O == 0):
        return -1, -1, -1, -1, -1
    M = round(I / O, 8)
    """
    计算S值
    """
    sumx = 0
    tempnodes = set(W.nodes)
    for node in nodes:
        x = 0
        loc = G.nodes[node]
        tempnodes.remove(node)
        for node_s in tempnodes:
            loc1 = G.nodes[node_s]
            d1 = math.sqrt(((loc1[0] - loc[0]) * (loc1[0] - loc[0])) + ((loc1[1] - loc[1]) * (loc1[1] - loc[1])))
            x += d1
        sumx += x
    Ix = W.Ix - sumx
    size = len(W.nodes) - len(nodes)
    S = round(-((2 * Ix) / (size * (size - 1))), 8)
    return M, S, I, O, Ix


def compute_ms(node, G, W):  # 根据增量计算节点集P的模块度M和空间内聚度S
    x = 0
    In = set(G.graph[node]) & W.nodes
    Out = set(G.graph[node]) - In
    I = W.I + len(In)
    O = W.O + len(Out) - len(In)
    if (O == 0):
        return -1, -1, -1, -1, -1
    M = round(I / O, 8)
    loc = G.nodes[node]
    for node_s in W.nodes:
        loc1 = G.nodes[node_s]
        d1 = math.sqrt(((loc1[0] - loc[0]) * (loc1[0] - loc[0])) + ((loc1[1] - loc[1]) * (loc1[1] - loc[1])))
        x += d1
    Ix = W.Ix + x
    S = round(-((2 * Ix) / (len(W.nodes) * (len(W.nodes) + 1))), 8)
    return M, S, I, O, Ix


def Issame(A, B):
    if (len(A) != len(B)):
        return False
    else:
        for i in range(0, len(A)):
            if (A[i].nodes != B[i].nodes):
                return False
        return True


def Findsons(G, archive, begin):  # 寻找当前档案的的的衍生解
    box = set().union(archive)
    CC = set()
    for W in archive:
        for node in W.N:
            tempc = frozenset([node]) | W.nodes
            tempN = copy.copy(W.dict)
            P = solution(tempc, tempN)
            if P in box:
                continue
            else:
                P.M, P.S, P.I, P.O, P.Ix = compute_ms(node, G, W)
                if (P.M == -1 and Isoutarchive(P, CC)):
                    CC.add(P)
                else:
                    P.N = Findneighbors(G, P)
                    box.add(P)  # 加入衍生解P
            ctime = time.perf_counter()
            if (ctime - begin > 7200):
                return list(box), CC
    box = list(box)
    return box, CC


# def merge(ND,G):
#     # print("\n^_^融合前的长度为：", len(ND))
#     # for j in range(0, len(ND)):
#     #     print(ND[j].nodes, "    M=", '%.4f' % ND[j].M, "     S=", '%.4f' % ND[j].S, "     d=",
#     #           '%.4f' % (ND[j].Ix))  # 输出当前档案中所有解
#     lenth=len(ND)
#     cutND=ND[int(lenth/4):math.ceil(3*lenth/4)]
#     W=cutND[0]
#     cutND.pop(0)
#     d=[W]
#     for c in cutND:
#         try:
#             node=list(c.nodes-W.nodes)[0]
#             tempc = frozenset([node]) | W.nodes
#             tempN = copy.copy(W.dict)
#             P = solution(tempc, tempN)
#             P.M, P.S, P.I, P.O, P.Ix = compute_ms(node, G, W)
#             P.N = Findneighbors(G, P)
#             d.append(P)
#             W=P
#         except:
#             continue
#     pareto=Findpreto(d)
#     S_mean = (pareto[0].S + pareto[len(pareto) - 1].S)/2
#     detalSlist = []
#     for i in pareto:
#         detalS = abs(i.S - S_mean)
#         detalSlist.append(detalS)
#     indexmean = detalSlist.index(min(detalSlist))
#     # M_mean=(pareto[0].M+pareto[len(pareto)-1].M)/2
#     # detalMlist=[]
#     # for i in pareto:
#     #     detalM=abs(i.M-M_mean)
#     #     detalMlist.append(detalM)
#     # indexmean=detalMlist.index(min(detalMlist))
#     return [pareto[indexmean]]

def cut(ND):
    cutND = []
    Mlist = [round(decimal.Decimal(i.M), 6) for i in ND]
    Slist = [round(decimal.Decimal(i.S), 6) for i in ND]
    M_mean = round(decimal.Decimal(sum(Mlist) / len(Mlist)), 6)
    S_mean = round(decimal.Decimal(sum(Slist) / len(Slist)), 6)
    deltaMlist = [round(abs(M_mean - decimal.Decimal(i)), 6) for i in Mlist]
    deltaSlist = [round(abs(S_mean - decimal.Decimal(i)), 6) for i in Slist]
    deltaM_mean = round(decimal.Decimal(sum(deltaMlist) / len(deltaMlist)), 6)
    deltaS_mean = round(decimal.Decimal(sum(deltaSlist) / len(deltaSlist)), 6)
    for num in range(len(Mlist)):
        if not (round(M_mean - Mlist[num], 6) > deltaM_mean or round(S_mean - Slist[num]) > deltaS_mean):
            cutND.append(ND[num])
    # if(len(cutND)==0):
    #     return ND[int(len(ND)/2)]
    # print(Mlist,M_mean)
    # print(Slist,S_mean)
    # print(deltaMlist,deltaM_mean)
    # print(deltaSlist,deltaS_mean)
    return cutND


def choosecommunity(ND):
    MMD = {}
    Mmin, Mmax, Smin, Smax = ND[len(ND) - 1].M, ND[0].M, ND[0].S, ND[len(ND) - 1].S
    if (Mmin == Mmax and Smin == Smax):
        return ND[0]
    # print(Mmin,Mmax)
    # print(len(dict))
    for c in ND:
        M = (c.M - Mmax) / (Mmin - Mmax)
        S = (c.S - Smax) / (Smin - Smax)
        # print("***",c.M,c.S)
        # print(M,S)
        MMD.update({c: M + S})
    C = min(MMD, key=MMD.get)
    # C=dict[index].nodes
    return C


def MMDsort(ND):
    MMD = {}
    Mmin, Mmax, Smin, Smax = ND[len(ND) - 1].M, ND[0].M, ND[0].S, ND[len(ND) - 1].S
    M_mean, S_mean = sum([C.M for C in ND]) / len(ND), sum([C.S for C in ND]) / len(ND)
    if (Mmin == Mmax and Smin == Smax):
        return ND
    # print(Mmin,Mmax)
    # print(len(dict))
    for c in ND:
        M = (c.M - Mmax) / (Mmin - Mmax)
        S = (c.S - Smax) / (Smin - Smax)
        # print("***",c.M,c.S)
        # print(M,S)
        # MMD.update({c: (M + S, S_mean +M_mean- c.S -c.M)})
        MMD.update({c: (M + S, c.S / S_mean - c.M / M_mean)})
        # MMD.update({c: (M + S,1)})
    sort = sorted(MMD.items(), key=lambda x: (x[1][0], x[1][1]))
    clist = [i[0] for i in sort]
    # C=min(MMD,key=MMD.get)
    # C=dict[index].nodes
    return clist


def merge(ND, G, currentC):
    # print("\n^_^融合前的长度为：", len(ND))
    # for j in range(0, len(ND)):
    #     print(ND[j].nodes, "    M=", '%.4f' % ND[j].M, "     S=", '%.4f' % ND[j].S, "     d=",
    #           '%.4f' % (ND[j].Ix))  # 输出当前档案中所有解
    if (currentC in ND):
        ND.remove(currentC)
        if(len(ND)==0):
            return [currentC]
    cutND = ND
    # print(len(cutND))
    # print("\n^_^过滤后的长度为：", len(cutND))
    # for j in range(0, len(cutND)):
    #     print(cutND[j].nodes, "    M=", '%.4f' % cutND[j].M, "     S=", '%.4f' % cutND[j].S, "     d=",
    #           '%.4f' % (cutND[j].Ix))  # 输出当前档案中所有解
    # cutND=ND[int(lenth/4):math.ceil(3*lenth/4)]
    clist = MMDsort(cutND)
    W = clist[0]
    clist.pop(0)
    d = [W]
    for c in clist:
        try:
            node = list(c.nodes - W.nodes)[0]
        except:
            continue
        tempc = frozenset([node]) | W.nodes
        tempN = copy.copy(W.dict)
        P = solution(tempc, tempN)
        P.M, P.S, P.I, P.O, P.Ix = compute_ms(node, G, W)
        P.N = Findneighbors(G, P)
        d.append(P)
        W = P
    pareto = Findpreto(list(set(d) | set(cutND)))
    # a = choosecommunity(pareto)
    a = MMDsort(pareto)[0]
    return [a]


def findpreto(sons, G, currentC):  # 寻找解集中的非支配解
    preto = []  # 存放非支配解
    sort = sorted(sons, key=lambda x: (x.M, x.S), reverse=True)  # 按照解的M值大小关系，对解降序排序
    preto.append(sort[0])  # 取第一个解作为非支配解
    maxS = sort[0].S
    for each in sort:  # 筛选出剩下解当中的非支配解存入preto中
        if (each.S > maxS):
            preto.append(each)
            maxS = each.S
        elif (each.S == maxS and each.M == preto[len(preto) - 1].M and Isoutarchive(each, preto)):
            preto.append(each)
        else:
            continue

    return merge(preto, G, currentC)


def Findpreto(sons):  # 寻找解集中的非支配解
    preto = []  # 存放非支配解
    sort = sorted(sons, key=lambda x: (x.M, x.S), reverse=True)  # 按照解的M值大小关系，对解降序排序
    preto.append(sort[0])  # 取第一个解作为非支配解
    maxS = sort[0].S
    for each in sort:  # 筛选出剩下解当中的非支配解存入preto中
        if (each.S > maxS):
            preto.append(each)
            maxS = each.S
        elif (each.S == maxS and each.M == preto[len(preto) - 1].M and Isoutarchive(each, preto)):
            preto.append(each)
        else:
            continue
    return preto


def LocalCommunityDetectionForNodei(nodei, G, archive):
    W = solution(frozenset([nodei]), {})
    W.M, W.I, W.Ix, W.S = 0, 0, 0, -100000
    W.O = len(G.graph[nodei])
    W.N = G.graph[nodei]
    archive.append(W)  # 档案记录第一个解
    HND = set()
    CC = set()
    begin = time.perf_counter()
    history=[]
    while (True):
        son, cc = Findsons(G, archive, begin)  # 当前档案的衍生解
        CC.update(cc)
        # print("\n^_^非支配解更新，当前档案长度为：", len(archive), ";     存档长度：", len(HND))
        # for j in range(0, len(archive)):
        #     print(archive[j].nodes, "    M=", '%.4f' % archive[j].M, "     S=", '%.4f' % archive[j].S, "     d=",
        #           '%.4f' % (archive[j].Ix))  # 输出当前档案中所有解
        ND = findpreto(son, G, archive[0]) # 衍生解中的非支配解
        for c in history:
            if(c.M>=ND[0].M and c.S>ND[0].S) or (c.M>ND[0].M and c.S>=ND[0].S):
                archive=[c]
                # print("最终档案长度为", len(archive))
                # for j in range(0, len(archive)):
                #     print(archive[j].nodes, "    M=", '%.4f' % archive[j].M, "     S=", '%.8f' % archive[j].S,
                #           "     d=",
                #           '%.4f' % (archive[j].Ix))  # 输出当前档案中所有解
                return archive
        history.append(ND[0])
        ctime = time.perf_counter()
        if (archive[0].nodes == ND[0].nodes or ctime - begin > 7200):  # 终止循环条件：更新前的档案和更新后的档案一样；否则，更新档案，继续循环
            break
        archive = ND
    # archive = list(set(archive)|CC)
    archive = Findpreto(list(set(archive) | HND))
    # print("最终档案长度为", len(archive))
    # for j in range(0, len(archive)):
    #     print(archive[j].nodes, "    M=", '%.4f' % archive[j].M, "     S=", '%.8f' % archive[j].S, "     d=",
    #           '%.4f' % (archive[j].Ix))  # 输出当前档案中所有解
    return archive


def nodes(savefile):
    a=set()
    for root, dirs, files in os.walk(savefile):
        for file in files:
            try:
                f = open(savefile + file, "r").read()
                if(len(f)>0):
                    a.add(int(file))
            except:
                pass
    return a

def Go(para):
    nodei = para[0]
    G = para[1]
    file = para[2]
    dataset=para[3]
    f = open(file+str(nodei),"w",encoding="utf-8")
    timef=open("results/test7-30/time/"+dataset+"time/"+str(nodei),"w",encoding="utf-8")
    if (G.graph[nodei] == []):
        f.writelines("")
        timef.writelines("")
        print(nodei,"孤立节点！")
    else:
        a=time.perf_counter()
        result = LocalCommunityDetectionForNodei(nodei, G,archive=[])
        b=time.perf_counter()
        timef.writelines(str(b-a))
        for j in range(0, len(result)):
            for nodes in result[j].nodes:
                f.writelines(str(nodes)+" ")
            f.writelines("\n")
        print(nodei,"成功！")
    f.close()
    timef.close()

if __name__ =="__main__":
    dataset="kite"
    if(sys.argv[1]!=None):
        dataset=sys.argv[1]
    f1 = "dataset/"+dataset+"-graph.txt"
    f2 = "dataset/"+dataset+"-node.txt"
    G = GetNetwork(f1, f2)
    res=LocalCommunityDetectionForNodei(nodei, G,archive=[])
    print(res)
#     savefile = "results/test7-30/"+dataset+"/"
#     timedir="results/test7-30/time/"+dataset+"time/"
#     if not os.path.exists(savefile):
#         os.makedirs(savefile)
#         if not os.path.exists(timedir):
#             os.makedirs(timedir)
#     """
#            kite:[1, 251, 501, 751, 1001, 1251, 1501, 1751, 2001, 2251, 2501, 2751, 3001, 3251, 3501, 3751, 4001, 4251, 4501, 4751, 5001, 5251, 5501, 5751, 6001, 6251, 6501, 6751, 7001, 7251, 7501, 7751, 8001, 8251, 8751, 9001, 9251, 9501, 9751, 10001, 10251, 10501, 10751, 11001, 11251, 11501, 11751, 12001, 12251, 12501, 12751, 13001, 13251, 13501, 13751, 14001, 14251, 14501, 14751, 15001, 15251, 15501, 15751, 16001, 16251, 16501, 16751, 17001, 17251, 17501, 18001, 18251, 18501, 18751, 19001, 19251, 19501, 19751, 20001, 20251, 20751, 21001, 21251, 21501, 21751, 22001, 22251, 22501, 22751, 23001, 23251, 23501, 23751, 24001, 24251, 24501, 24751, 25001, 25251, 25501, 25751, 26001, 26251, 26501, 26751, 27001, 27251, 27501, 27751, 28001, 28251, 28501, 28751, 29001, 29251, 29501, 29751, 30001, 30251, 30501, 30751, 31001, 31251, 31501, 31751, 32001, 32501, 32751, 33001, 33251, 33501, 33751, 34001, 34251, 34501, 34751, 35001, 35501, 35751, 36001, 36251, 36501, 36751, 37001, 37251, 37501, 37751, 38001, 38251, 38501, 38751, 39001, 39251, 39501, 39751, 40001, 40251, 40501, 40751, 41001, 41251, 41501, 41751, 42001, 42251, 42501, 42751, 43001, 43251, 43501, 43751, 44251, 44501, 44751, 45001, 45251, 45501, 45751, 46001, 46251, 46501, 46751, 47001, 47251, 47501, 47751, 48001, 48251, 48501, 48751, 49001, 49251, 49501, 49751, 2, 252, 502, 752, 1002, 1252]
#            gowalla；[1, 501, 1001, 1501, 2001, 2501, 3001, 3501, 4001, 4501, 5001, 5501, 6001, 6501, 7001, 7501, 8001, 8501, 9001, 9501, 10001, 10501, 11001, 11501, 12001, 12501, 13001, 14001, 14501, 15501, 16501, 17001, 17501, 18001, 18501, 19001, 19501, 20001, 20501, 21001, 21501, 22001, 22501, 23001, 23501, 24001, 24501, 25001, 25501, 26501, 27001, 27501, 28501, 29001, 30001, 30501, 31001, 31501, 32001, 32501, 33001, 33501, 34001, 34501, 35001, 35501, 36001, 36501, 37001, 37501, 38001, 38501, 39001, 39501, 40001, 40501, 41001, 41501, 42001, 42501, 43001, 43501, 44001, 44501, 45001, 45501, 46001, 46501, 47001, 47501, 48001, 48501, 49001, 49501, 50001, 50501, 51501, 52501, 53001, 53501, 54001, 54501, 55001, 55501, 56001, 56501, 57501, 58001, 58501, 59001, 59501, 60001, 61001, 61501, 62001, 62501, 63001, 63501, 64001, 64501, 65001, 66001, 66501, 67001, 67501, 68001, 68501, 69001, 69501, 70001, 70501, 71001, 71501, 72001, 72501, 73001, 73501, 74001, 74501, 75001, 75501, 76001, 76501, 77001, 77501, 78001, 78501, 79001, 79501, 80501, 81001, 81501, 82001, 82501, 83001, 83501, 84001, 84501, 85001, 85501, 86001, 86501, 87001, 87501, 88001, 88501, 89501, 90001, 90501, 91001, 91501, 92001, 92501, 93001, 94001, 94501, 95001, 96001, 96501, 97001, 97501, 98001, 98501, 99001, 99501, 2, 502, 1002, 1502, 2002, 2502, 3002, 3502, 4002, 4502, 5002, 5502, 6002, 6502, 7002]
#            filckr:[1, 1001, 2001, 4001, 5001, 6001, 7001, 8001, 9001, 10001, 11001, 12001, 13001, 14001, 15001, 16001, 17001, 18001, 19001, 20001, 22001, 23001, 24001, 25001, 26001, 27001, 28001, 29001, 30001, 31001, 32001, 33001, 36001, 37001, 38001, 40001, 41001, 42001, 46001, 47001, 49001, 50001, 52001, 53001, 54001, 55001, 56001, 57001, 58001, 59001, 61001, 62001, 63001, 67001, 69001, 70001, 71001, 72001, 73001, 74001, 76001, 77001, 78001, 79001, 80001, 81001, 82001, 83001, 84001, 85001, 86001, 88001, 89001, 90001, 91001, 92001, 93001, 94001, 95001, 97001, 98001, 100001, 101001, 102001, 103001, 104001, 108001, 109001, 110001, 111001, 113001, 115001, 116001, 117001, 119001, 121001, 122001, 123001, 125001, 126001, 127001, 130001, 131001, 137001, 138001, 141001, 142001, 144001, 145001, 149001, 151001, 152001, 153001, 154001, 155001, 156001, 157001, 159001, 160001, 161001, 163001, 164001, 166001, 168001, 171001, 172001, 173001, 174001, 175001, 176001, 177001, 178001, 180001, 181001, 182001, 184001, 186001, 187001, 188001, 189001, 190001, 191001, 192001, 193001, 194001, 195001, 196001, 197001, 198001, 2, 1002, 2002, 3002, 4002, 5002, 6002, 7002, 8002, 9002, 10002, 11002, 12002, 13002, 14002, 15002, 17002, 18002, 19002, 20002, 22002, 23002, 24002, 25002, 26002, 27002, 28002, 29002, 30002, 32002, 33002, 34002, 35002, 36002, 37002, 39002, 40002, 41002, 43002, 44002, 45002, 46002, 47002, 48002, 49002, 51002, 52002, 53002, 54002, 55002, 56002]
#            fsq:
#            [1, 10001, 20001, 30001, 40001, 50001, 60001, 70001, 80001, 90001, 100001, 110001, 120001, 140001, 150001, 170001, 180001, 190001, 200001, 230001, 240001, 260001, 270001, 310001, 320001, 330001, 340001, 350001, 360001, 370001, 380001, 390001, 400001, 410001, 420001, 430001, 440001, 450001, 460001, 470001, 480001, 490001, 500001, 510001, 520001, 530001, 540001, 550001, 560001, 570001, 590001, 600001, 610001, 630001, 640001, 650001, 660001, 690001, 700001, 740001, 750001, 760001, 770001, 780001, 790001, 800001, 820001, 830001, 840001, 850001, 860001, 870001, 890001, 900001, 910001, 920001, 930001, 940001, 950001, 960001, 970001, 980001, 990001, 1010001, 1020001, 1030001, 1040001, 1050001, 1060001, 1070001, 1080001, 1090001, 1100001, 1110001, 1120001, 1130001, 1140001, 1150001, 1160001, 1170001, 1190001, 1200001, 1210001, 1220001, 1230001, 1250001, 1260001, 1290001, 1300001, 1340001, 1350001, 1360001, 1370001, 1380001, 1390001, 1410001, 1420001, 1430001, 1440001, 1450001, 1460001, 1480001, 1490001, 1500001, 1510001, 1520001, 1530001, 1540001, 1550001, 1560001, 1570001, 1580001, 1590001, 1600001, 1610001, 1620001, 1630001, 1640001, 1650001, 1660001, 1670001, 1680001, 1690001, 1700001, 1710001, 1720001, 1730001, 1740001, 1750001, 1760001, 1770001, 1780001, 1790001, 1800001, 1810001, 1820001, 1830001, 1840001, 1850001, 1860001, 1870001, 1880001, 1890001, 1900001, 1910001, 1920001, 1930001, 1940001, 1950001, 1960001, 1970001, 1980001, 1990001, 2, 20002, 30002, 40002, 50002, 60002, 70002, 90002, 100002, 120002, 130002, 150002, 170002, 180002, 190002, 200002, 230002, 240002, 260002, 270002, 280002, 290002, 300002, 310002, 320002, 330002, 340002]
#            syn_1:[1, 21, 41, 61, 81, 101, 121, 141, 161, 181, 201, 221, 241, 261, 281, 301, 321, 341, 361, 381, 401, 421, 441, 461, 481, 501, 521, 541, 561, 581, 601, 621, 641, 661, 681, 701, 721, 741, 761, 781, 801, 821, 841, 861, 881, 901, 921, 941, 961, 981, 1001, 1021, 1041, 1061, 1081, 1101, 1121, 1141, 1161, 1181, 1201, 1221, 1241, 1261, 1281, 1301, 1321, 1341, 1361, 1381, 1401, 1421, 1441, 1461, 1481, 1501, 1521, 1541, 1561, 1581, 1601, 1621, 1641, 1661, 1681, 1701, 1721, 1741, 1761, 1781, 1801, 1821, 1841, 1861, 1881, 1901, 1921, 1941, 1961, 1981, 2001, 2021, 2041, 2061, 2081, 2101, 2121, 2141, 2161, 2181, 2201, 2221, 2241, 2261, 2281, 2301, 2321, 2341, 2361, 2381, 2401, 2421, 2441, 2461, 2481, 2501, 2521, 2541, 2561, 2581, 2601, 2621, 2641, 2661, 2681, 2701, 2721, 2741, 2761, 2781, 2801, 2821, 2841, 2861, 2881, 2901, 2921, 2941, 2961, 2981, 3001, 3021, 3041, 3061, 3081, 3101, 3121, 3141, 3161, 3181, 3201, 3221, 3241, 3261, 3281, 3301, 3321, 3341, 3361, 3381, 3401, 3421, 3441, 3461, 3481, 3501, 3521, 3541, 3561, 3581, 3601, 3621, 3641, 3661, 3681, 3701, 3721, 3741, 3761, 3781, 3801, 3821, 3841, 3861, 3881, 3901, 3921, 3941, 3961, 3981]
#            syn_2:[1, 501, 1001, 1501, 2001, 2501, 3001, 3501, 4001, 4501, 5001, 5501, 6001, 6501, 7001, 7501, 8001, 8501, 9001, 9501, 10001, 10501, 11001, 11501, 12001, 12501, 13001, 13501, 14001, 14501, 15001, 15501, 16001, 16501, 17001, 17501, 18001, 18501, 19001, 19501, 20001, 20501, 21001, 21501, 22001, 22501, 23001, 23501, 24001, 24501, 25001, 25501, 26001, 26501, 27001, 27501, 28001, 28501, 29001, 29501, 30001, 30501, 31001, 31501, 32001, 32501, 33001, 33501, 34001, 34501, 35001, 35501, 36001, 36501, 37001, 37501, 38001, 38501, 39001, 39501, 40001, 40501, 41001, 41501, 42001, 42501, 43001, 43501, 44001, 44501, 45001, 45501, 46001, 46501, 47001, 47501, 48001, 48501, 49001, 49501, 50001, 50501, 51001, 51501, 52001, 52501, 53001, 53501, 54001, 54501, 55001, 55501, 56001, 56501, 57001, 57501, 58001, 58501, 59001, 59501, 60001, 60501, 61001, 61501, 62001, 62501, 63001, 63501, 64001, 64501, 65001, 65501, 66001, 66501, 67001, 67501, 68001, 68501, 69001, 69501, 70001, 70501, 71001, 71501, 72001, 72501, 73001, 73501, 74001, 74501, 75001, 75501, 76001, 76501, 77001, 77501, 78001, 78501, 79001, 79501, 80001, 80501, 81001, 81501, 82001, 82501, 83001, 83501, 84001, 84501, 85001, 85501, 86001, 86501, 87001, 87501, 88001, 88501, 89001, 89501, 90001, 90501, 91001, 91501, 92001, 92501, 93001, 93501, 94001, 94501, 95001, 95501, 96001, 96501, 97001, 97501, 98001, 98501, 99001, 99501]
#         """
#     d = {}#nodedict
#     nodelist = d[dataset]
#     have_Ex = nodes(savefile)
#     nodelist = set(nodelist) - have_Ex
#     print(len(nodelist))
#     plist = [[node, G, savefile, dataset] for node in nodelist]
#     pool = multiprocessing.Pool(processes=4)  # 定义最大的进程数
#     pool.map(Go,plist)  # p必须是一个可迭代变量。
#     print("OK")
#     pool.close()
#     pool.join()
