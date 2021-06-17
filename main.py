from sample import *
import json

f = open('Section.json')
section = json.load(f)

NStory = 8
NBay = 3
WBay = 20
HStory1 = 15.09
HStoryTyp = 13.12
columnSectionExt = ["W24x146","W24x131","W24x94","W24x76"] # 2 succesive colunms have same section
columnSectionInt = ["W24x162","W24x162","W24x131","W24x76"] # 2 succesive colunms have same section
beamSection = ["W27x94","W24x94","W24x76","W18x50"] # 2 succesive floors  have same beam section
FloorWeight=586.25
lateralLoads = [3.72,8.599,14.33,20.73,27.67,35.09,42.92,51.14]

with open('test.tcl','w') as Element:
	fileDetails(NStory,NBay,Element)
with open('test.tcl','a') as Element:
	defineBuildingGeometry(NStory,NBay,WBay,HStory1,HStoryTyp,Element)
	locationsOfColumns(NBay,Element)
	locationsOfBeams(NStory,Element)
	panelZoneDimExt(NStory,columnSectionExt,section,Element)
	panelZoneDimInt(NStory,columnSectionInt,section,Element)
	panelZoneDimVert(NStory,beamSection,section,Element)
	plasticHingeOffset(NStory,NBay,Element)
	CalculateNodalMass(NBay,FloorWeight,Element)
	defineNodes(NStory,NBay,Element)
	ColumnHingeNodes(NStory,NBay,Element)
	beamHingeNodes(NStory,NBay,Element)
	panelZoneNodes(NStory,NBay,Element)
	nodalmasscreator(NStory,NBay,Element)
	degreesOfFreedom(NStory,NBay,Element)
	assignBoundaryCondidtions(NBay,Element)
	defineBeamColumnSection(NStory,columnSectionExt,columnSectionInt,beamSection,section,Element)
	IcolIbeamMod(NStory,Element)
	Ks_col(NStory,Element)
	Ks_beam(NStory,NBay,Element)
	elasticColumnElement(NStory,NBay,Element)
	elasticBeamColumnElements(NStory,NBay,Element)
	elementTrussPdelta(NStory,NBay,Element)
	pdeltaElasticColumn(NStory,NBay,Element)
	elemPanelZone2DCreator(NStory,NBay,Element)
	DefineProps(Element)
	defineColumnSprings(NStory,NBay,Element)
	beamSprings(NStory,NBay,Element)
	definePanelZoneSpring(NStory,NBay,Element)
	pDeltaSprings(NStory,NBay,Element)
	eigenValue(Element)
	GravityLoadLeaningColumn(NStory,Element)
	pointLoadonFrame(NStory,NBay,Element)
	Gravityanalysis(Element)
	recorders(NStory,NBay,Element)
	pushOver(NStory,NBay,lateralLoads,Element)