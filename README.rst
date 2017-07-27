**sankeyview** takes a database of flow data and transforms it into a Sankey
diagram. It implements the approach described in the paper `Hybrid Sankey diagrams: Visual analysis of multidimensional data for understanding resource use <https://doi.org/10.1016/j.resconrec.2017.05.002>`_.

Example: `Fruit - complete example.ipynb <http://nbviewer.jupyter.org/github/ricklupton/sankeyview/blob/master/examples/Fruit%20-%20complete%20example.ipynb>`_

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.161970.svg

Installation
------------

Since sankeyview depends on pandas and numpy, it's easiest to install those
using `Anaconda or Miniconda <https://www.continuum.io/downloads>`_.

Then install sankeyview using pip:

.. code-block:: console

   pip install sankeyview


Jupyter notebook
----------------

To use with the Jupyter notebook, the `ipysankeywidget
<https://github.com/ricklupton/ipysankeywidget>`_ package is also needed.
