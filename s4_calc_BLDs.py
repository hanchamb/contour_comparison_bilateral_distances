import numpy as np
import open3d as o3d
from scipy.spatial import KDTree
import os
import pandas as pd

##### CLASS DEFINITIONS 
# class to definte the contours with mesh and name
class Contour:
    """
    A class to store a mesh and associated name
    ...

    Attributes
    ----------
    mesh : TriangulatedMesh (from .ply file)
        triangulated mesh representing the contour (generated from Open3D, read from .ply file)
    name : str
        name of the mesh, (here, the filename without the extension)

    Methods
    -------
    None
    """
    def __init__(self, mesh, name):
        self.mesh = mesh;
        self.name = name;

##### FUNCTION DEFINITIONS 
#function to return the bidirectional distance at a point
def bidir_distances(pt_bidir_df_dir, contour_a, contour_b):
    """
    bidir_distances : Calculates the bidirectional local distance (https://aapm.onlinelibrary.wiley.com/doi/full/10.1118/1.4754802) between two contours. 
    1) Calculates the nearest neighbour distance between contour_a and contour_b using KDTrees queries from scipy.spatial. Exports the coordinates of nearest neighbours and and the distances between them both on contour_a and contour_b to CSV files to check the outputs. 
    2) For each point on the reference contour (contour_a), calculates the bidrectional local distance.  For a vertex_i on contour_a, if there is a vertex_x on contour_b which has vertex_i as its nearest neighbout, and it is further away than the current nearest neighbour to vertex_i, overwrite the nearest neighbout of vertex_i to this new vertex, vertex_x. This defines the bidirectional local distance. 
    3) Writes the bidirectional local distances to a CSV file (for checking outputs) and a .pkl file (for use in later steps)


    Parameters
    ----------
    pt_bidir_df_dir : filepath
        Directory to store the bilateral local distance files for each patient
    contour_a : Contour object
        Reference contour (here, the STAPLE contour). A Contour object, which stores the triangulated mesh of the contour and the contour name
    contour_b : Contour object
        Comparison contour (i.e. the left, manual contour, generated by observer 5). A Contour object, which stores the triangulated mesh of the contour and the contour name
    
    Returns
    -------
    None
    """
    
    ### https://aapm.onlinelibrary.wiley.com/doi/full/10.1118/1.4754802
    # will return the maximum distance at each vert of mesh a
    
    column_a_X = 'reference_X'
    column_a_Y = 'reference_Y'
    column_a_Z = 'reference_Z'
    column_a_index = 'reference_index'
    column_b_X = 'comparison_X'
    column_b_Y = 'comparison_Y'
    column_b_Z = 'comparison_Z'
    column_c_i= 'distance from reference'
    column_c_ii = 'distance from comparison'
    original_index = 'original_index_on_reference'
    bidir_dis_on_a = 'bidir_distance_on_reference' # initially a copy of column_c_i, then overwritten in bidir step if needed. 

    verts_a = np.asarray(contour_a.mesh.vertices)
    verts_b = np.asarray(contour_b.mesh.vertices)

    ### Calculate the nearest neighbours for all vertices on contour_a to-and-from contour_b
    # Creates the look up tree for easy searching
    lookup_tree_a = KDTree(verts_a)
    lookup_tree_b = KDTree(verts_b)
    # query lookup_tree_b for distances to verts_a, and the indices on mesh B which connects those points    
    dists_a, targets_on_b_index = lookup_tree_b.query(verts_a)
    # query lookup_tree_a for distances to verts_b, and the indices on mesh A which connects those points 
    dists_b, targets_on_a_index = lookup_tree_a.query(verts_b)

    # write a_to_b dataframe
    df_a_to_b = pd.DataFrame(columns=[column_a_X, column_a_Y, column_a_Z, 
                                      column_b_X, column_b_Y, column_b_Z, 
                                      column_c_i, original_index, bidir_dis_on_a])
    for i in range(0, len(verts_a)):
        # verts_a is a list of arrays with three components (i.e. verts_a[row][0] == x coordinate)
        # to get the corrdinate of the connected point from reference (i.e. the vertex on b), find the index value on verts_b (targets_on_b_index[i]) then find the coordinates on lookup_tree_b.data corresponding to that index
        # original_index is used in the bidirectional calculation in order to compare the two distances
        new_row = {column_a_X : verts_a[i][0], 
                   column_a_Y : verts_a[i][1], 
                   column_a_Z : verts_a[i][2], 
                   column_b_X : lookup_tree_b.data[targets_on_b_index[i]][0], 
                   column_b_Y : lookup_tree_b.data[targets_on_b_index[i]][1], 
                   column_b_Z : lookup_tree_b.data[targets_on_b_index[i]][2], 
                   column_c_i : dists_a[i], 
                   original_index: i, 
                   bidir_dis_on_a: dists_a[i]}
        df_a_to_b = df_a_to_b.append(new_row, ignore_index=True)

    # write b_to_a dataframe
    df_b_to_a = pd.DataFrame(columns=[column_b_X, column_b_Y, column_b_Z, column_a_X, column_a_Y, column_a_Z, column_a_index, column_c_ii])
    for i in range(0, len(verts_b)):
        
        new_row = {column_b_X : verts_b[i][0], 
                   column_b_Y  : verts_b[i][1], 
                   column_b_Z  : verts_b[i][2], 
                   column_a_X : lookup_tree_a.data[targets_on_a_index[i]][0], 
                   column_a_Y : lookup_tree_a.data[targets_on_a_index[i]][1], 
                   column_a_Z : lookup_tree_a.data[targets_on_a_index[i]][2], 
                   column_a_index: targets_on_a_index[i], 
                   column_c_ii : dists_b[i]}
        df_b_to_a = df_b_to_a.append(new_row, ignore_index=True)

    ##### BIDIRECTIONAL DISTANCES CALCULATION 
    # find the column numbers for use in iloc 
    bidir_col_no = df_a_to_b.columns.get_loc(bidir_dis_on_a)
    c_i_col_no = df_a_to_b.columns.get_loc(column_c_i)
    c_ii_col_no = df_b_to_a.columns.get_loc(column_c_ii)

    # create bidir column, i.e. the max distance between the two distance arrays from both files, by overwriting bidir_dis_on_a (originally just the ref_to_b distances)
    for target_idx, targ in enumerate(df_b_to_a[column_a_index]):
        target = int(targ)
        # match to corresponding point on mesh a
        # check if target distance greater than distance of current resident on this vert on mesh a
        if df_a_to_b.iloc[target, c_i_col_no] < df_b_to_a.iloc[target_idx, c_ii_col_no]:
            # replace if its less (i.e save the bigger value, the max distance)
            df_a_to_b.iloc[target, bidir_col_no] = df_b_to_a.iloc[target_idx, c_ii_col_no]
    
    ### WRITING BLD OUTPUTS TO FILES 
    # write full data frames as .csv files for checking the output of this step
    csv_path =  os.path.join(pt_bidir_df_dir, "full_BLD_dataframes")
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
    # a to b
    print("Writing distances dataframe to file; " + contour_a.name +"_to_" + contour_b.name)
    a_to_b_fname = f"{contour_a.name}_to_{contour_b.name}"
    df_a_to_b.to_csv(os.path.join(csv_path, f"{a_to_b_fname}.csv"))
    # b to a
    print("Writing distances dataframe to file; " + contour_b.name +"_to_" + contour_a.name)
    b_to_a_fname = f"{contour_b.name}_to_{contour_a.name}"
    df_b_to_a.to_csv(os.path.join(csv_path, f"{b_to_a_fname}.csv"))
    
    # slimmed down output (just the BLDs on the reference contour, no data for the points on contour b) 
    temp = df_a_to_b[["reference_X", "reference_Y", "reference_Z", "bidir_distance_on_reference"]]
    # save the slimmed down pkl files
    slimmed_path = os.path.join(pt_bidir_df_dir, "just_BLD_DFs") 
    if not os.path.exists(slimmed_path):
        os.makedirs(slimmed_path)
    temp.to_pickle(os.path.join(slimmed_path, f"{a_to_b_fname}.pkl"))

    # save the slimmed_down CSVs to another folder
    slimmed_csv_path = os.path.join(slimmed_path, "just_BLD_DFs_CSVs")
    if not os.path.exists(slimmed_csv_path):
        os.makedirs(slimmed_csv_path)
    temp.to_csv(os.path.join(slimmed_csv_path, f"{a_to_b_fname}.csv"))

def s4_main(mesh_base_dir, bld_dfs_dir, patient_IDs, observers, sides, contours, organ_name = "breast"):
    """
    Step 4 main function: Calculates bilateral distances between reference contour and every observer contour considered. 


    Parameters
    ----------
    mesh_base_dir : filepath
        The filepath which is the base directory for all the patient directories which store patients' mesh files.    
    bld_dfs_dir : filepath
        The filepath which is the base directory for all the patient directories which store the bilateral distance files, created in this step.
    patient_IDs : array of str
        The patient numbers, which are also the directory names for the directories in nifti_base_dir
    observers : array of str
        Array of strings which idicate the observer which generated the organ contour. Included in the naming of the region of interest contour in you treatment planning system, thus included in the naming of the nifti file sed to generate the STAPLE contour.      
    sides: array of str
        The laterality of the organ contour (here used to loop over left and right breast nifti files). Used to select the contours to be included in the STAPLE algorithm, i.e. only uses left contours to create the left breast STAPLE contour.
    contours : array of str
        The type of the organ contour. Example used here is "manual" contours and "altas-edited" contours, as we are do inter observer and inter-method analysis simultaneously. Used to select the contours to be included in the STAPLE algorithm, i.e. only uses "manual" contours to create the "manual breast STAPLE contour").
    organ_name : str
        The organ name which is featured in the name of the region of interest's nifti file.
    
 
    Returns
    -------
    None
    """
    # loop over patients' mesh files 
    for patient in patient_IDs: 
        print("           Working with patient " + str(patient))
        mesh_pt_dir = os.path.join(mesh_base_dir, patient)
        if not os.path.exists(mesh_pt_dir):
            os.mkdir(mesh_pt_dir)
        os.chdir(mesh_pt_dir)
        
        # arrays to stores meshes in "pairs" (see zip in line 215), ready for looping
        comparison_contour_array = []
        ref_contour_array = []    
        
        ###### LOAD IN MESHES 
        for side in sides:
            for contour in contours:
                #staple mesh
                staple_mesh = Contour(o3d.io.read_triangle_mesh(f"{side}_{organ_name}_{contour}_staple.ply")  , f"{side}_{contour}_staple")
                ref_contour_array.append(staple_mesh)

                #comparison contours
                comparison_contours = []
                for n in range(0,len(observers)):
                    comparison_contours.append(Contour(o3d.io.read_triangle_mesh(f"{side}_{contour}_{n+1}.ply"), f"{side}_{contour}_{n+1}"))
                comparison_contour_array.append(comparison_contours)
        
        # make folder to store BLD df for this patient 
        pt_bidir_df_dir = os.path.join(bld_dfs_dir, patient)
        if not os.path.exists(pt_bidir_df_dir):
            os.makedirs(pt_bidir_df_dir)
        os.chdir(pt_bidir_df_dir)

        # call function which calculates bidirectional distances     
        for comparison_contours, ref_contour in zip(comparison_contour_array, ref_contour_array):
            # loop over the multiple observer contours stored in comparison_contours ( the comparision contours to the 1 reference contour (here, the STAPLE contour))
            for mesh_test in comparison_contours:
                print(ref_contour.name, ' vs ', mesh_test.name )
                #call function which generates bidir distance files
                bidir_distances(pt_bidir_df_dir, contour_a = ref_contour, contour_b = mesh_test)
    
    print("Completed step 4: calculate BLDs. ")