##### **HELP**  

##### ADDITIONAL RESOURCES

- Office of Water Prediction (OWP), National Water Model  
<http://water.noaa.gov>

- OWP National Water Model Mapping Interface _(this is particularly useful to check COMIDs)_  
<http://water.noaa.gov/map>

- NLDAS-2  
The North American Land Data Assimilation System is a quality-controlled, spatially and temporally consistent meteorological dataset with many uses. It is one product that can be used to force a subsetted NWM domain, after it has been regridded using regridding tools on the WRF-Hydro website.  
<http://ldas.gsfc.nasa.gov/nldas/>


- HydroShare National Water Model Viewer for data collection  
<https://hs-apps.hydroshare.org/apps/nwm-forecasts/>



##### WRF-HYDRO and NCAR RESOURCES

###### The following provides references and brief tips for building WRF-Hydro V5 compatible with the CUAHSI Domain Subsetting Tool: NWM v1.2. 

It should be noted that we do not fully outline how to set up a WRF-Hydro model here and this page intended to give only general advice on the build process in reference to using WRF-Hydro with the CUAHSI NWM subsetting tool. WRF-Hydro is extensively documented by the development team at NCAR and you should refer to the [WRF-Hydro Modeling System website](<https://ral.ucar.edu/projects/wrf_hydro/overview>) and the links below for general WRF-Hydro information.  
For additional [user support](<https://ral.ucar.edu/projects/wrf_hydro/contact>), please contact <wrfhydro@ucar.edu>.

- WRF-Hydro V5 Technical Description:  
<https://ral.ucar.edu/sites/default/files/public/WRF-HydroV5TechnicalDescription_0.pdf>

- WRF-Hydro and NWM Source Code:  
<https://github.com/NCAR/wrf_hydro_nwm_public/tags>

- WRF-Hydro Citation and User Guides:  
<https://ral.ucar.edu/projects/wrf_hydro/technical-description-user-guide>

- Training Materials:  
<https://ral.ucar.edu/projects/wrf_hydro/training-materials>

- The Croton, NY testcase is a good reference for how to compile and run WRF-Hydro:  
<https://ral.ucar.edu/projects/wrf_hydro/testcases>  

- _rwrfhydro_, an R toolbox for managing, analyzing, and visualizing WRF-Hydro data:  
<https://github.com/NCAR/rwrfhydro>  
National Water Model NetCDF domain files and outputs can be easily accessed using the  _rwrfhydro_ package developed at NCAR. 

- Meteorological Forcing Regridding scripts for regridding forcing to the WRF-Hydro geogrid:  
<https://ral.ucar.edu/projects/wrf_hydro/regridding-scripts>

###### _WRF-Hydro Citation_ 
Until further notice please cite the WRF-Hydro Modeling System V5 as follows:  
_Gochis, D.J., M. Barlage, A. Dugger, K. FitzGerald, L. Karsten, M. McAllister, J. McCreight, J. Mills, A. RafieeiNasab, L. Read, K. Sampson, D. Yates, W. Yu, (2018).  The WRF-Hydro modeling system technical description, (Version 5.0).  NCAR Technical Note. 107 pages. Available online at https://ral.ucar.edu/sites/default/files/public/WRF-HydroV5TechnicalDesc.... Source Code DOI:10.5065/D6J38RBJ_


##### Basic WRF-Hydro Model Set-Up (using your subsetted domain):

1. Reference the following documents:  
	- “How to Build and Run WRF-Hydro V5 in Standalone Mode”:  
<https://ral.ucar.edu/sites/default/files/public/HowToBuildandRunWRF-HydroV5inStandaloneMode_0.pdf>
	- “WRF-Hydro V5 Test Case User Guide”:  
<https://ral.ucar.edu/sites/default/files/public/WRF-HydroV5TestCaseUserGuide_4.pdf>

2. Obtain the [source code](<https://github.com/NCAR/wrf_hydro_nwm_public/tags>) for the latest WRF-Hydro release

3. Set the required environmental variables for your machine/environment… this may require some Googling 


4. Configure 

5. Compile with nudging turned off  
The CUAHSI Domain Subsetting Tool: NWM v1.2 does not currently support subsetting of Nudging files.  As such, the model must be compiled using the NoahMP land surface model (LSM) with NUDGING TURNED OFF in the ```setEnvar.sh``` script (```export WRF_HYDRO_NUDGING=0```). 



##### CONTACT & INQUIRES 

For information specific to the CUAHSI Subsetting Tool, contact Tony Castronova <acastronova@cuahsi.org> or Danielle Tijerina <dtijerina@cuahsi.org>.

For information specific to WRF-Hydro please go to the [WRF-Hydro Support Page](https://ral.ucar.edu/projects/wrf_hydro/contact) and contact <nws.nwc.ops@noaa.gov> for questions specifically about the National Water Model.


