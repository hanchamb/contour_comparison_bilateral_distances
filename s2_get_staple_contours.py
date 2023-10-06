import SimpleITK as sitk
import os

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

def s2_main(nifti_base_dir, patient_numbers, sides, contour_set, observers, organ_name = "breast"): 
    """
    Step 2 main function: Creates staple contour from all observers' contours as a nifti file.


    Parameters
    ----------
    nifti_base_dir : filepath
        The filepath which is the base directory for all the patient directories which store patients' nifti files (created in step 1).
    patient_numbers : array of str
        The patient numbers, which are also the directory names for the directories in nifti_base_dir
    sides: array of str
        The laterality of the organ contour (here used to loop over left and right breast nifti files). Used to select the contours to be included in the STAPLE algorithm, i.e. only uses left contours to create the left breast STAPLE contour.
    contour_set : array of str
        The type of the organ contour. Example used here is "manual" contours and "altas-edited" contours, as we are do inter observer and inter-method analysis simultaneously. Used to select the contours to be included in the STAPLE algorithm, i.e. only uses "manual" contours to create the "manual breast STAPLE contour").
    observers : array of str
        Array of strings which idicate the observer which generated the organ contour. Included in the naming of the region of interest contour in you treatment planning system, thus included in the naming of the nifti file sed to generate the STAPLE contour.      
    organ_name : str
        The organ name which is featured in the name of the region of interest's nifti file.
    
 
    Returns
    -------
    None
    """
    #loop over patients' nifti directories
    for patient in patient_numbers:
        print("Creating staple contours for " + patient)

        # loop over laterality of the contour
        for side in sides:
            # loop over the type of contour ("manual" or "atlas-edited")
            for contour in contour_set:
                # locate the nifti directory for the patient
                try:
                    os.chdir(os.path.join(nifti_base_dir, patient))
                except:
                    print("step 2, line 10; could not find the nifti directory for the given patient")
                    exit();

                # load nifti file filepaths into array
                niftis = []
                for n in range(0,len(observers)):
                    niftis.append(NiftiFile(f"{side}{observers[n]}{contour}.nii", str(n+1)))
                        
                # read niftis using SITK 
                nibs = []
                for nii in niftis:
                    seg_sitk = sitk.ReadImage(nii.filepath)
                    nibs.append(seg_sitk)

                # run STAPLE algorithm 
                staple_filter = sitk.STAPLEImageFilter()
                staple_filter.SetForegroundValue(1)
                staple_image = staple_filter.Execute(nibs)

                # print specificity of STAPLE algorithm 
                # TODO: save specificity to separate file 
                staple_specificity = staple_filter.GetSpecificity()
                print("staple_specificity")
                print(staple_specificity)
                # print sensitivity of STAPLE algorithm 
                # TODO: save sensitivity to separate file 
                staple_sensitivity = staple_filter.GetSensitivity()
                print("staple_sensitivity")
                print(staple_sensitivity)

                # save STAPLE contour to .nii file
                fname = f"{side}_{organ_name}_{contour}_staple.nii"
                sitk.WriteImage(staple_image, fname) 
                print(f"Made {side}_{organ_name}_{contour}_staple.nii")
            
    print("Completed step 2: generated STAPLE contours")

