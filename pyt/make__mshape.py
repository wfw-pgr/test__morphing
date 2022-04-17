import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  make__mshape.py                                  === #
# ========================================================= #

def make__mshape():

    x_, y_, z_ = 0, 1, 2
    radius     = 1.050
    LI,LJ,LK   = 161,161,1

    # ------------------------------------------------- #
    # --- [1] make coordinate                       --- #
    # ------------------------------------------------- #
    import nkUtilities.equiSpaceGrid as esg
    x1MinMaxNum   = [ -radius, radius, LI ]
    x2MinMaxNum   = [ -radius, radius, LJ ]
    x3MinMaxNum   = [     0.0,    0.0, LK ]
    coord         = esg.equiSpaceGrid( x1MinMaxNum=x1MinMaxNum, x2MinMaxNum=x2MinMaxNum, \
                                       x3MinMaxNum=x3MinMaxNum, returnType = "point" )
    radii         = np.sqrt( coord[:,x_]**2 + coord[:,y_]**2 )
    coord[:,z_]   = 0.150 + 0.10 * ( 1.0 - ( radii / radius )**2 )
    coord         = np.reshape( coord, (LK,LJ,LI,3) )
    isfv          = np.zeros( (LK,LJ,LI,5) )
    Data          = np.concatenate( [coord,isfv], axis=3 )

    # ------------------------------------------------- #
    # --- [2]  save in a file                       --- #
    # ------------------------------------------------- #
    import nkUtilities.save__pointFile as spf
    outFile   = "dat/mshape_svd.dat"
    spf.save__pointFile( outFile=outFile, Data=Data )

    return()




# ========================================================= #
# ===  make__circleShape.py                             === #
# ========================================================= #

def make__circleShape( radius=1.0 ):
    
    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.option.setNumber( "Mesh.Algorithm"  , 5 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 4 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "model" )
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    xc,yc,zc = 0, 0, 0
    rx,ry    = radius, radius
    zAxis    = [0,0,1]
    gmsh.model.occ.addDisk( xc,yc,zc, rx,ry )
    
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.050 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.050 )

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.write( "msh/circle.msh" )
    gmsh.finalize()
    
    # ------------------------------------------------- #
    # --- [5] load mesh and resave as pointFile     --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.load__meshio as lms
    mshFile  = "msh/circle.msh"
    meshdict = lms.load__meshio( mshFile=mshFile, elementType="tetra", returnType="dict" )
    nodes    = meshdict["points"]
    import nkUtilities.save__pointFile as spf
    outFile   = "dat/circle.dat"
    spf.save__pointFile( outFile=outFile, Data=nodes )


    


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #
if ( __name__=="__main__" ):
    make__circleShape()
    make__mshape()
