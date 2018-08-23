Evident
=======

|Build Status| |Coverage Status|

# E-vident: elucidating sampling effort for microbial analysis studies

A critical consideration in any clinical study is power analysis, yet it has been difficult to perform such analyses for microbiome studies because the effect sizes of different disorders are unknown. Fortunately, several larger cohort studies, including but not limited to the Human Microbiome Project, now allow us to identify effect sizes for differences among ages and populations, and differences associated with obesity, IBD, and other disorders.

Evident is a web-based software tool with an interactive user interface, implemented in HTML, Web Graphics Library, mod_python and Quantitative Insights Into Microbial Ecology ([QIIME][]). The interface of E-vident (Fig. 1) is comprised of: (i) the selection of parameters (i.e., study of interest, number of sequences per sample, the number of samples to use, and the number of iterations); (ii) the kind of visualizations to generate (Demo PCoA shows the original results from the study, and PCoA recalculates the study using the user-defined parameters in (i); (iii) the WebGL plot display.

![Imgur](http://i.imgur.com/seMQ0.png)

*Figure 1*. E-vident GUI. (i) Selectors for study, sequences per sample, number of subjects, samples per subject and number of iteration; (ii) Analysis Menu: Demo (view original study results), PCoA plots and alpha rarefaction plots; (iii) Output area showing the webGL PCoA plot.
 
[QIIME]: https://github.com/qiime/qiime


.. |Build Status| image:: https://travis-ci.org/biocore/Evident.svg
   :target: https://travis-ci.org/biocore/Evident
.. |Coverage Status| image:: https://coveralls.io/repos/biocore/Evident/badge.svg
   :target: https://coveralls.io/r/biocore/Evident

