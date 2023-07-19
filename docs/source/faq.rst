Frequently Asked Questions
==========================

**Why do I need at least 100 deaths to run the InSilicoVA algorithm?**
    While it is possible to run InSilicoVA with fewer deaths, our experience
    suggests that the results are more reliable with larger sample sizes.  In
    our experimentation with VA data (with external causes assigned), 100 deaths
    provided to be a reasonable threshold for obtaining reliable results.

**Why are some deaths removed from the analysis (and not assigned a cause)?**
    If the VA record is missing information on either sex or age, then this death
    is removed from the analysis and is NOT assigned a cause of death.  Both of
    these demographic indicators are crucial to the assignment of CODs and the
    algorithms filter out these VA records before assigning causes of death.

**Why does the progress bar for InSilicoVA reset a few times after reaching the end?**
    InSilicoVA obtains results by making draws from a distribution.  With each draw, the
    progress bar inches forward a bit. After a certain number of draws are taken,
    InSilicoVA checks the quality of the sample (i.e., the collection of draws taken
    thus far) -- this is referred to as checking for convergence.  If the quality of the
    sample does not pass a certain threshold, then InSilicoVA makes more draws in an
    effort to improve the quality of the sample; and this is when the progress bar resets.
    After this second round of sampling, InSilicoVA will check the quality of the sample
    again, and if it has not reached the desired level of quality (i.e., converged), then
    the algorithm begins a third (and much longer) round of sampling, with the progress
    bar resetting again.

.. _faq_data_consistency_checks:

**What are the data consistency checks?**
    Both the InterVA and InSilicoVA algorithms perform a set of data consistency checks
    to make sure that the symptoms and indicators are in alignment.  For example, males
    should not have indicators of being pregnant or having symptoms specific to females.
    Another common example checks that the symptom is appropriate for the age group of
    the decedent.  If inconsistencies are found, then changes are made to a working data
    file (not the original data) and a message is added to the log file.  For more
    information see the `openVA GitHub repository <https://github.com/verbal-autopsy-software/vacheck#details>`_.

.. _faq_pycrossva:

**What is pyCrossVA?**
    Converting the data from the ODK format to the format expected by the algorithms is carried out using the
    pyCrossVA tool.  When a CSV data file is loaded into to the openVA App, these data are passed to pyCrossVA, which
    searches for the columns needed to produce the new variables in the output dataset expected by the algorithms.  If
    needed columns are found, then pyCrossVA performs the appropriate transformation to create the new variable;
    otherwise, pyCrossVA proceed as if the needed variable was present but had missing values for all of the VAs.
    pyCrossVA also allows users to specify the ID column.


:doc:`Home <index>`  :doc:`Customizable Mode <custom>`
