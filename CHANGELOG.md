v0.23.0
feat: add pole plotting and structural data rotation
- Added pole plotting with dedicated pole settings
- Added conversion between planes and poles (Planes to Poles and Poles to Planes)
- Added rotation of structural elements around an arbitrary axis
- Added contour plotting for poles
- Added rotation dialog with configurable axis, rotation angle and output precision
- Refactored calculation and file handling modules
- Added pole dataset example
- Added application icons in ICO, PNG and SVG formats to assets

v0.22.0
improve: refine settings dialogs and stereonet interaction
- Improved Plane Settings dialog with a reorganised layout and additional controls
- Improved Contour Settings dialog with enhanced layout and additional controls
- Added measurement comments to stereonet annotations
- Adjusted annotation positioning and appearance
- Refined plane highlighting and plotting appearance
- Added accellerators to File menu items for quicker access

v0.21.0
feat: introduce PyStereo, add Planes to Poles conversion and improve data handling and plotting
- Renamed the main application module from Stereo.py to PyStereo.py
- Added Planes to Poles functionality for converting plane orientations into pole orientations
- Added support for combined datasets containing planes and lineations
- Improved dataset handling and integration
- Refactored GUI dialogs and plotting components
- Improved contour plotting options and appearance
- Enhanced plane and lineation plotting
- Fixed axis clearing issues in plot panels
- Updated map projection handling
- Added CITATION.cff for software citation
- Updated project documentation and licensing information
- Removed obsolete experimental Fisher statistics scripts and supporting files

v0.20.0
refactor: improve application structure, plotting and prepare Fisher statistical analysis
- Refactored and cleaned up the application code
- Added preliminary Fisher statistical analysis scripts and supporting calculation resources
- Improved contour plot appearance by adjusting symbol size, line width and colour map
- Updated lineation symbol size
- Improved file dialog layout and measurement comment handling
- Updated application metadata and release date

v0.19.0
refactor: improve internal code structure and application organisation
- Refactored internal application components in preparation for further development
- Improved code organisation and maintainability
- Prepared the codebase for upcoming statistical analysis features

v0.18.0
feat: introduce settings menu with dedicated configuration dialogues for v0.18.0
- Integrated PlaneDialog from the new dialogs package
- Added a 'Settings/Plane' cascade to the main application menu bar
- Linked menu commands to launch preference dialogues for planes
- Implemented redraw callbacks within dialogues to update the plot dynamically

v0.17.0
feat: integrate contour settings and preference dialogues for v0.17.0
- Integrated ContourSettings and ContourDialog into the application workflow
- Added a 'Contours...' option to the Settings drop-down menu
- Initialised contour configuration state within StereoApp alongside planes and lineations
- Updated PlotPanel to pass all three setting objects dynamically to the projection engine

v0.16.0
feat: introduce plot settings classes for planes and lineations in v0.16.0
- Integrated LineationSettings and PlaneSettings from the new plots package
- Initialised setting instances within StereoApp to centralise plot configuration
- Updated PlotPanel to pass configuration state dynamically to the StereonetProjection
- Reordered names in the __AUTHOR__ metadata tuple

v0.15.0
- Introduced modular plots package
- Added LineationPlot
- Added PlanePlot
- Added ContourPlot
- Refactored projection dispatcher
- Preserved plotting behaviour

v0.14.0
feat: implement density contouring for lineations and add GUI filter for v0.14.0
- Integrated 'density_contourf' from mplstereonet to plot lineation density distributions
- Overlaid lineation data points as small markers on top of density contours for clarity
- Added a 'Contours' radio button to the UI display management panel
- Enhanced plot resetting by explicitly removing active annotation objects during redraws

v0.13.0
feat: implement bidirectional highlighting and custom axes styling for v0.13.0
- Added highlight_by_index method to projection module to trigger plot highlighting from table rows
- Customised stereonet appearance by disabling default grid lines and adding a central cross marker
- Fixed display filtering by correctly passing the active UI mode to the projection drawing method
- Standardised internal terminology by updating plane filters from 'planes' to 'surfaces'
- Cleaned up imports and reformatted the AUTHOR tuple for better readability

v0.12.0
feat: link table selection with plot highlighting and add display filters for v0.12.0
- Bound Treeview selection events to highlight the corresponding geological feature on the stereonet
- Added a radio button control panel to filter the plot view (All, Planes, Lineations)
- Implemented automatic plot redrawing immediately after a data file is successfully loaded
- Created the highlight_by_index method in PlotPanel to support cross-component interaction

v0.11.0
refactor: decouple stereonet plotting logic into a separate projection module for v0.11.0
- Extracted all plotting and data filtering logic from the GUI into a new 'projection.py' module
- Implemented the StereonetProjection class to handle geological data conversions (azimuth/dip to strike)
- Added interactive pick events to highlight selected features in red and display annotations dynamically
- Integrated the new StereonetProjection class into the main StereoApp workflow
- Cleaned up the main script by separating plotting functionality from UI rendering

v0.10.0
refactor: overhaul application architecture into modular panels and integrate stereonet canvas v0.10
- Refactored UI into dedicated DataPanel and PlotPanel classes for better separation of concerns
- Embedded Matplotlib FigureCanvasTkAgg with an mplstereonet projection into PlotPanel
- Rewrote read_data to parse and validate row values into structured dictionaries (id, azimuth, dip)
- Switched layout manager to Grid with column weights to enable smooth window resizing
- Added horizontal scrollbar to the Treeview widget and cleaned up table column headers

v0.9.0
feat: implement cross-platform icon handling and bump to v0.9
- Added cross-platform icon loading supporting .ico on Windows and .png on other OS platforms
- Wrapped icon loading in try-except blocks to prevent application crashes if files are missing
- Added Zuzana Lahová to the AUTHORS list
- Restricted Treeview data insertion to the first 5 columns to prevent indexing errors

v0.8.0
feat: add structural measurement type column to the data table for v0.8
- Added 'type' column to the Treeview to categorise geological features
- Configured column headings, width, and center alignment for the new type field
- Left-aligned the comments column heading in the table view

v0.7.0
feat: redesign application layout into two panels for v0.7
- Increased base window size to 1000x600
- Split layout into a left panel (data) and a right panel (stereonet)
- Modularised table creation into a separate _vytvor_tabulku method
- Added support for .csv files in the file dialogue
- Adjusted Treeview column widths for the side panel