# Created by: Arjun KV, Mohammed Salih C T, Afsal T K, Anandhu VG, National Institute of Technology Calicut
from source import *
import json

f = open('Section.json')
section = json.load(f)

NStory = 8
NBay = 3
WBay = 20			#in foots
HStory1 = 15.09		#in foots
HStoryTyp = 13.12	#in foots
columnSectionExt = ["W24x146","W24x131","W24x94","W24x76"] # 2 succesive colunms have same section
columnSectionInt = ["W24x162","W24x162","W24x131","W24x76"] # 2 succesive colunms have same section
beamSection = ["W27x94","W24x94","W24x76","W18x50"] # 2 succesive floors  have same beam section
FloorWeight = 586.25	#in kips
floorLength = 140.1		#in foots
floorWidth = 100.07		#in foots
lateralLoads = [3.72,8.599,14.33,20.73,27.67,35.09,42.92,51.14,59,67,79,88,95,104,116,125,130,145,155,167]		# in kips

lateralLoadCheck(NStory,lateralLoads,"lateralLoads")
lengthChecker(NStory,columnSectionExt,"columnSectionExt")
lengthChecker(NStory,columnSectionInt,"columnSectionInt")
lengthChecker(NStory,beamSection,"beamSection")
SectionDetailsAdder(section,columnSectionExt)
SectionDetailsAdder(section,columnSectionInt)
SectionDetailsAdder(section,beamSection)
with open(f'MRF_{NStory}S_{NBay}B_Structure.tcl','w') as Element:
	fileDetails(NStory,NBay,Element)
with open(f'MRF_{NStory}S_{NBay}B_Structure.tcl','a') as Element:
	defineBuildingGeometry(NStory,NBay,WBay,HStory1,HStoryTyp,Element)
	locationsOfColumns(NBay,Element)
	locationsOfBeams(NStory,Element)
	panelZoneDim(NStory,NBay,columnSectionExt,columnSectionInt,section,Element)
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
	defineBeamColumnSection(NStory,NBay,columnSectionExt,columnSectionInt,beamSection,section,Element)
	IcolIbeamMod(NStory,NBay,Element)
	Ks_col(NStory,NBay,Element)
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
	GravityLoadLeaningColumn(NStory,NBay,WBay,FloorWeight,floorLength,floorWidth,Element)
	pointLoadonFrame(NStory,NBay,Element)
	Gravityanalysis(Element)
	recorders(NStory,NBay,Element)
	pushOver(NStory,NBay,lateralLoads,Element)
	timeHistory(Element)
	print(NStory,"story",NBay,"bay MRF tcl file is successfully created ")