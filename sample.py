
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

def locationsOfColumns(NBay,Element):
    column1="""# calculate locations of Beam-column joint centerlines:
    set Pier1  0.0;		# leftmost column line"""
    print(column1,end="",file=Element)
    for i in range(2,NBay+3):
        columns="""set Pier{p}  [expr $Pier{leftp} + $WBay];""".format(
            p=i, leftp=i-1 
        )
        print("\n   ",columns,end="",file=Element)
    print(" # P-delta column line",file=Element)

def locationsOfBeams(NStory):
    beam12="""
    set Floor1 0.0;		# ground floor
    set Floor2 [expr $Floor1 + $HStory1];"""
    print("\t",beam12)
    for i in range(3,NStory+2):
        beams="set Floor{f} [expr $Floor{downf} + $HStoryTyp];".format(
            f=i, downf=i-1 
        )
        print("   ",beams)

def elementTrussPdelta(story,bay,Element): 
    for floor in range(2,story+2):
        elementTruss="element truss  6{p1}{f} {p1}{f}05 {p2}{f} $Arigid $TrussMatID;	# Floor {f}".format(f=floor,p1=bay+1,p2=bay+2)
        print (elementTruss,file=Element)

def panelZoneDimExt(NStory,extColDepth,Element):
    header="""# calculate panel zone dimensions 
    # lateral dist from CL of beam-col joint to edge of panel zone (= half the column depth), xy x=floor y=nextfloor, ext=external,int=internal"""
    print(header,file=Element)
    for i in range(2,NStory+1,2):
        pzlat = "set pzlatext{f1}{f2}   [expr {d}/2.0];".format(
            f1=i, f2=i+1, d=extColDepth[i//2-1]
        )
        print("   ",pzlat,file=Element)

def panelZoneDimInt(NStory,intColDepth,Element):
    for i in range(2,NStory+1,2):
        pzlat = "set pzlatint{f1}{f2}   [expr {d}/2.0];".format(
            f1=i, f2=i+1, d=intColDepth[i//2-1]
        )
        print("   ",pzlat,file=Element)

def panelZoneDimVert(NStory,beamDepth,Element):
    for i in range(2,NStory+1,2):
        pzvert = "set pzvert{f1}{f2}   [expr {d}/2.0];".format(
            f1=i, f2=i+1, d=beamDepth[i//2-1]
        )
        print("   ",pzvert,file=Element)

def plasticHingeOffset(NStory,Element):
    header="""# calculate plastic hinge offsets from beam-column centerlines:
    # lateral dist from CL of beam-col joint to beam hinge, xy x=floor y=nextfloor, ext=external,int=internal"""
    print(header,file=Element)
    for i in range(2,NStory+1,2):
        phlat = "set phlatint{f1}{f2} [expr $pzlatent{f1}{f2}  + 7.5 + 22.5/2.0];".format(
            f1=i, f2=i+1
        )
        print("   ",phlat,file=Element)
    print("\n",end="")
    for i in range(2,NStory+1,2):
        phlat = "set phlatint{f1}{f2} [expr $pzlatent{f1}{f2}  + 7.5 + 22.5/2.0];".format(
            f1=i, f2=i+1
        )
        print("   ",phlat,file=Element)

    header="""
# vert dist from CL of beam-col joint to column hinge (forms at edge of panel zone)"""
    print(header,file=Element)
    for i in range(2,NStory+1,2):
        phvert = "set phvert{f1}{f2} [expr $pzvert{f1}{f2}  + 0.0];".format(
            f1=i, f2=i+1
        )
        print("   ",phvert,file=Element)

def defineNodes(NStory,NBays,Element):
    header="""
# define nodes and assign masses to beam-column intersections of frame
    # command:  node nodeID xcoord ycoord -mass mass_dof1 mass_dof2 mass_dof3
    # nodeID convention:  "xy" where x = Pier # and y = Floor # """
    print(header,file=Element)
    for i in range(1,NBays+3):
        node = "node {b}1 $Pier{b} $Floor1;".format(b=i)
        print("   ",node,file=Element)
    for i in range(2,NStory+1):
        node = "node 5{s} $Pier5 $Floor{s};".format(s=i)
        print("   ",node,file=Element)

def defineColumnSprings(NStory,NBay,Element):
	mycol=1
	for NStory in range(1,NStory+1):
		print("""\n set a_memext [expr ($n+1.0)*($Mycol_ext{cola}{colb}*($McMy-1.0)) / ($Ks_col_ext{s}*$th_pP)];	# strain hardening ratio of spring
	set bext [expr ($a_memext)/(1.0+$n*(1.0-$a_memext))];					# modified strain hardening ratio of spring (Ibarra & Krawinkler 2005, note: Eqn B.5 is incorrect)
	set a_memint [expr ($n+1.0)*($Mycol_int{cola}{colb}*($McMy-1.0)) / ($Ks_col_int{s}*$th_pP)];	# strain hardening ratio of spring
	set bint [expr ($a_memint)/(1.0+$n*(1.0-$a_memint))];					# modified strain hardening ratio of spring (Ibarra & Krawinkler 2005, note: Eqn B.5 is incorrect)""".format(cola=mycol, colb=mycol+1,s=NStory),file=Element)
		for dir in range(2):
			if dir%2==0:
				if NStory>1:
					
					print("\n# col springs @ bottom of Story {s} (at base)".format(s=NStory),file=Element)
					for pier in range(1,NBay+2):
						if pier == 1 or pier == NBay+1:
							print("rotSpring2DModIKModel 3{p}{s}2 {p}{s}7 {p}{s}8 $Ks_col_{pos}{s} $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(s=NStory, f=NStory+1, p=str(pier), pos="ext", cola=mycol, colb=mycol+1),file=Element)
						else:
							print("rotSpring2DModIKModel 3{p}{s}2 {p}{s}7 {p}{s}8 $Ks_col_{pos}{s} $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(s=NStory, f=NStory+1, p=str(pier), pos="int", cola=mycol, colb=mycol+1),file=Element)
					if NStory%2==1:
						mycol+=2
				else:
					for pier in range(1,NBay+2):
						if pier == 1 or pier == NBay+1:
							print("rotSpring2DModIKModel 3{p}11 {p}1 {p}17 $Ks_col_{pos}1 $b{pos} $b{pos} $Mycol_{pos} [expr -$Mycol_{pos}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(p=pier, pos="ext"),file=Element)
						else:
							print("rotSpring2DModIKModel 3{p}11 {p}1 {p}17 $Ks_col_{pos}1 $b{pos} $b{pos} $Mycol_{pos} [expr -$Mycol_{pos}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(p=pier, pos="int"),file=Element)

			else:
				print("\n#col springs @ top of Story {s}".format(s=NStory),file=Element)
				for pier in range(1,NBay+2):
					if pier == 1 or pier == NBay+1:
						print("rotSpring2DModIKModel 3{p}{s}2 {p}{f}6 {p}{f}5 $Ks_col_{pos}{s} $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(s=NStory, f=NStory+1, p=str(pier), pos="ext", cola=mycol, colb=mycol+1),file=Element)
					else:
						print("rotSpring2DModIKModel 3{p}{s}2 {p}{f}6 {p}{f}5 $Ks_col_{pos}{s} $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(s=NStory, f=NStory+1, p=str(pier), pos="int", cola=mycol, colb=mycol+1),file=Element)

def Ks_col(NStory,Element):
    story1 = """# calculate modified rotational stiffness for plastic hinge springs: use length between springs //
    set Ks_col_ext1   [expr $n*6.0*$Es*$Icol_ext12mod/($HStory1-$phvert23)];		# rotational stiffness of Story 1, external column springs 
    set Ks_col_int1   [expr $n*6.0*$Es*$Icol_int12mod/($HStory1-$phvert23)];		# rotational stiffness of Story 1, internal column springs """
    print("   ",story1,file=Element)
    for i in range(2,NStory+1):
        if i%2==0:
            story="""set Ks_col_ext{s}   [expr $n*6.0*$Es*$Icol_ext{f1}{s}mod/($HStoryTyp-$phvert{s}{f3}-$phvert{s}{f3})];	# rotational stiffness of Story {s} external column springs
    set Ks_col_int{s}   [expr $n*6.0*$Es*$Icol_int{f1}{s}mod/($HStoryTyp-$phvert{s}{f3}-$phvert{s}{f3})]; 	# rotational stiffness of Story {s} internal column springs""".format(
            s=i, f1=i-1, f3= i+1
        )
            print("   ",story,file=Element)
        else:
            story="""set Ks_col_ext{s}   [expr $n*6.0*$Es*$Icol_ext{s}{f2}mod/($HStoryTyp-$phvert{f}{s}-$phvert{f2}{f3})];	# rotational stiffness of Story {s} external column springs
    set Ks_col_int{s}   [expr $n*6.0*$Es*$Icol_int{s}{f2}mod/($HStoryTyp-$phvert{f}{s}-$phvert{f2}{f3})]; 	# rotational stiffness of Story {s} internal column springs""".format(
            s=i, f=i-1, f2=i+1, f3= i+2
        )
            print("   ",story,file=Element)

def IcolIbeamMod(NStory,Element):
    header="""    # determine stiffness modifications to equate the stiffness of the spring-elastic element-spring subassembly to the stiffness of the actual frame member
    # References: (1) Ibarra, L. F., and Krawinkler, H. (2005). "Global collapse of frame structures under seismic excitations," Technical Report 152,
    #             		The John A. Blume Earthquake Engineering Research Center, Department of Civil Engineering, Stanford University, Stanford, CA.
    #			  (2) Zareian, F. and Medina, R. A. (2010). A practical method for proper modeling of structural damping in inelastic plane
    #					structural systems, Computers & Structures, Vol. 88, 1-2, pp. 45-53.
    # calculate modified section properties to account for spring stiffness being in series with the elastic element stiffness
    set n 10.0;		# stiffness multiplier for rotational spring

    # calculate modified moment of inertia for elastic elements between plastic hinge springs"""
    print(header,file=Element)
    
    for i in range(1,NStory,2):
        Icol = """set Icol_ext{f1}{f2}mod  [expr $Icol_ext{f1}{f2}*($n+1.0)/$n];	# modified moment of inertia for external columns in Story {f1},{f2}
    set Icol_int{f1}{f2}mod  [expr $Icol_int{f1}{f2}*($n+1.0)/$n];	# modified moment of inertia for internal columns in Story {f1},{f2}""".format(
        f1=i, f2=i+1
        )
        print("   ",Icol,file=Element)
    print("",file=Element)

    for i in range(1,NStory,2):
        Ibeam = "set Ibeam_{f1}{f2}mod [expr $Ibeam_{f1}{f2}*($n+1.0)/$n];	# modified moment of inertia for beams in Floor {f1}.{f2}".format(
            f1=i+1, f2=i+2
        )
        print("   ",Ibeam,file=Element)
    
def Ks_beam(NStory,Nbays,Element):
    header = "    #Ks_beam_y1y2z y1=floor y2floor z = bay"
    print(header,file=Element)
    for i in range(2,NStory+1,2):
        for j in range(1,Nbays+1):
            ksb="set Ks_beam_{f1}{f2}{b} [expr $n*6.0*$Es*$Ibeam_{f1}{f2}mod/($WBay-$phlatext{f1}{f2}-$phlatint{f1}{f2})];		# rotational stiffness of Floor {f1},{f2} & Bay {b} beam springs".format(
                f1=i, f2=i+1, b=j
            )
            print("   ",ksb,file=Element)

def ColumnHingeNodes(NStory,NBay,Element):
	vert=2
	for NStory in range(1,NStory+1):
		for dir in range(2):
			if dir%2==0:
				if NStory>1:
					print("    # column hinges at bottom of story {s}".format(s=NStory),file=Element)
					for pier in range(1,NBay+3):
						if pier < NBay+2:
							print(("    node {p}{f}7 $Pier{p} [expr $Floor{f} + $phvert{v1}{v2}];").format(p=pier,f=NStory,v1=vert,v2=vert+1),file=Element)
							print(("    node {p}{f}8 $Pier{p} [expr $Floor{f} + $phvert{v1}{v2}];").format(p=pier,f=NStory,v1=vert,v2=vert+1),file=Element)
						else:
							print(("    node {p}{f}7 $Pier{p} $Floor{f};	# zero-stiffness spring will be used on p-delta column").format(p=pier,f=NStory),file=Element)
					if NStory%2==1:
						print("    # column hinges at mid of story {s}".format(s=NStory),file=Element)
						for pier in range(1,NBay+2):
							print(("    node {p}{s}0 $Pier1 [expr $Floor{s} + $phvert{v1}{v2} + 0.5*$HNStoryTyp];	#xy0, x=pier y=floor").format(p=pier,s=NStory,v1=vert,v2=vert+1),file=Element)
						vert+=2
				else:
					print( "    # column hinges at bottom of story 1 (base)",file=Element)
					for pier in range(1,NBay+2):
						print(("    node {p}17 $Pier{p} $Floor1;").format(p=pier),file=Element)
			else:
				print("    # column hinges at top of story {s}".format(s=NStory),file=Element)
				for pier in range(1,NBay+3):
					if pier < NBay+2:
						print(("    node {p}{f}5 $Pier{p} [expr $Floor{f} - $phvert{v1}{v2}];").format(p=pier,f=NStory+1,v1=vert,v2=vert+1),file=Element)
						print(("    node {p}{f}6 $Pier{p} [expr $Floor{f} - $phvert{v1}{v2}];").format(p=pier,f=NStory+1,v1=vert,v2=vert+1),file=Element)
					else:
						print(("    node {p}{f}6 $Pier{p} $Floor{f};	# zero-stiffness spring will be used on p-delta column\n").format(p=pier,f=NStory+1,f2=NStory),file=Element)

def elasticColumnElement(NStory,Nbay,Element):
    header="""# set up geometric transformation of elements
	set PDeltaTransf 1;
	geomTransf PDelta $PDeltaTransf; 	# PDelta transformation

# define elastic column elements using "element" command
	# command: element elasticBeamColumn $eleID $iNode $jNode $A $E $I $transfID
	# eleID convention:  "1xy" where 1 = col, x = Pier #, y = Story #"""
    print(header,file=Element)
    for i in range(1,NStory+1):
        if i==1 :
            print(("    # Columns Story {s}".format(s=i)),file=Element)
            for j in range(1,Nbay+2):
                elem = "    element elasticBeamColumn  1{p}{s}  {p}{s}7 {p}{s2}5 $Acol_ext{s}{s2} $Es $Icol_ext{s}{s2}mod $PDeltaTransf;	# Pier {p}".format(
                    p=j, s=i, s2=i+1, f=i-1
                )
                print(elem,file=Element)
        elif i==1 or i>1 and i%2==0:
            print(("    # Columns Story {s}".format(s=i)),file=Element)
            for j in range(1,Nbay+2):
                elem = "    element elasticBeamColumn  1{p}{s}  {p}{s}8 {p}{s2}5 $Acol_ext{f}{s} $Es $Icol_ext{f}{s}mod $PDeltaTransf;	# Pier {p}".format(
                    p=j, s=i, s2=i+1, f=i-1
                )
                print(elem,file=Element)
        else:
            print(("    # Columns Story {s} below node splice // xyza x=column y=pier z=story a=1,2 1=down 2=up".format(s=i)),file=Element)
            for j in range(1,Nbay+2):
                elem = "    element elasticBeamColumn  1{p}{s}1  {p}{s}8 {p}{s}0 $Acol_ext{f1}{f2} $Es $Icol_ext{f1}{f2}mod $PDeltaTransf;	# Pier {p}".format(
                    p=j, s=i, f1=i-2, f2=i-1
                )
                print(elem,file=Element)
            print(("    # Columns Story {s} above node splice // xyza x=column y=pier z=story a=1,2 1=down 2=up".format(s=i)),file=Element)
            for j in range(1,Nbay+2):
                elem = "    element elasticBeamColumn  1{p}{s}2  {p}{s}0 {p}{s2}5 $Acol_ext{s}{s2} $Es $Icol_ext{s}{s2}mod $PDeltaTransf;	# Pier {p}".format(
                    p=j, s=i, s2=i+1
                )
                print(elem,file=Element)