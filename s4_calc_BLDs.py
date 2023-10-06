import numpy as np
import open3d as o3d
from scipy.spatial import KDTree
import os
import pandas as pd

##### CLASS DEFINITIONS 
# class to definte the contours with mesh and name
class Contour:
    def __init__(self, mesh, name):
        self.mesh = mesh;
        self.name = name;

##### FUNCTION DEFINITIONS 
#function to return the bidirectional distance at a point
def bidir_distances(pt_bidir_df_dir, contour_a, contour_b):
    ### https://aapm.onlinelibrary.wiley.com/doi/full/10.1118/1.4754802
    # basic implementation, will return the maximum distance at each vert of mesh a
    
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

    ### Calculate the nearest neighbours for all vertices on mesh_from on mesh_to
    # Creates the look up tree for easy searching
    lookup_tree_a = KDTree(verts_a)
    lookup_tree_b = KDTree(verts_b)
    # query KDTree_b for distances to verts_a     
    dists_a, targets_on_b_index = lookup_tree_b.query(verts_a)
    # query KDTree_A for distances to verts_B AND the index on mesh A which connects those points 
    dists_b, targets_on_a_index = lookup_tree_a.query(verts_b)

    # write a_to_b dataframe
    df_a_to_b = pd.DataFrame(columns=[column_a_X, column_a_Y, column_a_Z, 
                                      column_b_X, column_b_Y, column_b_Z, 
                                      column_c_i, original_index, bidir_dis_on_a])
    for i in range(0, len(verts_a)):
        # verts_a is a list of arrays with three components (i.e. verts_a[row][0] == x coordinate)
        # to get the corrdinate of the connected point from reference (i.e. the point on b), find the index value on verts_b (targets_on_b_index[i]) then find the coordinates on lookup_tree_b.data corresponding to that index
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
    # can written to csv for checks that the bidir code is doing what it is supposed to


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
    

    ###### WRITING BIDIR DISTANCES DATAFRAME TO FILE 
    print("Writing distances dataframe to file; " + contour_a.name +"_to_" + contour_b.name)
    a_to_b_fname = f"{contour_a.name}_to_{contour_b.name}"
    
    ### write full data frames as .csv files
    csv_path =  os.path.join(pt_bidir_df_dir, "full_BLD_dataframes")
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
    df_a_to_b.to_csv(os.path.join(csv_path, f"{a_to_b_fname}.csv"))
    


    # slimmed down output (just the BLDs on the reference contour, no data for the points on contour b) 
    temp = df_a_to_b[["reference_X", "reference_Y", "reference_Z", "bidir_distance_on_reference"]]

    # save the slimmed down pkl files in the folder directly 
    slimmed_path = os.path.join(pt_bidir_df_dir, "just_BLD_DFs") 
    if not os.path.exists(slimmed_path):
        os.makedirs(slimmed_path)
    temp.to_pickle(os.path.join(slimmed_path, f"{a_to_b_fname}.pkl"))

    # save the CSVs to another folder
    slimmed_csv_path = os.path.join(slimmed_path, "just_BLD_DFs_CSVs")
    if not os.path.exists(slimmed_csv_path):
        os.makedirs(slimmed_csv_path)
    temp.to_csv(os.path.join(slimmed_csv_path, f"{a_to_b_fname}.csv"))

def s4_main(mesh_base_dir, bld_dfs_dir, patient_IDs, observers, sides, contours, organ_name = "breast"):

    for patient in patient_IDs: 
        print("           Working with patient " + str(patient))
        mesh_pt_dir = os.path.join(mesh_base_dir, patient)
        if not os.path.exists(mesh_pt_dir):
            os.mkdir(mesh_pt_dir)
        os.chdir(mesh_pt_dir)
        
        # arrays to stores meshes in "pairs", ready for looping
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
        
        # make folder to store BLD df for patient 
        pt_bidir_df_dir = os.path.join(bld_dfs_dir, patient)
        if not os.path.exists(pt_bidir_df_dir):
            os.makedirs(pt_bidir_df_dir)
        os.chdir(pt_bidir_df_dir)

        # call function which calculates bidirectional distances     
        for comparison_contours, ref_contour in zip(comparison_contour_array, ref_contour_array):
            for mesh_test in comparison_contours:
                print(ref_contour.name, ' vs ', mesh_test.name )
                #call function which generates bidir distance files
                bidir_distances(pt_bidir_df_dir, contour_a = ref_contour, contour_b = mesh_test)
    
    print("Completed step 4: calculate BLDs. ")
