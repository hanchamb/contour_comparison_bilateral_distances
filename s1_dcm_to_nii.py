import os
from DicomRTTool import DicomReaderWriter   # using this magic package to convert from dicom to nifti: https://pypi.org/project/DicomRTTool/
import SimpleITK as sitk

def s1_main(dicom_base_dir, nifti_base_dir, patient_numbers, organ_name):

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
        
        names = reader.return_rois(print_rois=False)
        for name in names:
            if (organ_name in name): 
                reader.set_contour_names_and_associations([name])
                reader.get_mask()
                sitk.WriteImage(reader.annotation_handle, os.path.join(nifti_dir, f"{name}.nii"))
                print("Completed converting contour " + name)

    print("Step 1 complete: \n\t.dcm converted to .nii")
