
def elemPanelZone2DCreator(story,bay,Element):
    for floor in range(2,story+2):
        for pier in range(1,bay+1):
            elemPanelZone2D="elemPanelZone2D   500{p}{f}1 {p}{f}01 $Es $Apz $Ipz $PDeltaTransf;	# Pier {p}, Floor {f}".format(p=pier,f=floor)
            print(elemPanelZone2D,file=Element)
        print("",file=Element)

def defineBuildingGeometry(story,bay,WBays,HStory1,Hstorytyp,Element):
    header="""###################################################################################################
#          Define Building Geometry, Nodes, Masses, and Constraints											  
###################################################################################################
# define structure-geometry parameters
	set NStories {s};						# number of stories
	set NBays {b};						# number of frame bays (excludes bay for P-delta column)
	set WBay      [expr {wb}*12.0];		# bay width in inches
	set HStory1   [expr {hs1}*12.0];		# 1st story height in inches
	set HStoryTyp [expr {hst}*12.0];		# story height of other stories in inches
	set HBuilding [expr $HStory1 + ($NStories-1)*$HStoryTyp];	# height of building""".format(
        s=story,b=bay,wb=WBays,hs1=HStory1,hst=Hstorytyp
    )
    print(header,file=Element)

def locationsOfBeams(NBay,Element):
    beam1="""# calculate locations of beam-column joint centerlines:
    set Pier1  0.0;		# leftmost column line"""
    print(beam1,end="",file=Element)
    for i in range(2,NBay+3):
        beams="""set Pier{p}  [expr $Pier{leftp} + $WBay];""".format(
            p=i, leftp=i-1 
        )
        print("\n   ",beams,end="",file=Element)
    print(" # P-delta column line",file=Element)


def nodalmasscreator(story,bay,Element):
    for floor in range(2,story+2):
        for pier in range(1,bay+1):
            nodalmass="mass {p}{f}05 $NodalMass $Negligible $Negligible;	# Pier {p}, Floor {f}".format(p=pier,f=floor)
            print(nodalmass,file=Element)
        print("",file=Element)

def degreesOfFreedom(story,bay,Element):
    for floor in range(2,story+2):
            for pier in range(2,bay+3):
                if pier<=bay+1:
                    dof="equalDOF 1{f}05 {p}205 $dof1;		# Floor {f}:  Pier 1 to Pier {p}".format(p=pier,f=floor)
                    print(dof,file=Element)
                else:
                    dof="equalDOF 1{f}05 {p}{f} $dof1;		        # Floor {f}:  Pier 1 to Pier {p}".format(p=pier,f=floor)
                    print(dof,file=Element)
            print("",file=Element)

def assignBoundaryCondidtions(bay,Element):
    for pier in range(1,bay+3):
        if pier<bay+2:
            boundarycondition="""fix {p}1 1 1 {d};""".format(p=pier,d=str(1))
            print (boundarycondition,file=Element)  
        else:
            boundarycondition="""fix {p}1 1 1 {d};""".format(p=pier,d=str(0))
            print (boundarycondition,file=Element)    