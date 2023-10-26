####################################
Vignette: analysis with example data
####################################

This help page walks through an example session of the One-Click Wizard mode.  We will use the InterVA5 algorithm
to assign causes of death to the example data set included with the openVA App.


#. **Set working directory**: The openVA App has several features allowing you to load or save files.  It can be useful
   to set a working directory, which is a folder on you computer where the app will open as the default location for
   opening or saving files.  You can set the working directory using the menu bar: `File` -> `Set working directory`.  In
   the new window that opens, go to the folder that you would like to use as the working directory, click on it, and then
   click `Open`.

   .. image:: img/vignette_setwd.png

#. **Load example data set**: On the menu bar click on the following sequence of menus:
   `Data` -> `Load example data in...` -> `Wizard mode`.  The openVA App should switch to the "load and prepare data"
   window.  Below the "Load Data (.csv)" button, you should see a message stating that the example data set has been
   loaded with 111 VA records.  This example data set was created with the 2016 WHO VA instrument, but it contains a
   few errors for illustrative purposes.

   .. image:: img/vignette_load_data.png

#. **Select column ID**: If there is a column in your data set that contains an ID for uniquely identifying the deaths,
   you can select this column name so the ID will be included when you save the individual cause assignments.  To do so,
   click on the box under the label "Select ID column in data".  This will display a list of the column names in your
   data file.  Simply click on the column name that serves as the ID.  In the example data set (a downloaded CSV export
   from ODK Central), the `meta-instanceID` column contains unique values for each VA record.  If you select a column
   that does not uniquely identify each row, then the openVA App will give a warning message.  After selecting the ID
   column, click the "Next" button which will take you to the "select algorithm" window.

   .. image:: img/vignette_select_id.png

#. **Select algorithm**: Click on the "InterVA" button and the openVA App will display a new window for selecting the
   InterVA options and running the algorithm.

   .. image:: img/vignette_select_interva.png

#. **Select InterVA options**: The "InterVA" window contains two option boxes for selecting the HIV and Malaria input
   parameters.  Clicking on either box will display a menu with 3 options: `high`, `low`, and `very low`.  These
   parameters characterize the prevalence of HIV/AIDS and malaria deaths in the region where your VA data were
   collected.  According the User Guide for the original InterVA5 software, these levels roughly correspond to the cause
   accounting for 1.0% of all deaths (high), 0.10% (low), and 0.01% (very low).

   .. image:: img/vignette_select_interva_options.png

#. **Start the InterVA algorithm**: Now click on the "Run InterVA" button, which causes the openVA App to go through
   three steps:  (1) use pyCrossVA to convert the VA data from ODK format to the format expected by the algorithms;
   (2) perform the data consistency check; and (3) assign causes of death with the InterVA algorithm.

   .. image:: img/vignette_run_interva.png

   After starting the algorithm you will see a message giving the values for the HIV and Malaria parameters used for the
   current run (this message appears below the "Run InterVA" button).  It should only take a few second for pyCrossVA to
   create the new data set for InterVA.  Once its job is complete, the message from pyCrossVA is displayed in the
   box below the start button.  If the original VA data file is in the expected format, then pyCrossVA will have no
   problems and report that "pyCrossVA finished.  All good!"; otherwise, pyCrossVA will produce a message that typically
   lists columns that are missing in your data that are needed to create the input file for InterVA (or InSilicoVA).
   Next, the openVA App will perform the data consistency checks and if any VA records are removed from the data set
   (due to missing data), then a new window will appear with a list of IDs for the records that have been removed.
   (If no deaths are removed, then this window will not appear.)

   .. image:: img/vignette_run_interva_data_check_msg.png

   Once you click the "OK" button on the pop-up window the message will close and the progress bar will begin marching
   forward as InterVA assigns causes to the VA data (this should take a minute or two).

   .. image:: img/vignette_running_interva.png

#. **Inspect the data check log**: When the InterVA algorithm has finished assigning causes, the message below the
   "Run InterVA" button will state that the "InterVA5 results are ready (7 deaths failed data check)."  The part about
   the 7 deaths failing the data checks indicates that 7 records do not have enough information for InterVA (or
   InSilicoVA) to assign a causes.  More specifically, these records have a missing value for either age or sex, or all
   of the symptoms have missing information (which may happen if the respondent did not provide consent for the VA
   interview).  To get more details about these records, as well as any inconsistencies in the data (which the InterVA
   algorithm tries to correct), you can save the log file (as a text file) by clicking on the
   "Save Log from data checks" button.

   .. image:: img/vignette_ready_interva.png

   You can open the log file with any text editor (e.g., Notepad or Wordpad), and the contents should look like the
   following screenshot.  For more information about the data consistency checks, see the
   :ref:`FAQ page<faq_data_consistency_checks>`.

   .. image:: img/vignette_interva_log.png

#. **Switch to the results window**: Now, click on the "Next" button, which will take you to the "Results" window where
   you can view and save the InterVA results.

   .. image:: img/vignette_show_results.png

#. **Results window**: The "Results" window has three different panels: "Options", "Show Results", and "Save Results".
   The "Options" panel (at the top of the window) includes controls for choosing the number of CODs to include in
   summaries of the cause-specific mortality fractions (or CSMFs).  Here, you can also choose to display the CSMF
   results as proportions (the default is to use percentages ranging from 0 to 100), and to examine your results for
   different age groups (adults, children, and neonates), for females or males, or a combination of the two demographic
   variables.  In the "Show Results" panel located in the middle of the window, includes buttons for viewing the CSMF
   distribution as a table or a plot.  There is also a "Show demographics" button which will display a table with the
   number of deaths by age and sex.  These results, as well as the individual cause assignments, can be saved using the
   buttons in the bottom panel (under the label
   "Save Results").

   .. image:: img/vignette_interva_results.png

#. **Examine demographics**: To get a sense for how much information we have for the different demographic groups, let's
   first turn our attention to the "Show Results" panel in the middle of the window, and click on the
   "Show demographics" button.

   .. image:: img/vignette_interva_show_dem.png

   The new window that appears (see the following screenshot) displays the number of deaths we have by age and sex.  In
   the example data set, we have 66 adults; this is not a lot of information, but we will explore these results to
   illustrate what the openVA App can do.  Finally, to close the demographic table, click on the "X" in the upper-right
   corner of the window.

   .. image:: img/vignette_interva_dem_tab.png


#. **Select age group and # of top causes**: In our next step, we will focus on the CSMF for adults by clicking on the
   option box for "age" and select `adult`.

   .. image:: img/vignette_interva_select_adults.png

   Since there are only 66 adults, we will start by limiting our analysis to the top 3 causes in the CSMF.  To do so,
   locate the box in the "Options" panel with the text "Include 5 causes in the results".  Click on the down arrow to
   reduce the number of top causes from 5 to 3.

   .. image:: img/vignette_interva_ntop.png

#. **Look at the CSMF plot**: Now let us take a look at the CSMF plot by clicking on the "Show CSMF plot" button in the
   "Show Results" panel.

   .. image:: img/vignette_interva_show_plot.png

   The openVA App will produce a new window with a bar chart of the top 3 causes.  Note how the title includes the
   demographic group we are focusing on.  Over 17.5% of the adult deaths were due to Acute respiratory infections,
   including pneumonia, while about 15% were HIV/AIDS related deaths, and about 11% of adult deaths were caused by
   acute cardiac disease.

   .. image:: img/vignette_interva_csmf.png

#. **Select more causes and view the CSMF table**: Although we do not have a lot of information (only 66 adult deaths),
   let's increase the number of deaths to 12 so we can illustrate another feature of the openVA App.

   .. image:: img/vignette_interva_ntop_12.png

   Next, click on the "Show CSMF table" button in the middle panel of the window.

   .. image:: img/vignette_interva_show_tab.png

   Again, to close this window, simply click on the "X" in the top right corner of the window with the CSMF table.

   .. image:: img/vignette_interva_tab.png

#. **Save the individual cause assignments with VA data**: In the final steps, we will merge the original VA data to
   the individual causes assigned by InterVA, and then save the results as a CSV file.  To do this, first click in the
   checkbox located at the bottom of the "Save Results" panel.  As the label states, this will
   "Include VA data (with individual CODs)".  Next, click on the button "Save Individual Cause Assignments", which will
   produce a new window where you can choose where to save the results as a CSV file.  Note that the default file name
   is "interva_adult_individual_cod.csv" indicating that these results will only include the 66 cause assignments for
   the adults.

   .. image:: img/vignette_interva_save_data.png

   The results, when opened in a spreadsheet program, should look like the following screenshot.  You should verify
   that the values in the meta-InstanceID column match the ID column in the saved file.

   .. image:: img/vignette_interva_indiv.png


|:tada:| Congratulations |:tada:|  You have finished the tour of the openVA App and are hopefully ready to begin analyzing your own
data.

===================  ==================================  =================================  ================
:doc:`Home <index>`  :doc:`One-Click (Wizard) <wizard>`  :doc:`Customizable Mode <custom>`  :doc:`FAQ <faq>`
===================  ==================================  =================================  ================
