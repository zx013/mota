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


#怪物分布设计
#方案1：按顺序由弱到强随机分布monster和gem，并由此计算出最佳路径和所有可能的路径数量，如果最佳路径在合理范围内，则放置potion，使hero中途health不小于等于0
#方案2：monster和gem分组匹配，计算最优顺序，并填入potion，将最优顺序依次放入序列中