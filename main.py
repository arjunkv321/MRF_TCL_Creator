from sample import *

NStory = 8
NBay = 3
WBay = 20
HStory1 = 15.09
HStoryTyp = 13.12
extColDepth = [24.74,24.48,24.31,23.92] #exterior column depth, 2 successive colunms have same depth
intColDepth = [25,25,24.48,23.92] #interior column depth, 2 successive colunms have same depth
beamDepth = [26.92,24.31,23.92,17.99] #beam column depth, 2 successive colunms have same depth

with open('test.tcl','w') as Element:
	elemPanelZone2DCreator(NStory,NBay,Element)
    