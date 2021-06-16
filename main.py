from sample import *

NStory = 8
NBay = 3
WBay = 20
HStory1 = 15.09
HStoryTyp = 13.12
extColDepth = [24.74,24.48,24.31,23.92] #exterior column depth, 2 successive colunms have same depth
intColDepth = [25,25,24.48,23.92] #interior column depth, 2 successive colunms have same depth
beamDepth = [26.92,24.31,23.92,17.99] #beam column depth, 2 successive colunms have same depth
columnSectionExt = ["W24X146","W24X131","W24X94","W24X76"] # 2 succesive colunms have same section
columnSectionInt = ["W24X162","W24X162","W24X131","W24X76"] # 2 succesive colunms have same section
beamSection = ["W27X94","W24X94","W24X76","W18X50"] # 2 succesive floors  have same beam section
FloorWeight=586.25

with open('test.tcl','w') as Element:
	fileDetails(NStory,NBay,Element)
with open('test.tcl','a') as Element:
	defineBuildingGeometry(NStory,NBay,WBay,HStory1,HStoryTyp,Element)
	locationsOfColumns(NBay,Element)
	locationsOfBeams(NStory,Element)
	panelZoneDimExt(NStory,extColDepth,Element)
	panelZoneDimInt(NStory,intColDepth,Element)
	panelZoneDimVert(NStory,beamDepth,Element)
	plasticHingeOffset(NStory,Element)
	CalculateNodalMass(NBay,FloorWeight,Element)
	defineNodes(NStory,NBay,Element)
	ColumnHingeNodes(NStory,NBay,Element)
	beamHingeNodes(NStory,NBay,Element)
	panelZoneNodes(NStory,NBay,Element)
	nodalmasscreator(NStory,NBay,Element)
	degreesOfFreedom(NStory,NBay,Element)
	assignBoundaryCondidtions(NBay,Element)
