One-Click Wizard
================

This mode in the openVA App will guide you through a sequence of windows where you will
walk through the following steps (in order):

1. :ref:`load and prepare the your VA data <wiz_step1>`
2. :ref:`select the algorithm you wish to use for assigning CoDs <wiz_step2>`
3. :ref:`running the algorithm (with user-selected options) <wiz_step3>`

   * :ref:`InSilicoVA<wiz_step3_1>`

   * :ref:`InterVA<wiz_step3_2>`

4. :ref:`accessing the results <wiz_step4>`

Each of these steps is described below.  To access this mode, simply click the
"Start One-Click (Wizard)" button in the initial openVA App window

.. image:: img/openva_app.png


.. _wiz_step1:

Step1: Load and Prepare Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After clicking the "Start One-Click (Wizard)" button on the initial openVA App window, you will
be presented with the "load and prepare data" window where you can: **(a)** load your VA data into the App;
**(b)** select the column in the data file with the ID for the autopsy records; and **(c)** select the version
of the WHO VA instrument that was used to collect the VA data.


.. image:: img/wiz_load_data.png


(a) Here you can load a comma-separated values (CSV) file containing VA data into the openVA App.
This mode is designed to work with CSV exports from an `ODK Central Server <https://docs.getodk.org/central-intro>`_.
Clicking the "Load Data (.csv)" button will open a new window in which you can navigate your computer's
folders to find your VA data file.  Once you have located your CSV file, select the file by clicking on it,
and then click on the Open button.  The "load and prepare data" window should now display a message that your
data have been loaded, along with the name of the CSV file, and the number of deaths included in your VA data.
If there is a problem (e.g., the file is corrupt or empty), then a message will appear stating that the openVA
App is unable to to load the data file.  In this case, check to make sure you can open the CSV file in a spreadsheet
program and that the file is not empty.

(b) After loading your data, click on the arrows to display a list of the column names in the CSV data file.
Scroll to the column name that you would like to use as the ID for the individual VA records and click on the name.
In a later step, you will be able to run an algorithm and save the assigned causes as a CSV file.  This file will
include the ID column you selected oo help you identify the VA records.  The default option (which appears after the
data file is loaded) is "no ID column", which will simply use integers 1, 2, 3, ... for the ID.

(c) As of now, the openVA App is only able to process VA data collected using the 2016 WHO VA instrument,
and thus this is the only option.  When the InterVA and InSilicoVA algorithms have been updated to use
data collected with the 2022 WHO VA instrument, the openVA App will also be updated.

Once you have loaded your data and chosen your ID column, click on the Next button to go to the next window where you
can select the algorithm you want to use to assign COD to your VA records.  Alternatively, you can click the
Back button to return to the window where you can select the mode (either One-Click Wizard mode, or the Customizable
mode).  Finally, you can click the Exit button to close the openVA App.


.. _wiz_step2:

Step 2: Select Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~

The openVA App displays the "select algorithm" window after you advance from the "load and prepare data" window.  Simply
click on the InSilicoVA button to run this algorithm.  **Please note that your data file must include at least 100
deaths to use the InSilicoVA algorithm.** [#]_ If the CSV data file that you loaded includes less than one hundred
records, clicking on the InSilicoVA button will produce a message stating that "InSilicoVA is unavailable.  At least 100
deaths are needed for reliable results. (InterVA is available.)"


Alternatively, click on the "InterVA" button to use the InterVA5 algorithm to assign causes of death to the VA records.


.. image:: img/wiz_select_alg.png


Clicking on one of the algorithm buttons will switch the app to a new window where you will be able to run either
InSilicoVA algorithm or the InterVA algorithm.  Alternatively, you can click the Back button to return to the window
where you can load and prepare your data; or you can click the Exit button to close the openVA App.


.. _wiz_step3:

Step3: Run the Algorithm with Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The openVA App offers COD assignment using either the InSilicoVA or InterVA algorithm.  In the One-Click Wizard mode,
each algorithm has its own window, which are described in turn.

.. _wiz_step3_1:

----------
InSilicoVA
----------

The InSilicoVA window in the One-Click Wizard mode simply allows users to start (and stop) the algorithm and
to save the message log from the data consistency check procedure.


.. image:: img/wiz_run_insilicova.png


Once the data have been loaded (with at least 100 deaths included in the data file), clicking the "Run InSilicoVA"
button will start the process of assigning CODs.  This procedure includes 3 steps.  First, the app will convert the data
from the ODK format to the format expected by the algorithm. [#]_ Next, the app will run the data consistency
checks. [#]_  During these first two steps the openVA App will display a "preparing data" message below the progress bar.
During the final step, the app will start the process of assigning CODs and the progress bar will start advancing
(you will also see a message "Running InSilicoVA.." below the progress bar).  Depending on the size of the data set, it
may take a while for the InSilicoVA algorithm to finish -- a data set with 100 deaths takes around 12 minutes to process
with InSilicoVA.  The progress bar may reset once or twice, as the InSilicoVA algorithm works towards convergence
of its sampling procedure for obtaining results.  Finally, there is a "Stop" button that will stop the InSilicoVA
algorithm -- if stopped, the algorithm will need to run through all of the steps from the beginning when restarted.

Once the results are ready, the message below the progress bar will indicate that the "InSilicoVA results are ready"
and you will be able to access the results and the log from the data consistency checks.  Clicking on the
"Save log from data checks" button will produce a new window where you can choose the location for saving the log file
from the data consistency check.

Clicking on the "Show Results" button will take you to a new window where you will be able to access the cause of death
results produced by InSilicoVa.  Clicking the "Back" button will return to the window where you can select the
algorithm, and you can click the "Exit" button to close the openVA App.


.. _wiz_step3_2:

-------
InterVA
-------

Here ww will include the screenshot of InterVA mode and describe the different options.


.. _wiz_step4:

Step 4: Access Results
~~~~~~~~~~~~~~~~~~~~~~

Only able to show results for one algorithm at a time.[#]_

.. rubric:: Footnotes

.. [#]  While it is possible to run InSilicoVA with fewer deaths, our experience suggests that the results are more
        reliable with larger sample sizes.  In our experimentation with VA data (with external causes assigned), 100
        deaths provided to be a reasonable threshold for obtaining reliable results.
.. [#]  Converting the data from the ODK format to the format expected by the algorithms is carried out using the
        pyCrossVA tool.  If you are interested in seeing the output from this step, you can use the openVA App's
        Customizable mode.  We need a user friendly introduction webpage for what pyCrossVA is actually doing.
.. [#]  For mor information about the data consistency checks, see the :ref:`FAQ page<faq_data_consistency_checks>`.
.. [#]  The openVA App's Customizable mode allows users to view results from both InterVA and InSilicoVA.

:doc:`Home <index>`  :doc:`Customizable Mode <custom>`
