import numpy as np
import skimage.measure
import SimpleITK as sitk
import open3d as o3d
import os
from scipy import ndimage

# FUNCTION DEFINITIONS 

def load_n_mesh(fname):
    """
    load_n_mesh : Converts individual nifti files to .ply meshes 


    Parameters
    ----------
    fname : filepath
        The filepath to the nifti file to be converted to the mesh
    
    Returns
    -------
    mesh : o3d.geometry.TriangleMesh()
        the triangulated mesh created from the nifti file  
    
    mask : np.array 
        np.array created from the conversion of the nifti file using SimpleITK

    """
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
    """
    Optional function to apply smoothing to the mesh returned from load_n_mesh. Taubin smoothing included as an example


    Parameters
    ----------
    mesh : o3d.geometry.TriangleMesh()
        the triangulated mesh created from the nifti file 
    
    Returns
    -------
    mesh : o3d.geometry.TriangleMesh()
        the triangulated mesh created from the nifti file, which has been smoothed by this function
    
    """
    
    #mesh = mesh.filter_smooth_taubin(number_of_iterations=1)

    return mesh

class NiftiFile:
    """
    A class to store a filepath to a nifti file, and store the name for ease of use in the remaining code.

    ...

    Attributes
    ----------
    filepath : str
        filepath to the nifti file
    name : str
        name of the nifti file, i.e. the filepath without the extension

    Methods
    -------
    None
    """
    def __init__(self, filepath, name):
        self.filepath = filepath;
        self.name = name;

def s3_main(nifti_base_dir, mesh_base_dir, patient_IDs, observers, sides, contour_names, organ_name = "breast"):
    """
    Step 3 main function: Convert nifit files to .ply meshes by looping over patient number, organ laterality, and contour names. 


    Parameters
    ----------
    nifti_base_dir : filepath
        The filepath which is the base directory for all the patient directories which store patients' nifti files (created in step 1).
    mesh_base_dir : filepath
        The filepath which is the base directory for all the patient directories which store patients' mesh files, created in this step.    
    patient_IDs : array of str
        The patient numbers, which are also the directory names for the directories in nifti_base_dir
    observers : array of str
        Array of strings which idicate the observer which generated the organ contour. Included in the naming of the region of interest contour in you treatment planning system, thus included in the naming of the nifti file sed to generate the STAPLE contour.      
    sides: array of str
        The laterality of the organ contour (here used to loop over left and right breast nifti files). Used to select the contours to be included in the STAPLE algorithm, i.e. only uses left contours to create the left breast STAPLE contour.
    contour_names : array of str
        The type of the organ contour. Example used here is "manual" contours and "altas-edited" contours, as we are do inter observer and inter-method analysis simultaneously. Used to select the contours to be included in the STAPLE algorithm, i.e. only uses "manual" contours to create the "manual breast STAPLE contour").
    organ_name : str
        The organ name which is featured in the name of the region of interest's nifti file.
    
 
    Returns
    -------
    None
    """
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

        ### read nifti files and store to array 
        nifti_files = [];
        # loop over organ laterality
        for side in sides:
            # loop over contour names included in file name (here either "manual" or "atlas-edited")
            for contour in contour_names:
                # STAPLE contour
                nifti_files.append(NiftiFile(f"{side}_{organ_name}_{contour}_staple.nii" , f"{side}_{organ_name}_{contour}_staple"))
            
                # comparison contours 
                for n in range(0,len(observers)):
                    nifti_files.append(NiftiFile(f"{side}{observers[n]}{contour}.nii" , f"{side}_{contour}_{n+1}"))

        print("finished reading nifti files")
        
        #loop over nifti files and convert to meshes
        for example in nifti_files:
            # convert to meshes and masks
            mesh, mask = load_n_mesh(example.filepath) 
            # smooth meshes
            mesh = smooth_n_simplify(mesh)
            #save to .ply file
            o3d.io.write_triangle_mesh(os.path.join(output_dir, f"{example.name}.ply"), mesh)
            print("Converted " + example.name)

    print("Completed step 3: converted all .nii files to meshes. ")

