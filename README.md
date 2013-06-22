This repository contains files needed to add DXF support (import-export) to FreeCAD ( http://free-cad.sf.net ). They cannot be included directly in the FreeCAD source code anymore, because they are licensed under the GPL, and for stupid reasons, the OpenCasCade kernel used in FreeCAD prevents using GPL code in FreeCAD. 

As a result, to avoid further problems, we decided to make FreeCAD LGPL-only, and remove all non-LGPL bits from its source code.

The files included here don't need to be downoaded manually. On first use of the dxf importer or exporter, these files will be downloaded and placed in the appropriate directory, and normally the user would never need to worry about this anymore.

If for some reason the automatic download failed, you can always download these files manually and place them into your FreeCAD user folder ($HOME/.FreeCAD on linuxand mac, C:\Users\yourUser\Application Data\FreeCAD on windows). After that dxf import/export should work normally.