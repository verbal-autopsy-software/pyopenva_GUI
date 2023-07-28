###################################
Welcome to openVA App documentation
###################################

The openVA App implements the `InterVA <https://doi.org/10.1186/s12916-019-1333-6>`_ and
`InSilicoVA <https://doi.org/10.1080/01621459.2016.1152191>`_ algorithms for coding cause of death
from verbal autopsy (VA) data.  This app is intended to be used with VA data collected using the
2016 WHO Verbal Autopsy Instrument, and support will be included for the 2022 instrument when the
algorithms have been updated to use the new format.

The initial window of the openVA App presents two options for analyzing VA data:

  * :doc:`One-Click (Wizard) <wizard>` -- a guided series of windows for assigning CoDs

  * :doc:`Customizable <custom>` -- allows finer control over the analysis with more options


Each option leads to a window where you can view and download the cause-specific mortality
fractions (CSMF), as well as download button for accessing the individual cause assignments.

This documentation also include:

  * :doc:`Analysis of example data set <vignette>`

  * :doc:`Frequently Asked Questions (FAQ) <faq>`

(Each help page can be accessed using the links on the left.)


The openVA App was created and is maintained by the `openVA Team <https://openva.net>`_,
and is graciously supported by the Bloomberg Philanthropies Data for Health Initiative
and Vital Strategies.

The openVA App is licensed under the `GNU General Public License v3.0 <https://www.gnu.org/licenses/gpl-3.0.en.html>`_.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contents:

   One-Click Wizard <wizard>
   Customizable Mode <custom>
   Vignette: analysis with example data <vignette>
   Frequently Asked Questions <faq>
