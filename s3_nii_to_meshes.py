import numpy as np
import skimage.measure
import SimpleITK as sitk
import open3d as o3d
import os
from scipy import ndimage

# FUNCTION DEFINITIONS 

def load_n_mesh(fname):
    # load data
    nii = sitk.ReadImage(fname)
    direction_matrix = nii.GetDirection();# --> covariance matic, orientation of the image, same for all masks
    spacing = np.array(nii.GetSpacing())

    # convert to numpy array (mask)
    mask = sitk.GetArrayFromImage(nii)
    mask = np.flip(mask, axis=2) # for LR flip 
    
    # switch axes order from (ap,lr,cc) to (cc,ap,lr) (done in conversion to np array)
    spacing = spacing[[2,0,1]]
    # using marching cubes to get the triangulated surface
    verts, faces, normals, _ = skimage.measure.marching_cubes(volume=mask, level=0.5, spacing=spacing)

    # use Open3D to create 3D model
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(verts)
    mesh.triangles = o3d.utility.Vector3iVector(faces)
    mesh.vertex_normals = o3d.utility.Vector3dVector(normals)

    return mesh, mask

# smoothing taubin function
def smooth_n_simplify(mesh):
    #mesh = mesh.filter_smooth_taubin(number_of_iterations=1)
    return mesh

class NiftiFile:
    def __init__(self, filepath, name):
        self.filepath = filepath;
        self.name = name;

def s3_main(nifti_base_dir, mesh_base_dir, patient_IDs, observers, sides, contour_names, organ_name = "breast"):

    for patient in patient_IDs: 
        print("           Working with patient " + str(patient))
        #set current directory (patient folder with nifti masks)
        try:
            os.chdir(os.path.join(nifti_base_dir, patient))
        except:
            print("step 3, line 85; could not find the nifti directory for the given patient")
            exit();
        
        # create folders to save meshes to 
        output_dir = os.path.join(mesh_base_dir, patient)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        #######################################################################
        # # BEGINNING OF READ AND SELECT NIFTIs
        #######################################################################
        nifty_files = [];

        ### read nifti files 
        for side in sides:
            for contour in contour_names:
                #STAPLE contour
                nifty_files.append(NiftiFile(f"{side}_{organ_name}_{contour}_staple.nii" , f"{side}_{organ_name}_{contour}_staple"))
            
                # comparison contours 
                for n in range(0,len(observers)):
                    nifty_files.append(NiftiFile(f"{side}{observers[n]}{contour}.nii" , f"{side}_{contour}_{n+1}"))

        print("read nifti files")
        # # END OF READ AND SELECT NIFTIs
        
        for example in nifty_files:
            # convert to meshes and masks
            mesh, mask = load_n_mesh(example.filepath) 
            # smooth meshes
            mesh = smooth_n_simplify(mesh)
            #save to file
            o3d.io.write_triangle_mesh(os.path.join(output_dir, f"{example.name}.ply"), mesh)
            print("Converted " + example.name)

    print("Completed step 3: converted all .nii files to meshes. ")

