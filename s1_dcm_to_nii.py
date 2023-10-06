import os
from DicomRTTool import DicomReaderWriter   # using this magic package to convert from dicom to nifti: https://pypi.org/project/DicomRTTool/
import SimpleITK as sitk

def s1_main(dicom_base_dir, nifti_base_dir, patient_numbers, organ_name):
    """Step 1 main function: Converts the DICOM RTStruct file to a nifti file for each contour.


    Parameters
    ----------
    dicom_base_dir : filepath
        The filepath which is the base directory for all the patient directories which contain patients' DICOM data. 
    nifti_base_dir : filepath
        The filepath which is the base directory for all the patient directories which will store patients' nifti files, created in this step.
    patient_numbers : array of str
        The patient numbers, which are also the directory names for the directories in dicom_base_dir and nifti_base_dir
    organ_name : str
        The organ name which is featured in every region of interest to be converted to nifti files. This flag avoids converting unnecessary regions of interest stored in the RT struct file, thus avoiding pre-processing in your treatment planning system 
    
 
    Returns
    -------
    None
    """

    #loop over patients' DICOM directories
    for patient in patient_numbers:
        print("Working with patient " + str(patient))

        #going into the dicom directory for that patient
        dicom_dir = os.path.join(dicom_base_dir, patient)

        # making the directory to store that patients' nifti files 
        nifti_dir = os.path.join(nifti_base_dir, patient)
        if not os.path.exists(nifti_dir):
            os.mkdir(nifti_dir)
        
        reader = DicomReaderWriter()
        reader.walk_through_folders(dicom_dir)
        reader.get_images()
        
        # create array of the regions of interest names store in the RTStruct file 
        names = reader.return_rois(print_rois=False)
        for name in names:
            # only convert the regions of interest in the RTStruct which contain the 'organ_name' (specfied in the call to the function)
            if (organ_name in name): 
                reader.set_contour_names_and_associations([name])
                reader.get_mask()
                sitk.WriteImage(reader.annotation_handle, os.path.join(nifti_dir, f"{name}.nii"))
                print(f"Completed converting contour {name}")

    print("Step 1 complete: \n\t.dcm converted to .nii")
