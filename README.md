This repository contains files needed to add DXF support (import-export) to FreeCAD ( http://free-cad.sf.net ). They cannot be included directly in the FreeCAD source code anymore, because they are licensed under the GPL, and for stupid reasons, the OpenCasCade kernel used in FreeCAD prevents using GPL code in FreeCAD. 

As a result, to avoid further problems, we decided to make FreeCAD LGPL-only, and remove all non-LGPL bits from its source code.

The files included here don't need to be downoaded manually. On first use of the dxf importer or exporter, these files will be downloaded and placed in the appropriate directory, and normally the user would never need to worry about this anymore.

If for some reason the automatic download failed, you can always download these files manually and place them into your FreeCAD user folder ($HOME/.FreeCAD on linuxand mac, C:\Users\yourUser\Application Data\FreeCAD on windows). After that dxf import/export should work normally.

## DOWNLOAD

* For FreeCAD 0.14, you need the dxf lib 1.36. Download it [here](https://github.com/yorikvanhavre/Draft-dxf-importer/archive/1.36.zip).
* For FreeCAD 0.15, you need the dxf lib 1.38. Download it [here](https://github.com/yorikvanhavre/Draft-dxf-importer/archive/1.38.zip).

The "Download ZIP" button on the right of this page always gives you the version needed by the current stalbe release of FreeCAD (currenntly 0.14)

## WARNING

Don't try to save the python scripts here with the "save as..." function of your browser, as it will save html pages, not the python scripts. Use the links above, or the "download ZIP" button on the right side of this page.

## VERSIONS

This repository contains several versions of the DXF importer. The default version, that you download when you press the "download ZIP" button above, is always the version needed by the current stable version of FreeCAD.

If you use another version of FreeCAD, for example a development version or an older version, you might also need another verison of this DXF library. You can find out which version of the DXF library is needed by your version of FreeCAD, by entering the following code in the FreeCAD python console:

    import importDXF
    print importDXF.CURRENTDXFLIB

Then, by using the "branch" button at he top of this page, you can change the version that you will be downloading. Or, more simply, you can use the links provided above.
