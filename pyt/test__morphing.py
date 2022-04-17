import os, sys
import numpy as np

# ========================================================= #
# ===  morphing__test.py                                === #
# ========================================================= #

def morphing__test():

    x_, y_, z_ = 0, 1, 2
    radius     = 1.050

    # ------------------------------------------------- #
    # --- [1] load mesh from MeshIO                 --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.load__meshio as lms
    mshFile    = "msh/model.msh"
    meshdict   = lms.load__meshio( mshFile=mshFile, elementType="tetra", returnType="dict" )
    nodes      = meshdict["points"]
    elems      = meshdict["cells"]
    physNums   = meshdict["physNums"]

    # ------------------------------------------------- #
    # --- [2] inquire sharing Nodes                 --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.inquire__sharingNodes as isn
    shareNodes = isn.inquire__sharingNodes  ( nodes=nodes, elems=elems, physNums=physNums )
    
    # ------------------------------------------------- #
    # --- [3] inquire nodes in physNums             --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.inquire__nodesInPhysNum as inp
    physNodes  = inp.inquire__nodesInPhysNum( nodes=nodes, elems=elems, physNums=physNums )

    # ------------------------------------------------- #
    # --- [4] prepare train nodes                   --- #
    # ------------------------------------------------- #
    radii      = np.sqrt( nodes[:,x_]**2 + nodes[:,y_]**2 )
    index_bot  = np.where( ( nodes[:,z_] == 0.0 ) & ( radii <= radius ) )
    index_mid  = list( shareNodes["301"]["302"] )
    index_top  = list( shareNodes["302"]["303"] )
    nodes_bot  = nodes[index_bot]
    nodes_mid  = nodes[index_mid]
    nodes_top  = nodes[index_top]

    # ------------------------------------------------- #
    # --- [5] interpolate mshape onto nodes_mid     --- #
    # ------------------------------------------------- #
    import nkUtilities.load__pointFile as lpf
    inpFile    = "dat/circle.dat"
    circpt     = lpf.load__pointFile( inpFile=inpFile, returnType="point" )
    
    import nkUtilities.load__pointFile as lpf
    inpFile    = "dat/mshape_svd.dat"
    mshape     = lpf.load__pointFile( inpFile=inpFile, returnType="structured" )
    gridData   = np.reshape( mshape[:,:,:,x_:z_+1], (mshape.shape[1],mshape.shape[2],3) )
    pointData  = np.copy( circpt )

    nodes_bot  = np.copy( circpt )
    nodes_top  = np.copy( circpt )
    nodes_mid  = np.copy( circpt )
    nodes_bot[:,z_] = 0.0
    nodes_mid[:,z_] = 0.2
    nodes_top[:,z_] = 0.3
    
    import nkInterpolator.interpolate__grid2point as g2p
    nodes_mod  = g2p.interpolate__grid2point( gridData=gridData, pointData=pointData )

    import nkVTKRoutines.convert__vtkPolySurface as cps
    cps.convert__vtkPolySurface( Data=nodes_top, outFile="png/out_top.vtp" )
    cps.convert__vtkPolySurface( Data=nodes_bot, outFile="png/out_bot.vtp" )
    cps.convert__vtkPolySurface( Data=nodes_mid, outFile="png/out_mid.vtp" )
    cps.convert__vtkPolySurface( Data=nodes_mod, outFile="png/out_mod.vtp" )
    
    # ------------------------------------------------- #
    # --- [6] boundaries making                     --- #
    # ------------------------------------------------- #
    boundary301     = np.concatenate( [nodes_bot,nodes_mid], axis=0 )
    boundary302     = np.concatenate( [nodes_mid,nodes_top], axis=0 )
    boundary301_mod = np.concatenate( [nodes_bot,nodes_mod], axis=0 )
    boundary302_mod = np.concatenate( [nodes_mod,nodes_top], axis=0 )
    displacement301 = boundary301_mod - boundary301
    displacement302 = boundary302_mod - boundary302

    nodes301        = np.copy( nodes[ list( physNodes["301"] ) ] )
    nodes302        = np.copy( nodes[ list( physNodes["302"] ) ] )
    import nkMeshRoutines.morph__rbf as rbf
    result301       = rbf.morph__rbf( boundaries=boundary301, displacement=displacement301, \
                                      nodes = nodes301, coef=0.100 )
    result302       = rbf.morph__rbf( boundaries=boundary302, displacement=displacement302, \
                                      nodes = nodes302, coef=0.100 )
    nodes[ list( physNodes["301"] ) ] = result301
    nodes[ list( physNodes["302"] ) ] = result302

    # ------------------------------------------------- #
    # --- [7] save as a bdf File                    --- #
    # ------------------------------------------------- #
    import nkMeshRoutines.save__nastranFile as snf
    snf.save__nastranFile( points=nodes, cells=elems, matNums=physNums, \
                           outFile="msh/modified.bdf" )
    
    return()


# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):
    morphing__test()

    
