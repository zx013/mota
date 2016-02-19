#宝石加成值
#(期望终止攻防和 - 初始攻防和) / 宝石数量，取整
#该加成作为基础值，属性增减都为该数值整数倍

#monster类型，H(ealth), A(ttack), D(efence)

#商店的属性选择（A，D），极少数情况下选择H
#整体
#A >= max(h + d)				A
#A + D > max(a) + max(d)		A -> max(d), D -> max(a), A or D
#A <= max(d)					None

#个体
#A >= h + d						A
#A + D > a + d					A -> d, D -> a, A or D
#A + D <= a + d					A
#A <= d							None

#A -> d
#if A + D > a + d:
#	A or D -> a
#A