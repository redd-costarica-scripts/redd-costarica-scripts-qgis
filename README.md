# Scripts de QGIS para procesamiento de datos de Costa Rica para REDD+

Este repositorio contiene un conjunto de *scripts* para procesar datos de Costa Rica relacionados con el mecanismo de [Reducción de Emisiones por Deforestación y Degradación de bosques más conservación y aumento de reservas de carbono forestal (REDD+)](https://es.wikipedia.org/wiki/Reducci%C3%B3n_de_las_emisiones_de_la_deforestaci%C3%B3n). Los scripts de distriuyen como un complemento del sistema de información geográfica [QGIS](https://qgis.org) y su marco de trabajo [Processing](https://docs.qgis.org/3.22/en/docs/user_manual/processing/intro.html).

## Instalación

### Herramientas

1. [QGIS](https://qgis.org): sistema de información geográfica. En este proyecto, se utilizó la **versión 3.22.11 Białowieża LTR**. Siga las instrucciones correspondiente a su sistema operativo en la [página de descargas de QGIS](https://qgis.org/en/site/forusers/download.html). Para el caso de Microsoft Windows, se recomienda el instalador [OSGeo4W](https://qgis.org/en/site/forusers/alldownloads.html#osgeo4w-installer).
2. [Orfeo Toolbox (OTB)](http://orfeo-toolbox.org/): biblioteca para procesamiento de imágenes de satélite. En este proyecto, se utilizó la **versión 8.1.0**. Siga las instrucciones correspondientes a su sistema operativo en la [página de descargas de OTB](https://www.orfeo-toolbox.org/download/).
    1. Configure la [interfaz de QGIS para OTB](https://www.orfeo-toolbox.org/CookBook/QGISInterface.html).
3. [Fmask](https://github.com/GERSL/Fmask): software para la generación de máscaras de nubes y sombras en imágenes satelitales. En este proyecto, se utilizó la **versión 4.6**. Siga las instrucciones correspondientes a su sistema operativo.
4. [R](https://www.r-project.org/) y [RStudio Desktop](https://www.rstudio.com/products/rstudio/): lenguaje de programación para análisis estadístico y ambiente de desarrollo integrado. En este proyecto, se utilizó la **versión 4.2.1 de R** y la **versión 2022.07.1+554 de RStudio Desktop**. Siga las instrucciones correspondientes a su sistema operativo en la [página de descargas de R](https://cloud.r-project.org/) y en la [página de descargas de RStudio](https://www.rstudio.com/products/rstudio/download/).

Adicionalmente, para usuarios avanzados, se recomienda instalar el sistema para control de versiones [Git](https://git-scm.com/). Siga las instrucciones correspondientes a su sistema operativo en la [página de descargas](https://git-scm.com/downloads).

### Complemento `REDD+ Costa Rica` de QGIS
Puede descargar el complemento como un [archivo ZIP](https://github.com/redd-costarica-scripts/redd-costarica-scripts-qgis/archive/refs/heads/main.zip) o a través de Git con el comando:

```shell
git clone https://github.com/redd-costarica-scripts/redd-costarica-scripts-qgis.git
```

El directorio resultante debe ser ubicado en el directorio de complementos de QGIS (ej. `D:\Users\mfvargas\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`).

Luego, debe instalar el complemento con la opción de menú `Complementos - Manejar e instalar complementos` de QGIS.