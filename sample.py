import json

def elemPanelZone2DCreator(story,bay,Element):
    header="""\n# define elastic panel zone elements (assume rigid)
	# elemPanelZone2D creates 8 elastic elements that form a rectangular panel zone
	# references provided in elemPanelZone2D.tcl
	# note: the nodeID and eleID of the upper left corner of the PZ must be imported
	# eleID convention:  500xya, 500 = panel zone element, x = Pier #, y = Floor #
	# "a" convention: defined in elemPanelZone2D.tcl, but 1 = top left element
	set Apz 1000.0;	# area of panel zone element (make much larger than A of frame elements)
	set Ipz 1.0e5;  # moment of intertia of panel zone element (make much larger than I of frame elements)
    # elemPanelZone2D eleID  nodeR E  A_PZ I_PZ transfTag"""
    print(header,file=Element)
    for floor in range(2,story+2):
        for pier in range(1,bay+2):
            elemPanelZone2D="    elemPanelZone2D   500{p}{f}1 {p}{f}01 $Es $Apz $Ipz $PDeltaTransf;	# Pier {p}, Floor {f}".format(p=pier,f=floor)
            print(elemPanelZone2D,file=Element)
        print("",file=Element)
    print("""# display the model with the node numbers
	DisplayModel2D NodeNumbers;""",file=Element)

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
    print("""# define nodal masses:  lump at beam-column joints in frame
	# command: mass $nodeID5$dof1mass $dof2mass $dof3mass""",file=Element)
    for floor in range(2,story+2):
        for pier in range(1,bay+2):
            nodalmass="    mass {p}{f}05 $NodalMass $Negligible $Negligible;	# Pier {p}, Floor {f}".format(p=pier,f=floor)
            print(nodalmass,file=Element)
        print("",file=Element)

def degreesOfFreedom(story,bay,Element):
    print("""# constrain beam-column joints in a floor to have the same lateral displacement using the "equalDOF" command
	# command: equalDOF $MasterNodeID $SlaveNodeID $dof1 $dof2...
    set dof1 1;	# constrain movement in dof 1 (x-direction)""",file=Element)
    for floor in range(2,story+2):
        for pier in range(2,bay+3):
            if pier<=bay+1:
                dof="    equalDOF 1{f}05 {p}{f}05 $dof1;		# Floor {f}:  Pier 1 to Pier {p}".format(p=pier,f=floor)
                print(dof,file=Element)
            else:
                dof="    equalDOF 1{f}05 {p}{f} $dof1;		    # Floor {f}:  Pier 1 to Pier {p}".format(p=pier,f=floor)
                print(dof,file=Element)
        print("",file=Element)

def assignBoundaryCondidtions(bay,Element):
    print("""# assign boundary condidtions 
	# command:  fix nodeID dxFixity dyFixity rzFixity
	# fixity values: 1 = constrained; 0 = unconstrained
	# fix the base of the building; pin P-delta column at base""",file=Element)
    for pier in range(1,bay+3):
        if pier<bay+2:
            boundarycondition="""    fix {p}1 1 1 {d};""".format(p=pier,d=str(1))
            print (boundarycondition,file=Element)  
        else:
            boundarycondition="""    fix {p}1 1 1 {d};   # P-delta column is pinned""".format(p=pier,d=str(0))
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

def locationsOfBeams(NStory,Element):
    beam12="""
    set Floor1 0.0;		# ground floor
    set Floor2 [expr $Floor1 + $HStory1];"""
    print("\t",beam12,file=Element)
    for i in range(3,NStory+2):
        beams="set Floor{f} [expr $Floor{downf} + $HStoryTyp];".format(
            f=i, downf=i-1 
        )
        print("   ",beams,file=Element)

def elementTrussPdelta(story,bay,Element):
    header="""# define p-delta columns and rigid links
    set TrussMatID 600;		# define a material ID
    set Arigid 1000.0;		# define area of truss section (make much larger than A of frame elements)
    set Irigid 100000.0;	# moment of inertia for p-delta columns  (make much larger than I of frame elements)
    uniaxialMaterial Elastic $TrussMatID $Es;		# define truss material
    # rigid links
    # command: element truss $eleID $iNode $jNode $A $materialID
    # eleID convention:  6xy, 6 = truss link, x = Bay #, y = Floor #"""
    print(header,file=Element) 
    for floor in range(2,story+2):
        elementTruss="    element truss  6{p1}{f} {p1}{f}05 {p2}{f} $Arigid $TrussMatID;	# Floor {f}".format(f=floor,p1=bay+1,p2=bay+2)
        print (elementTruss,file=Element)

def panelZoneDim(NStory,NBay,columnSectionExt,columnSectionInt,section,Element):
    header="""# calculate panel zone dimensions 
    # lateral dist from CL of beam-col joint to edge of panel zone (= half the column depth), xy x=floor y=nextfloor, ext=external,int=internal"""
    print(header,file=Element)
    for i in range(2,NStory+1,2):
        sec=columnSectionExt[i//2-1]
        pzlat = "set pzlatext{f1}{f2}   [expr {d}/2.0];".format(
            f1=i, f2=i+1, d=section[sec]["dcol"]
        )
        print("   ",pzlat,file=Element)
    print("",file=Element)
    if NBay>1:
        for i in range(2,NStory+1,2):
            sec = columnSectionInt[i//2-1]
            pzlat = "set pzlatint{f1}{f2}   [expr {d}/2.0];".format(
                f1=i, f2=i+1, d=section[sec]["dcol"]
            )
            print("   ",pzlat,file=Element)
        print("",file=Element)

def panelZoneDimVert(NStory,beamSection,section,Element):
    for i in range(2,NStory+1,2):
        sec=beamSection[i//2-1]
        pzvert = "set pzvert{f1}{f2}   [expr {d}/2.0];".format(
            f1=i, f2=i+1, d=section[sec]["dcol"]
        )
        print("   ",pzvert,file=Element)
    print("",file=Element)

def plasticHingeOffset(NStory,NBay,Element):
    header="""# calculate plastic hinge offsets from beam-column centerlines:
    # lateral dist from CL of beam-col joint to beam hinge, xy x=floor y=nextfloor, ext=external,int=internal"""
    print(header,file=Element)
    for i in range(2,NStory+1,2):
        phlat = "set phlatext{f1}{f2} [expr $pzlatext{f1}{f2}  + 7.5 + 22.5/2.0];".format(
            f1=i, f2=i+1
        )
        print("   ",phlat,file=Element)
    print("\n",end="")
    if NBay>2:
        for i in range(2,NStory+1,2):
            phlat = "set phlatint{f1}{f2} [expr $pzlatint{f1}{f2}  + 7.5 + 22.5/2.0];".format(
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
    for i in range(2,NStory+2):
        node = f"node {NBays+2}{i} $Pier{NBays+2} $Floor{i};"
        print("   ",node,file=Element)

def defineColumnSprings(NStory,NBay,Element):
    SpringArray=[]
    mycol=1
    for NStory in range(1,NStory+1):
        print("""\n    # compute strain hardening Story {s}
    set a_memext [expr ($n+1.0)*($Mycol_ext{cola}{colb}*($McMy-1.0)) / ($Ks_col_ext{s}*$th_pP)];	# strain hardening ratio of spring
    set bext [expr ($a_memext)/(1.0+$n*(1.0-$a_memext))];					# modified strain hardening ratio of spring (Ibarra & Krawinkler 2005, note: Eqn B.5 is incorrect)""".format(cola=mycol, colb=mycol+1,s=NStory),file=Element)
        if NBay>1:
            print("""    set a_memint [expr ($n+1.0)*($Mycol_int{cola}{colb}*($McMy-1.0)) / ($Ks_col_int{s}*$th_pP)];	# strain hardening ratio of spring
    set bint [expr ($a_memint)/(1.0+$n*(1.0-$a_memint))];					# modified strain hardening ratio of spring (Ibarra & Krawinkler 2005, note: Eqn B.5 is incorrect)""".format(cola=mycol, colb=mycol+1,s=NStory),file=Element)
        for dir in range(2):
            if dir%2==0:
                if NStory>1:
                    
                    print("\n    # col springs @ bottom of Story {s} (at base)".format(s=NStory),file=Element)
                    for pier in range(1,NBay+2):
                        if pier == 1 or pier == NBay+1:
                            print("    rotSpring2DModIKModel 3{p}{s}1 {p}{s}7 {p}{s}8 $Ks_col_{pos}{s} $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(s=NStory, f=NStory+1, p=str(pier), pos="ext", cola=mycol, colb=mycol+1),file=Element)
                            SpringArray.append("3"+str(pier)+str(NStory)+"1")
                        else:
                            print("    rotSpring2DModIKModel 3{p}{s}1 {p}{s}7 {p}{s}8 $Ks_col_{pos}{s} $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(s=NStory, f=NStory+1, p=str(pier), pos="int", cola=mycol, colb=mycol+1),file=Element)
                            SpringArray.append("3"+str(pier)+str(NStory)+"1")
                    if NStory%2==1:
                        mycol+=2
                else:
                    for pier in range(1,NBay+2):
                        if pier == 1 or pier == NBay+1:
                            print("    rotSpring2DModIKModel 3{p}11 {p}1 {p}17 $Ks_col_{pos}1 $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(p=pier, pos="ext",cola=mycol, colb=mycol+1),file=Element)
                            SpringArray.append("3"+str(pier)+"11")
                        else:
                            print("    rotSpring2DModIKModel 3{p}11 {p}1 {p}17 $Ks_col_{pos}1 $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(p=pier, pos="int",cola=mycol, colb=mycol+1),file=Element)
                            SpringArray.append("3"+str(pier)+"11")
            else:
                print("\n    #col springs @ top of Story {s}".format(s=NStory),file=Element)
                for pier in range(1,NBay+2):
                    if pier == 1 or pier == NBay+1:
                        print("    rotSpring2DModIKModel 3{p}{s}2 {p}{f}6 {p}{f}5 $Ks_col_{pos}{s} $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(s=NStory, f=NStory+1, p=str(pier), pos="ext", cola=mycol, colb=mycol+1),file=Element)
                        SpringArray.append("3"+str(pier)+str(NStory)+"2")
                    else:
                        print("    rotSpring2DModIKModel 3{p}{s}2 {p}{f}6 {p}{f}5 $Ks_col_{pos}{s} $b{pos} $b{pos} $Mycol_{pos}{cola}{colb} [expr -$Mycol_{pos}{cola}{colb}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;".format(s=NStory, f=NStory+1, p=str(pier), pos="int", cola=mycol, colb=mycol+1),file=Element)
                        SpringArray.append("3"+str(pier)+str(NStory)+"2")
    print("""    # create region for frame column springs
    # command: region $regionID -ele $ele_1_ID $ele_2_ID...
    region 1 -ele""",end=" ",file=Element)
    for nodes in SpringArray:
	    print(nodes,end=" ",file=Element)
    print(";",file=Element)


def Ks_col(NStory,NBay,Element):
    print("""\n    # calculate modified rotational stiffness for plastic hinge springs: use length between springs //
    set Ks_col_ext1   [expr $n*6.0*$Es*$Icol_ext12mod/($HStory1-$phvert23)];		# rotational stiffness of Story 1, external column springs """,file=Element)
    if NBay>1:
        print("    set Ks_col_int1   [expr $n*6.0*$Es*$Icol_int12mod/($HStory1-$phvert23)];		# rotational stiffness of Story 1, internal column springs ",file=Element)
    
    for i in range(2,NStory+1):
        if i%2==0:
            print("    set Ks_col_ext{s}   [expr $n*6.0*$Es*$Icol_ext{f1}{s}mod/($HStoryTyp-$phvert{s}{f3}-$phvert{s}{f3})];	# rotational stiffness of Story {s} external column springs".format(s=i, f1=i-1, f3= i+1),file=Element)
            if NBay>1:
                print("    set Ks_col_int{s}   [expr $n*6.0*$Es*$Icol_int{f1}{s}mod/($HStoryTyp-$phvert{s}{f3}-$phvert{s}{f3})]; 	# rotational stiffness of Story {s} internal column springs".format(s=i, f1=i-1, f3= i+1),file=Element)   
        else:
            print("    set Ks_col_ext{s}   [expr $n*6.0*$Es*$Icol_ext{s}{f2}mod/($HStoryTyp-$phvert{f}{s}-$phvert{f2}{f3})];	# rotational stiffness of Story {s} external column springs".format(s=i, f=i-1, f2=i+1, f3= i+2),file=Element)
            if NBay>1:
                print("    set Ks_col_int{s}   [expr $n*6.0*$Es*$Icol_int{s}{f2}mod/($HStoryTyp-$phvert{f}{s}-$phvert{f2}{f3})]; 	# rotational stiffness of Story {s} internal column springs".format(s=i, f=i-1, f2=i+1, f3= i+2),file=Element)

def IcolIbeamMod(NStory,NBay,Element):
    header="""# determine stiffness modifications to equate the stiffness of the spring-elastic element-spring subassembly to the stiffness of the actual frame member
    # References: (1) Ibarra, L. F., and Krawinkler, H. (2005). "Global collapse of frame structures under seismic excitations," Technical Report 152,
    #             		The John A. Blume Earthquake Engineering Research Center, Department of Civil Engineering, Stanford University, Stanford, CA.
    #			  (2) Zareian, F. and Medina, R. A. (2010). A practical method for proper modeling of structural damping in inelastic plane
    #					structural systems, Computers & Structures, Vol. 88, 1-2, pp. 45-53.
    # calculate modified section properties to account for spring stiffness being in series with the elastic element stiffness
    set n 10.0;		# stiffness multiplier for rotational spring

    # calculate modified moment of inertia for elastic elements between plastic hinge springs"""
    print(header,file=Element)
    
    for i in range(1,NStory,2):
        print("    set Icol_ext{f1}{f2}mod  [expr $Icol_ext{f1}{f2}*($n+1.0)/$n];	# modified moment of inertia for external columns in Story {f1},{f2}".format(f1=i, f2=i+1),file=Element)
        if NBay>1:
            print("    set Icol_int{f1}{f2}mod  [expr $Icol_int{f1}{f2}*($n+1.0)/$n];	# modified moment of inertia for internal columns in Story {f1},{f2}".format(f1=i, f2=i+1),file=Element)
        
    print("",file=Element)

    for i in range(1,NStory,2):
        Ibeam = "set Ibeam_{f1}{f2}mod [expr $Ibeam_{f1}{f2}*($n+1.0)/$n];	# modified moment of inertia for beams in Floor {f1}.{f2}".format(
            f1=i+1, f2=i+2
        )
        print("   ",Ibeam,file=Element)
    
def Ks_beam(NStory,Nbays,Element):
    header = "    #Ks_beam_y1y2z y1=floor y2floor z = bay"
    print(header,file=Element)
    if Nbays>1:
        for i in range(2,NStory+1,2):
            ksb="""set Ks_beam_int{f1}{f2} [expr $n*6.0*$Es*$Ibeam_{f1}{f2}mod/($WBay-$phlatext{f1}{f2}-$phlatint{f1}{f2})];		# rotational stiffness of Floor {f1},{f2} & beam springs of external column
        set Ks_beam_ext{f1}{f2} [expr $n*6.0*$Es*$Ibeam_{f1}{f2}mod/($WBay-$phlatext{f1}{f2}-$phlatint{f1}{f2})];		# rotational stiffness of Floor {f1},{f2} & beam springs internal column""".format(
                f1=i, f2=i+1
            )
            print("   ",ksb,file=Element)
    else:
        for i in range(2,NStory+1,2):
            ksb="set Ks_beam_ext{f1}{f2} [expr $n*6.0*$Es*$Ibeam_{f1}{f2}mod/($WBay-$phlatext{f1}{f2}-$phlatext{f1}{f2})];		# rotational stiffness of Floor {f1},{f2} & beam springs internal column""".format(
                f1=i, f2=i+1
            )
            print("   ",ksb,file=Element)        

def ColumnHingeNodes(NStory,NBay,Element):
    print("""\n# define extra nodes for plastic hinge rotational springs
	# nodeID convention:  "xya" where x = Pier #, y = Floor #, a = location relative to beam-column joint
	# "a" convention: 1,2 = left; 3,4 = right; (used for beams)
	# "a" convention: 5,6 = below; 7,8 = above; (used for columns)""",file=Element)
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
                            print(("    node {p}{s}0 $Pier{p} [expr $Floor{s} + $phvert{v1}{v2} + 0.5*$HStoryTyp];	#xy0, x=pier y=floor").format(p=pier,s=NStory,v1=vert,v2=vert+1),file=Element)
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
                if j==1 or j==Nbay+1:
                    elem = "    element elasticBeamColumn  1{p}{s}  {p}{s}7 {p}{s2}5 $Acol_ext{s}{s2} $Es $Icol_ext{s}{s2}mod $PDeltaTransf;	# Pier {p}".format(
                        p=j, s=i, s2=i+1, f=i-1
                    )
                    print(elem,file=Element)
                else:
                    elem = "    element elasticBeamColumn  1{p}{s}  {p}{s}7 {p}{s2}5 $Acol_int{s}{s2} $Es $Icol_int{s}{s2}mod $PDeltaTransf;	# Pier {p}".format(
                        p=j, s=i, s2=i+1, f=i-1
                    )
                    print(elem,file=Element)
        elif i==1 or i>1 and i%2==0:
            print(("    # Columns Story {s}".format(s=i)),file=Element)
            for j in range(1,Nbay+2):
                if j==1 or j==Nbay+1:
                    elem = "    element elasticBeamColumn  1{p}{s}  {p}{s}8 {p}{s2}5 $Acol_ext{f}{s} $Es $Icol_ext{f}{s}mod $PDeltaTransf;	# Pier {p}".format(
                        p=j, s=i, s2=i+1, f=i-1
                    )
                    print(elem,file=Element)
                else:
                    elem = "    element elasticBeamColumn  1{p}{s}  {p}{s}8 {p}{s2}5 $Acol_int{f}{s} $Es $Icol_int{f}{s}mod $PDeltaTransf;	# Pier {p}".format(
                        p=j, s=i, s2=i+1, f=i-1
                    )
                    print(elem,file=Element)
        else:
            print(("    # Columns Story {s} below node splice // xyza x=column y=pier z=story a=1,2 1=down 2=up".format(s=i)),file=Element)
            for j in range(1,Nbay+2):
                if j==1 or j==Nbay+1:
                    elem = "    element elasticBeamColumn  1{p}{s}1  {p}{s}8 {p}{s}0 $Acol_ext{f1}{f2} $Es $Icol_ext{f1}{f2}mod $PDeltaTransf;	# Pier {p}".format(
                        p=j, s=i, f1=i-2, f2=i-1
                    )
                    print(elem,file=Element)
                else:
                    elem = "    element elasticBeamColumn  1{p}{s}1  {p}{s}8 {p}{s}0 $Acol_int{f1}{f2} $Es $Icol_int{f1}{f2}mod $PDeltaTransf;	# Pier {p}".format(
                        p=j, s=i, f1=i-2, f2=i-1
                    )
                    print(elem,file=Element)
            print(("    # Columns Story {s} above node splice // xyza x=column y=pier z=story a=1,2 1=down 2=up".format(s=i)),file=Element)
            for j in range(1,Nbay+2):
                if j==1 or j==Nbay+1:
                    elem = "    element elasticBeamColumn  1{p}{s}2  {p}{s}0 {p}{s2}5 $Acol_ext{s}{s2} $Es $Icol_ext{s}{s2}mod $PDeltaTransf;	# Pier {p}".format(
                        p=j, s=i, s2=i+1
                    )
                    print(elem,file=Element)
                else:
                    elem = "    element elasticBeamColumn  1{p}{s}2  {p}{s}0 {p}{s2}5 $Acol_int{s}{s2} $Es $Icol_int{s}{s2}mod $PDeltaTransf;	# Pier {p}".format(
                        p=j, s=i, s2=i+1
                    )
                    print(elem,file=Element)


def beamHingeNodes(story,bay,Element):
    for floor in range(2,story+2):
        if floor%2==0:
            temp=floor
        else:
            temp=floor-1
        for pier in range(1,bay+2):
            if pier==1:
                beamhingeNode="""    # beam hinges at Floor {f}
    node {p}{f}1 [expr $Pier{p} + $phlatext{f1}{f2}] $Floor{f};
    node {p}{f}2 [expr $Pier{p} + $phlatext{f1}{f2}] $Floor{f};""".format(f=floor,p=pier,f1=temp,f2=temp+1)
                print(beamhingeNode,file=Element)
            elif pier==bay+1:
                beamhingeNode="""    node {p}{f}3 [expr $Pier{p} - $phlatext{f1}{f2}] $Floor{f};
    node {p}{f}4 [expr $Pier{p} - $phlatext{f1}{f2}] $Floor{f};""".format(f=floor,p=pier,f1=temp,f2=temp+1)
                print(beamhingeNode,file=Element)
                print("",file=Element)                 
            else:
                beamhingeNode="""    node {p}{f}3 [expr $Pier{p} - $phlatint{f1}{f2}] $Floor{f};
    node {p}{f}4 [expr $Pier{p} - $phlatint{f1}{f2}] $Floor{f};
    node {p}{f}1 [expr $Pier{p} + $phlatint{f1}{f2}] $Floor{f};
    node {p}{f}2 [expr $Pier{p} + $phlatint{f1}{f2}] $Floor{f};""".format(f=floor,p=pier,f1=temp,f2=temp+1)
                print(beamhingeNode,file=Element)


def panelZoneNodes(story,bay,Element):
    header="""# define extra nodes for panel zones
    # nodeID convention:  "xybc" where x = Pier #, y = Floor #, bc = location relative to beam-column joint
    # "bc" conventions: 01,02 = top left of joint; 
    # 					03,04 = top right of joint;
    # 					05    = middle right of joint; (vertical middle, horizontal right)
    # 					06,07 = btm right of joint;
    # 					08,09 = btm left of joint;
    # 					10    = middle left of joint; (vertical middle, horizontal left)
    # note: top center and btm center nodes were previously defined as xy7 and xy6, respectively, at Floor 2(center = horizonal center)"""
    print(header,file=Element)
    print("\n",file=Element)
    



    for floor in range(2,story+2):
        if floor%2==0:
            temp=floor
        else:
            temp=floor-1
        for pier in range(1,bay+2):
            if pier==1 or pier==bay+1:
                panelzoneNode="""# panel zone at Pier {p}, Floor {f}
    node {p}{f}01 [expr $Pier{p} - $pzlatext{f1}{f2} ] [expr $Floor{f} + $phvert{f1}{f2}];
    node {p}{f}02 [expr $Pier{p} - $pzlatext{f1}{f2} ] [expr $Floor{f} + $phvert{f1}{f2}];
    node {p}{f}03 [expr $Pier{p} + $pzlatext{f1}{f2} ] [expr $Floor{f} + $phvert{f1}{f2}];
    node {p}{f}04 [expr $Pier{p} + $pzlatext{f1}{f2} ] [expr $Floor{f} + $phvert{f1}{f2}];
    node {p}{f}05 [expr $Pier{p} + $pzlatext{f1}{f2} ] [expr $Floor{f}];
    node {p}{f}06 [expr $Pier{p} + $pzlatext{f1}{f2} ] [expr $Floor{f} - $phvert{f1}{f2}];
    node {p}{f}07 [expr $Pier{p} + $pzlatext{f1}{f2} ] [expr $Floor{f} - $phvert{f1}{f2}];
    node {p}{f}08 [expr $Pier{p} - $pzlatext{f1}{f2} ] [expr $Floor{f} - $phvert{f1}{f2}];
    node {p}{f}09 [expr $Pier{p} - $pzlatext{f1}{f2} ] [expr $Floor{f} - $phvert{f1}{f2}];
    node {p}{f}10 [expr $Pier{p} - $pzlatext{f1}{f2} ] [expr $Floor{f}];""".format(f=floor,p=pier,f1=temp,f2=temp+1)
                print(panelzoneNode,file=Element)
                if floor==story+1:
                    print(f"    node {pier}{floor}7  [expr $Pier{pier}]  [expr $Floor{floor} + $phvert{temp}{temp+1}]; # not previously defined since no column above",file=Element)
                print("",file=Element)
            else:
                panelzoneNode="""# panel zone at Pier {p}, Floor {f}
    node {p}{f}01 [expr $Pier{p} - $pzlatint{f1}{f2} ] [expr $Floor{f} + $phvert{f1}{f2}];
    node {p}{f}02 [expr $Pier{p} - $pzlatint{f1}{f2} ] [expr $Floor{f} + $phvert{f1}{f2}];
    node {p}{f}03 [expr $Pier{p} + $pzlatint{f1}{f2} ] [expr $Floor{f} + $phvert{f1}{f2}];
    node {p}{f}04 [expr $Pier{p} + $pzlatint{f1}{f2} ] [expr $Floor{f} + $phvert{f1}{f2}];
    node {p}{f}05 [expr $Pier{p} + $pzlatint{f1}{f2} ] [expr $Floor{f}];
    node {p}{f}06 [expr $Pier{p} + $pzlatint{f1}{f2} ] [expr $Floor{f} - $phvert{f1}{f2}];
    node {p}{f}07 [expr $Pier{p} + $pzlatint{f1}{f2} ] [expr $Floor{f} - $phvert{f1}{f2}];
    node {p}{f}08 [expr $Pier{p} - $pzlatint{f1}{f2} ] [expr $Floor{f} - $phvert{f1}{f2}];
    node {p}{f}09 [expr $Pier{p} - $pzlatint{f1}{f2} ] [expr $Floor{f} - $phvert{f1}{f2}];
    node {p}{f}10 [expr $Pier{p} - $pzlatint{f1}{f2} ] [expr $Floor{f}];""".format(f=floor,p=pier,f1=temp,f2=temp+1)
                print(panelzoneNode,file=Element)
                if floor==story+1:
                    print(f"    node {pier}{floor}7  [expr $Pier{pier}]  [expr $Floor{floor} + $phvert{temp}{temp+1}]; # not previously defined since no column above",file=Element)
                print("",file=Element)

def fileDetails(NStory,NBay,Element):
    print(("""# --------------------------------------------------------------------------------------------------
# Example: {s}-Story {b}-Bay Steel Moment Frame with Concentrated Plasticity
# Panel Zone Model with Concentrated Plastic Hinges at RBS Locations
# Created by:  Laura Eads, Stanford University, 2010
# Units: kips, inches, seconds

# Element ID conventions:
#	1xy    = frame columns with RBS springs at both ends
#	2xy    = frame beams with RBS springs at both ends
#	6xy    = trusses linking frame and P-delta column
#	7xy    = P-delta columns
#	2xya   = frame beams between panel zone and RBS spring
#	3xya   = frame column rotational springs
#	4xya   = frame beam rotational springs
#	5xya   = P-delta column rotational springs
#	4xy00  = panel zone rotational springs
#	500xya = panel zone elements
#	where:
#		x = Pier or Bay #
#		y = Floor or Story #
#		a = an integer describing the location relative to beam-column joint (see description where elements and nodes are defined)

###################################################################################################
#          Set Up & Source Definition									  
###################################################################################################
	wipe all;							# clear memory of past model definitions
	model BasicBuilder -ndm 2 -ndf 3;	# Define the model builder, ndm = #dimension, ndf = #dofs
	source DisplayModel2D.tcl;			# procedure for displaying a 2D perspective of model
	source DisplayPlane.tcl;			# procedure for displaying a plane in a model
	source rotSpring2DModIKModel.tcl;	# procedure for defining a rotational spring (zero-length element) for plastic hinges
	source rotLeaningCol.tcl;			# procedure for defining a rotational spring (zero-length element) with very small stiffness
	source rotPanelZone2D.tcl;			# procedure for defining a rotational spring (zero-length element) to capture panel zone shear distortions
	source elemPanelZone2D.tcl;			# procedure for defining 8 elements to create a rectangular panel zone
	
###################################################################################################
#          Define Analysis Type										  
###################################################################################################
# Define type of analysis:  "pushover" = pushover;  "dynamic" = dynamic
	set analysisType "pushover";
	
	if {l}$analysisType == "pushover"{r} {l}
		set dataDir Concentrated-PanelZone-Pushover-Output;	# name of output folder
		file mkdir $dataDir; 								# create output folder
	{r}
	if {l}$analysisType == "dynamic"{r} {l}
		set dataDir Concentrated-PanelZone-Dynamic-Output;	# name of output folder
		file mkdir $dataDir; 								# create output folder
	{r}
	""").format(s=NStory,b=NBay,l='{',r='}'),file=Element)

def CalculateNodalMass(NBay,FloorWeight,Element):
    print(f"""# calculate nodal masses -- lump floor masses at frame nodes
	set g 386.2;				# acceleration due to gravity
	set FloorWeight {FloorWeight};		# weight of all Floor  in kips
	set WBuilding  [expr $FloorWeight * $NStories]; # total building weight
	set NodalMass [expr ($FloorWeight/$g) / ({float(NBay+1)})];	# mass at each node on Floors
	set Negligible 1e-9;	# a very small number to avoid problems with zero""",file=Element)

def defineBeamColumnSection(NStory,NBay,columnSectionExt,columnSectionInt,beamSection,section,Element):
    print("""
###################################################################################################
#          Define Section Properties and Elements													  
###################################################################################################
# define material properties
	set Es 29000.0;			# steel Young's modulus
	set Fy 50.0;			# steel yield strength
    """,file=Element)
    for i in range(1,NStory+1,2):
        sec = columnSectionExt[i//2]
        print(f"# define column section {sec} for Story {i}&{i+1} for external column",file=Element)
        print(f"""	set Acol_ext{i}{i+1}  {section[sec]["Acol"]};		# cross-sectional area
	set Icol_ext{i}{i+1}  {section[sec]["Icol"]};		# moment of inertia
	set Mycol_ext{i}{i+1} {section[sec]["Mycol"]};	# yield moment at plastic hinge location (i.e., My of RBS section)
	set dcol_ext{i}{i+1} {section[sec]["dcol"]};		# depth
	set bfcol_ext{i}{i+1} {section[sec]["bfcol"]};		# flange width
	set tfcol_ext{i}{i+1} {section[sec]["tfcol"]};		# flange thickness
	set twcol_ext{i}{i+1} {section[sec]["twcol"]};		# web thickness
    """,file=Element)

    if NBay>1:
        for i in range(1,NStory+1,2):
            sec = columnSectionInt[i//2]
            print(f"# define column section {sec} for Story {i}&{i+1} for internal column",file=Element)
            print(f"""	set Acol_int{i}{i+1}  {section[sec]["Acol"]};		# cross-sectional area
        set Icol_int{i}{i+1}  {section[sec]["Icol"]};		# moment of inertia
        set Mycol_int{i}{i+1} {section[sec]["Mycol"]};	# yield moment at plastic hinge location (i.e., My of RBS section)
        set dcol_int{i}{i+1} {section[sec]["dcol"]};		# depth
        set bfcol_int{i}{i+1} {section[sec]["bfcol"]};		# flange width
        set tfcol_int{i}{i+1} {section[sec]["tfcol"]};		# flange thickness
        set twcol_int{i}{i+1} {section[sec]["twcol"]};		# web thickness
        """,file=Element)

    for i in range(2,NStory+2,2):
        sec = beamSection[i//2-1]
        print(f"# define beam section {sec} for Floor {i}&{i+1}",file=Element)
        print(f"""    set Abeam_{i}{i+1}  {section[sec]["Acol"]};		# cross-sectional area (full section properties)
	set Ibeam_{i}{i+1}  {section[sec]["Icol"]};	# moment of inertia  (full section properties)
	set Mybeam_{i}{i+1} {section[sec]["Mybeam"]};	# yield moment at plastic hinge location (i.e., My of RBS section)
	set dbeam_{i}{i+1} {section[sec]["dcol"]};		# depth
    """,file=Element)

def elasticBeamColumnElements(story,bay,Element):
    print("""\n# define elastic beam elements
    # element between plastic hinges: eleID convention = "2xy" where 2 = beam, x = Bay #, y = Floor #
    # element between plastic hinge and panel zone: eleID convention = "2xya" where 2 = beam, x = Bay #, y = Floor #, a = loc in bay
    #	"a" convention: 1 = left end of bay; 2 = right end of bay""",file=Element)
    print("\n",file=Element)    

    for floor in range(2,story+2):
        if floor%2==0:
            temp=floor
        else:
            temp=floor-1
        print("    # Beams story{s} or floor {f}".format(f=floor,s=floor-1),file=Element)
        for pier in range(1,bay+1):
            elasticBeamElement="""    element elasticBeamColumn  2{p}{f}1 {p}{f}05 {p}{f}1  $Abeam_{f1}{f2} $Es $Ibeam_{f1}{f2}    $PDeltaTransf;
    element elasticBeamColumn  2{p}{f}  {p}{f}2  {p1}{f}3  $Abeam_{f1}{f2} $Es $Ibeam_{f1}{f2}mod $PDeltaTransf;
    element elasticBeamColumn  2{p}{f}2 {p1}{f}4  {p1}{f}10 $Abeam_{f1}{f2} $Es $Ibeam_{f1}{f2}    $PDeltaTransf;""".format(p=pier,f=floor,s=floor-1,p1=pier+1,f1=temp,f2=temp+1)
            print(elasticBeamElement,file=Element)
            print("",file=Element)

def pdeltaElasticColumn(NStory,NBay,Element):
    header="""\n# p-delta columns
    #eleID convention:  7xy, 7 = p-delta columns, x = Pier #, y = Story #"""
    print(header,file=Element)
    print(f"    element elasticBeamColumn  7{NBay+2}1  {NBay+2}1	{NBay+2}26 $Arigid $Es $Irigid $PDeltaTransf;	# Story 1",file=Element)
    for floor in range(2,NStory+1):
        print(f"    element elasticBeamColumn  7{NBay+2}{floor}  {NBay+2}{floor}7	{NBay+2}{floor+1}6 $Arigid $Es $Irigid $PDeltaTransf;	# Story {floor}",file=Element)

def DefineProps(Element):
    print("""\n###################################################################################################
#          Define Rotational Springs for Plastic Hinges, Panel Zones, and Leaning Columns												  
###################################################################################################
# define rotational spring properties and create spring elements using "rotSpring2DModIKModel" procedure
	# rotSpring2DModIKModel creates a uniaxial material spring with a bilinear response based on Modified Ibarra Krawinkler Deterioration Model
	# references provided in rotSpring2DModIKModel.tcl
	# input values for Story 1 column springs
	set McMy 1.05;			# ratio of capping moment to yield moment, Mc / My
	set LS 1000.0;			# basic strength deterioration (a very large # = no cyclic deterioration)
	set LK 1000.0;			# unloading stiffness deterioration (a very large # = no cyclic deterioration)
	set LA 1000.0;			# accelerated reloading stiffness deterioration (a very large # = no cyclic deterioration)
	set LD 1000.0;			# post-capping strength deterioration (a very large # = no deterioration)
	set cS 1.0;				# exponent for basic strength deterioration (c = 1.0 for no deterioration)
	set cK 1.0;				# exponent for unloading stiffness deterioration (c = 1.0 for no deterioration)
	set cA 1.0;				# exponent for accelerated reloading stiffness deterioration (c = 1.0 for no deterioration)
	set cD 1.0;				# exponent for post-capping strength deterioration (c = 1.0 for no deterioration)
	set th_pP 0.025;		# plastic rot capacity for pos loading
	set th_pN 0.025;		# plastic rot capacity for neg loading
	set th_pcP 0.3;			# post-capping rot capacity for pos loading
	set th_pcN 0.3;			# post-capping rot capacity for neg loading
	set ResP 0.4;			# residual strength ratio for pos loading
	set ResN 0.4;			# residual strength ratio for neg loading
	set th_uP 0.4;			# ultimate rot capacity for pos loading
	set th_uN 0.4;			# ultimate rot capacity for neg loading
	set DP 1.0;				# rate of cyclic deterioration for pos loading
	set DN 1.0;				# rate of cyclic deterioration for neg loading""",file=Element)

def beamSprings(story,bay,Element):
    print("""   
# define beam springs
    # Spring ID: "4xya", where 4 = beam spring, x = Bay #, y = Floor #, a = location in bay
    # "a" convention: 1 = left end, 2 = right end
    # redefine the rotations since they are not the same
    set th_pP 0.02;
    set th_pN 0.02;
    set th_pcP 0.16;
    set th_pcN 0.16;""",file=Element)
    springarray=[]
    for floor in range(2,story+2):
        if floor%2==0:
            temp=floor
        else:
            temp=floor-1
        print("""    set a_mem1 [expr ($n+1.0)*($Mybeam_{f1}{f2}*($McMy-1.0)) / ($Ks_beam_ext{f1}{f2}*$th_pP)];	# strain hardening ratio of spring
    set b1 [expr ($a_mem1)/(1.0+$n*(1.0-$a_mem1))];								# modified strain hardening ratio of spring (Ibarra & Krawinkler 2005, note: there is mistake in Eqn B.5)""".format(f1=temp,f2=temp+1),file=Element)
        if bay>1:
            print("""    set a_mem2 [expr ($n+1.0)*($Mybeam_{f1}{f2}*($McMy-1.0)) / ($Ks_beam_int{f1}{f2}*$th_pP)];	# strain hardening ratio of spring
    set b2 [expr ($a_mem2)/(1.0+$n*(1.0-$a_mem2))];								# modified strain hardening ratio of spring (Ibarra & Krawinkler 2005, note: there is mistake in Eqn B.5)""".format(f1=temp,f2=temp+1),file=Element)
        print("",file=Element)
        print("    #beam springs at Floor {f}".format(f=floor),file=Element)
        for pier in range(1,bay+1):
            if pier==1 or pier==bay:
                position="ext"
            else:
                position="int"
            beamRotSpring="""    rotSpring2DModIKModel 4{p}{f}1 {p}{f}1 {p}{f}2 $Ks_beam_{pos}{f1}{f2} $b1 $b1 $Mybeam_{f1}{f2} [expr -$Mybeam_{f1}{f2}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;
    rotSpring2DModIKModel 4{p}{f}2 {p1}{f}3 {p1}{f}4 $Ks_beam_{pos}{f1}{f2} $b1 $b1 $Mybeam_{f1}{f2} [expr -$Mybeam_{f1}{f2}] $LS $LK $LA $LD $cS $cK $cA $cD $th_pP $th_pN $th_pcP $th_pcN $ResP $ResN $th_uP $th_uN $DP $DN;""".format(p=pier,f=floor,f1=temp,f2=temp+1,pos=position,p1=pier+1)
            springarray.append("4"+str(pier)+str(floor)+"1")
            springarray.append("4"+str(pier)+str(floor)+"2")
            print(beamRotSpring,file=Element)
        print("",file=Element)
    print("""    #create region for beam springs
    region 2 -ele""",end=" ",file=Element)
    for nodes in springarray:
        print(nodes,end=" ",file=Element)
    print(";",file=Element)

def pDeltaSprings(story,bay,Element):
    pDeltaar=[]
    print("""# define p-delta column spring: zero-stiffness elastic spring	
    #Spring ID: "5xya" where 5 = leaning column spring, x = Pier #, y = Story #, a = location in story
    # "a" convention: 1 = bottom of story, 2 = top of story
    # rotLeaningCol ElemID ndR ndC """,file=Element)
    print("    rotLeaningCol 5{p}12 {p}2 {p}26;	# top of Story 1".format(p=bay+2),file=Element)
    pDeltaar.append("5"+str(bay+2)+"12")
    for floor in range(2,story+1):
        spring="""    rotLeaningCol 5{p}{f1}1 {p}{f1} {p}{f1}7;	# bottom of Story {f1}
    rotLeaningCol 5{p}{f1}2 {p}{f2} {p}{f2}6;	# top of Story {f1}""".format(p=bay+2,f1=floor,f2=floor+1)
        pDeltaar.append("5"+str(bay+2)+str(floor)+"1")
        pDeltaar.append("5"+str(bay+2)+str(floor)+"2")
        print(spring,file=Element)
    print("",file=Element)
    print("""    # create region for P-Delta column springs
    region 3 -ele""",end=" ",file=Element)
    for nodes in pDeltaar:
            print(nodes,end=" ",file=Element)
    print(";",file=Element)

def definePanelZoneSpring(Nstory,Nbay,Element):
	print("""
#define panel zone springs
	# rotPanelZone2D creates a uniaxial material spring with a trilinear response based on the Krawinkler Model
	#				It also constrains the nodes in the corners of the panel zone.
	# references provided in rotPanelZone2D.tcl
	# note: the upper right corner nodes of the PZ must be imported
	source rotPanelZone2D.tcl
	set Ry 1.2; 	# expected yield strength multiplier
	set as_PZ 0.03; # strain hardening of panel zones
	# Spring ID: "4xy00" where 4 = panel zone spring, x = Pier #, y = Floor #
	""",file=Element)
	s=1
	for floor in range(2,Nstory+2):
		print(f"""	#Floor {floor} PZ springs
	#             ElemID  ndR  ndC  E   Fy   dc         bf_c           tf_c          tp        db       Ry   as""",file=Element)
		if floor>2 and floor%2==0:
			s+=2
		for pier in range(1,Nbay+2):
			if pier==1 or pier==Nbay+1:
				print(f"	rotPanelZone2D 4{pier}{floor}00 {pier}{floor}03 {pier}{floor}04 $Es $Fy $dcol_ext{s}{s+1} $bfcol_ext{s}{s+1} $tfcol_ext{s}{s+1} $twcol_ext{s}{s+1} $dbeam_{s+1}{s+2} $Ry $as_PZ;",file=Element)
			else:
				print(f"	rotPanelZone2D 4{pier}{floor}00 {pier}{floor}03 {pier}{floor}04 $Es $Fy $dcol_int{s}{s+1} $bfcol_int{s}{s+1} $tfcol_int{s}{s+1} $twcol_int{s}{s+1} $dbeam_{s+1}{s+2} $Ry $as_PZ;",file=Element)
		print("",file=Element)

def eigenValue(Element):
    print("""\n############################################################################
#                       Eigenvalue Analysis                    			   
############################################################################
	set pi [expr 2.0*asin(1.0)];						# Definition of pi
	set nEigenI 1;										# mode i = 1
	set nEigenJ 2;										# mode j = 2
	set lambdaN [eigen [expr $nEigenJ]];				# eigenvalue analysis for nEigenJ modes
	set lambdaI [lindex $lambdaN [expr $nEigenI-1]];	# eigenvalue mode i = 1
	set lambdaJ [lindex $lambdaN [expr $nEigenJ-1]];	# eigenvalue mode j = 2
	set w1 [expr pow($lambdaI,0.5)];					# w1 (1st mode circular frequency)
	set w2 [expr pow($lambdaJ,0.5)];					# w2 (2nd mode circular frequency)
	set T1 [expr 2.0*$pi/$w1];							# 1st mode period of the structure
	set T2 [expr 2.0*$pi/$w2];							# 2nd mode period of the structure
	puts "T1 = $T1 s";									# display the first mode period in the command window
	puts "T2 = $T2 s";									# display the second mode period in the command window
""",file=Element)

def GravityLoadLeaningColumn(NStory,NBay,WBay,FloorWeight,floorLength,floorWidth,Element):
    print("""\n############################################################################
#              Gravity Loads & Gravity Analysis
############################################################################
# apply gravity loads
    #command: pattern PatternType $PatternID TimeSeriesType
    pattern Plain 101 Constant {
            
        # point loads on leaning column nodes
        # command: load node Fx Fy Mz\n""",file=Element)
    flrWtprsqrins=(FloorWeight*2)/(floorLength*floorWidth*12*12)
    loadpier=flrWtprsqrins*WBay*WBay*12*12*0.5*(NBay+1)
    grvtyLoad=round((FloorWeight-loadpier),2)
    for floor in range(2,NStory+2):
        print(f"        set P_PD{floor} [expr -{grvtyLoad}];	# Floor {floor}",file=Element)
    print("",file=Element)
    for floor in range(2,NStory+2):
        print(f"        load 5{floor} 0.0 $P_PD{floor} 0.0;		# Floor {floor}",file=Element)

def pointLoadonFrame(NStory,NBay,Element):
    print("\n        # point loads on frame column nodes",file=Element)
    for floor in range(2,NStory+2):
        print(f"        set P_F{floor} [expr 0.25*(-1.0*$FloorWeight-$P_PD{floor})];	# load on each frame node in Floor {floor}",file=Element)
    for floor in range(2,NStory+2):
        print(f"\n        # Floor {floor} loads",file=Element)
        for pier in range(1,NBay+2):
            print(f"        load {pier}{floor}7 0.0 $P_F{floor} 0.0;",file=Element)
    print("}",file=Element)

def Gravityanalysis(Element):
    print("""# Gravity-analysis: load-controlled static analysis	
    set Tol 1.0e-6;							# convergence tolerance for test
	constraints Plain;						# how it handles boundary conditions
	numberer RCM;							# renumber dof's to minimize band-width (optimization)
	system BandGeneral;						# how to store and solve the system of equations in the analysis (large model: try UmfPack)
	test NormDispIncr $Tol 6;				# determine if convergence has been achieved at the end of an iteration step
	algorithm Newton;						# use Newton's solution algorithm: updates tangent stiffness at every iteration
	set NstepGravity 10;					# apply gravity in 10 steps
	set DGravity [expr 1.0/$NstepGravity];	# load increment
	integrator LoadControl $DGravity;		# determine the next time step for an analysis
	analysis Static;						# define type of analysis: static or transient
	analyze $NstepGravity;					# apply gravity

	# maintain constant gravity loads and reset time to zero
	loadConst -time 0.0
	puts "Model Built"
""",file=Element)

def recorders(NStory,NBay,Element):
    print("""############################################################################
#              Recorders					                			   
############################################################################
# record drift histories
    # record drifts
    recorder Drift -file $dataDir/Drift-Story1.out -time -iNode 11 -jNode 1205 -dof 1 -perpDirn 2;""",file=Element)
    for floor in range(2,NStory+2):
        if floor<NStory+1:
            print(f"    recorder Drift -file $dataDir/Drift-Story{floor}.out -time -iNode 1{floor}05 -jNode 1{floor+1}05 -dof 1 -perpDirn 2;",file=Element)
        else:
            print(f"    recorder Drift -file $dataDir/Drift-Roof.out -time -iNode 11 -jNode 1{floor}05 -dof 1 -perpDirn 2;",file=Element)
    print(f"""\n# record floor displacements	
    recorder Node -file $dataDir/Disp.out -time -node""",end=" ",file=Element)
    for floor in range(2,NStory+1):
        print(f"1{floor}05",end=" ",file=Element)
    print(f"1{NStory+1}05 -dof 1 disp; ",file=Element)
    print("""\n# record base shear reactions
    recorder Node -file $dataDir/Vbase.out -time -node""",end=" ",file=Element)
    for pier in range(1,NBay+2):
        print(f"{pier}17",end=" ",file=Element)
    print(f"{NBay+2}1 -dof 1 reaction;",file=Element)

    print("\n# record story 1 column forces in global coordinates ",file=Element)
    for pier in range(1,NBay+2):
        print(f"    recorder Element -file $dataDir/Fcol1{pier}1.out -time -ele 1{pier}1 force;",file=Element)
    print(f"    recorder Element -file $dataDir/Fcol7{NBay+2}1.out -time -ele 1{NBay+2}1 force;",file=Element)

    print("""	
# record response history of all frame column springs (one file for moment, one for rotation)
    recorder Element -file $dataDir/MRFcol-Mom-Hist.out -time -region 1 force;
    recorder Element -file $dataDir/MRFcol-Rot-Hist.out -time -region 1 deformation;
        
# record response history of all frame beam springs (one file for moment, one for rotation)
    recorder Element -file $dataDir/MRFbeam-Mom-Hist.out -time -region 2 force;
    recorder Element -file $dataDir/MRFbeam-Rot-Hist.out -time -region 2 deformation;

    """,file=Element)

def pushOver(NStory,NBay,lateralLoad,Element):
	print("""
#######################################################################################
#                                                                                     #
#                              Analysis Section			                              #
#                                                                                     #
#######################################################################################

############################################################################
#              Pushover Analysis                			   			   #
############################################################################
if {$analysisType == "pushover"} { 
	puts "Running Pushover..."
# assign lateral loads and create load pattern:  use ASCE 7-10 distribution """,file=Element)
	for floor in range(2,NStory+2):
		print(f"	set lat{floor} {lateralLoad[floor-2]};	# force on each beam-column joint in Floor {floor}",file=Element)
	print("",file=Element)
	print("	pattern Plain 200 Linear {",file=Element)
	for floor in range(2,NStory+2):
		for pier in range(1,NBay+2):
			print(f"					load {pier}{floor}05 $lat{floor} 0.0 0.0;",file=Element)
		print("",file=Element)
	print("	}",file=Element)
	print(f"""# display deformed shape:
	set ViewScale 5;
	DisplayModel2D DeformedShape $ViewScale ;	# display deformed shape, the scaling factor needs to be adjusted for each model

# displacement parameters
	set IDctrlNode 1{NStory+1}05;				# node where disp is read for disp control ///////// changed to 1305 to 1405
	set IDctrlDOF 1;					# degree of freedom read for disp control (1 = x displacement)
	set Dmax [expr 0.1*$HBuilding];		# maximum displacement of pushover: 10% roof drift
	set Dincr [expr 0.01];				# displacement increment

# analysis commands
	constraints Plain;					# how it handles boundary conditions
	numberer RCM;						# renumber dof's to minimize band-width (optimization)
	system BandGeneral;					# how to store and solve the system of equations in the analysis (large model: try UmfPack)
	test NormUnbalance 1.0e-5 400;		# type of convergence criteria with tolerance, max iterations
	algorithm Newton;					# use Newton's solution algorithm: updates tangent stiffness at every iteration
	integrator DisplacementControl  $IDctrlNode   $IDctrlDOF $Dincr;	# use displacement-controlled analysis
	analysis Static;					# define type of analysis: static for pushover
	set Nsteps [expr int($Dmax/$Dincr)];# number of pushover analysis steps
	set ok [analyze $Nsteps];			# this will return zero if no convergence problems were encountered
	puts "Pushover complete";			# display this message in the command window
}} 	""",file=Element)

def timeHistory(Element):
    print("""	
############################################################################
#   Time History/Dynamic Analysis               			   			   #
############################################################################	
if {$analysisType == "dynamic"} { 
	puts "Running dynamic analysis..."
		# display deformed shape:
		set ViewScale 5;	# amplify display of deformed shape
		DisplayModel2D DeformedShape $ViewScale;	# display deformed shape, the scaling factor needs to be adjusted for each model
	
	# Rayleigh Damping
		# calculate damping parameters
		set zeta 0.02;		# percentage of critical damping
		set a0 [expr $zeta*2.0*$w1*$w2/($w1 + $w2)];	# mass damping coefficient based on first and second modes
		set a1 [expr $zeta*2.0/($w1 + $w2)];			# stiffness damping coefficient based on first and second modes
		set a1_mod [expr $a1*(1.0+$n)/$n];				# modified stiffness damping coefficient used for n modified elements. See Zareian & Medina 2010.
		
		# assign damping to frame beams and columns		
		# command: region $regionID -eleRange $elementIDfirst $elementIDlast rayleigh $alpha_mass $alpha_currentStiff $alpha_initialStiff $alpha_committedStiff
		region 4 -eleRange 111 239 rayleigh 0.0 0.0 $a1_mod 0.0;	# assign stiffness proportional damping to frame beams & columns w/ n modifications
		region 5 -eleRange 2121 2392 rayleigh 0.0 0.0 $a1 0.0;		# assign stiffness proportional damping to frame beams & columns w/out n modifications
		#region 6 -eleRange 500000 599999 rayleigh 0.0 0.0 $a1 0.0;	# assign stiffness proportional damping to panel zone elements
		rayleigh $a0 0.0 0.0 0.0;              						# assign mass proportional damping to structure (only assigns to nodes with mass)
		
	# define ground motion parameters
		set patternID 1;				# load pattern ID
		set GMdirection 1;				# ground motion direction (1 = x)
		set GMfile "NR94cnp.tcl";		# ground motion filename
		set dt 0.01;					# timestep of input GM file
		set Scalefact 1.0;				# ground motion scaling factor
		set TotalNumberOfSteps 2495;	# number of steps in ground motion
		set GMtime [expr $dt*$TotalNumberOfSteps + 10.0];	# total time of ground motion + 10 sec of free vibration
		
	# define the acceleration series for the ground motion
		# syntax:  "Series -dt $timestep_of_record -filePath $filename_with_acc_history -factor $scale_record_by_this_amount
		set accelSeries "Series -dt $dt -filePath $GMfile -factor [expr $Scalefact*$g]";
		
	# create load pattern: apply acceleration to all fixed nodes with UniformExcitation
		# command: pattern UniformExcitation $patternID $GMdir -accel $timeSeriesID 
		pattern UniformExcitation $patternID $GMdirection -accel $accelSeries;
		
	# define dynamic analysis parameters
		set dt_analysis 0.001;			# timestep of analysis
		wipeAnalysis;					# destroy all components of the Analysis object, i.e. any objects created with system, numberer, constraints, integrator, algorithm, and analysis commands
		constraints Plain;				# how it handles boundary conditions
		numberer RCM;					# renumber dof's to minimize band-width (optimization)
		system UmfPack;					# how to store and solve the system of equations in the analysis
		test NormDispIncr 1.0e-8 10;	# type of convergence criteria with tolerance, max iterations
		algorithm Newton;				# use Newton's solution algorithm: updates tangent stiffness at every iteration
		integrator Newmark 0.5 0.25;	# uses Newmark's average acceleration method to compute the time history
		analysis Transient;				# type of analysis: transient or static
		set NumSteps [expr round(($GMtime + 0.0)/$dt_analysis)];	# number of steps in analysis
		
	# perform the dynamic analysis and display whether analysis was successful	
		set ok [analyze $NumSteps $dt_analysis];	# ok = 0 if analysis was completed
		if {$ok == 0} {
			puts "Dynamic analysis complete";
		} else {
			puts "Dynamic analysis did not converge";
		}		
		
	# output time at end of analysis	
		set currentTime [getTime];	# get current analysis time	(after dynamic analysis)
		puts "The current time is: $currentTime";
		wipe all;
}
	
wipe all;""",file=Element)


def SectionDetailsAdder(section,inputDetails):
    for sec in inputDetails:
        if sec not in section:
            data={}
            print(sec," Details not in database \nPlease add following to Database")
            for elements in section["W24x146"]:
                data[elements]=float(input(str(elements)+" :"))
            print('## Entered Values Are ###')
            for i in data:
                print(i," : ",data[i])
            fix=(input("Enter yes to confirm the updation of database else enter no :"))
            fix.lower()
            while(True):
                if fix=='yes':
                    f = open('Section.json','w')
                    section[sec]=data
                    json.dump(section,f)
                    print("Database is Updated :) ")
                    f.close()
                    break
                elif fix=="no":
                    print("Sorry Enter Once more :(")
                    break
                else:
                    fix=input("Wrong Command, Enter Yes or No")
                    fix.lower()
            SectionDetailsAdder(section,inputDetails) 