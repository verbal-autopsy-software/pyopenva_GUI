# Version 1.1 (2023-11-29)

## Changes & New Features

- Bug fix: the documentation files can now be viewed on macOS (using cx_Freeze version 6.15.11).
- New option for setting "InterVA rule" (for calculating CSMF) in customizable mode
 [#24](https://github.com/verbal-autopsy-software/pyopenva_GUI/issues/24).
   - Removed option for excluding 'Undertermined' from CSMF (with re-normalization step).
- When saving VA data with individual-level results, only the item name (e.g., Id10002) is included in the CSV file.
- New option to use either percentages or proportions for CSMF (default is %)
- Updated documentation to describe differences between InSilicoVA & InterVA.
- Exception handling for trying to load non utf-8 data.
