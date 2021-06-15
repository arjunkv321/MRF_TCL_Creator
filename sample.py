
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







