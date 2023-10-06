import SimpleITK as sitk
import os

class NiftiFile:
    def __init__(self, filepath, name):
        self.filepath = filepath;
        self.name = name;

def s2_main(nifti_dir, patient_numbers, sides, cntset, observers, organ_name = "breast"): 
    
    for patient in patient_numbers:
        print("Creating staple contours for " + patient)

        for side in sides:
            print(side)
            for contour in cntset:
                try:
                    os.chdir(os.path.join(nifti_dir, patient))
                except:
                    print("step 2, line 10; could not find the nifti directory for the given patient")
                    exit();

                # load masks
                niftis = []
                for n in range(0,len(observers)):
                    niftis.append(NiftiFile(f"{side}{observers[n]}{contour}.nii", str(n+1)))
                        
                # load .nii's using SITK 
                nibs = []
                for nii in niftis:
                    seg_sitk = sitk.ReadImage(nii.filepath)
                    nibs.append(seg_sitk)

                # run STAPLE algorithm 
                staple_filter = sitk.STAPLEImageFilter()
                staple_filter.SetForegroundValue(1)
                staple_image = staple_filter.Execute(nibs)

                staple_specificity = staple_filter.GetSpecificity()
                print("staple_specificity")
                print(staple_specificity)
                staple_sensitivity = staple_filter.GetSensitivity()
                print("staple_sensitivity")
                print(staple_sensitivity)

                # save STAPLE approx to .nii file
                fname = f"{side}_{organ_name}_{contour}_staple.nii"
                sitk.WriteImage(staple_image, fname) 
                print(f"Made {side}_{organ_name}_{contour}_staple.nii")
            
    print("Completed step 2: generated STAPLE contours")

