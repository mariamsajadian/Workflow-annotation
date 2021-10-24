# Workflow-annotation
This work investigated the functional similarity of GIS software packages by assessing the generalization effectiveness of the Core Concept Datatype (CCD) ontology.
More precisely, A GIS tool can be considered a GI-function which takes a certain input, transforms it, and returns an output. A workflow is then considered a sequence
of functions and their inputs and outputs. This sequence of functions can be varied in different software packages and may be defined differently by GIS experts.
The research pursues to find an answer to the question:

To what extent can the semantic values of data inputs and outputs be used to generalize the functionality of tools and workflows in different GIS-software environments?

The research question is broken down into the following sub-questions:

1)	From a conceptual perspective, what is the relation between GIS-tools and workflows? 
2)	How contentious is the interpretation of the semantics of inputs and outputs when using the CCD ontology?
3)	To what extent do the semantics of data inputs and outputs of tools cover the semantically significant characteristics of GIS-tools? 
4)	To what extent can the CCD ontology be used to assess the similarity and equivalence of workflows?


To answer this question, the research was conducted in five steps. First, scenarios are defined for the collection of a dataset of geo-operators five sets of workflows are
derived from five scenarios using two GIS software environments, namely ArcGIS Pro and QGIS. Each scenario focuses on answering a spatial-analytical research question. The
scenarios revolved around the following five questions:

•	Which places have a high risk of air pollution in the Randstad region?
•	Where are the best places to build schools?
•	How much sediment has been accumulated in the land?
•	What is the greenness score for cycling or walking in Enschede?
•	Which areas are low-lying lands? And Which areas might be affected by flood when hit by a storm?

These scenarios were brock down into several steps. Fore example, here is a spatial question for scenario 4:

What is the greenness score for cycling or walking in Enschede?

In this scenario, we wish to generate a raster road map that shows the greenness score calculated based on NDVI. The datasets needed for this scenario consists
of Enschede roads polyline and the NDVI raster. The steps in the scenario are:

•	Create the source dataset as the starting point of the route, destination dataset as the ending point of the route.

•	Turn road vector data into raster by using Polyline to Raster tool. The road as value 1, outside of the road will be no data. (note that cell size needs to bigger
than NDIV cell size)

•	Create the cost dataset by multiplying NDVI and Road raster using the Raster calculator.

•	Perform cost distance analysis using the source (file name: Source) and cost datasets as inputs. The distance dataset created from this tool is a raster in which
the value of each cell is the accumulated cost of traveling from each cell back to the source.

•	Find the least-cost path by using the Cost Path tool. Input destination (file name: destination).

In the next phase, The results of the five scenarios were wrapped in RDF files using various vocabularies (please see RDFs folder). The vocabularies are used for the construction
of workflows to describe specific provenance contexts such as agents, datasets, and tools; however, there is a lack of generalization over types of input and output data and
spatial concepts, such as objects, fields, and networks. These concepts allow datasets used in the workflow chains to be logically described by analytic tools. Besides, users 
can formulate their questions that can be translated into meaningful queries based on these concepts. The concepts, which are considered as the core commutations between operations,
are usable in different application domains. Then, the accuracy of the annotation is analyzed using inter-annotator agreement measures based on adjusted agreement coefficients. 
The inter-annotator agreement is captured based on a statistical model to evaluate the accuracy of CCD ontology annotated in tools RDF files and an analysis of the equivalence
between tools and between workflows (please see Python codes in Scripts folder). Finally, the similarity between tools and between workflows is evaluated using an aggregation of
the Wu-Palmer metric.

To conclude:
The first question is: From a conceptual perspective, what is the relation between GIS-tools and workflows? Although the definitions of GIS-tools and workflows are subject to
scientific debate, an answer to this question can be formulated with the help of the literature in the theoretical background. A definition for GIS-tools is offered by Brauner
(2015), who regards them as functions or pieces of software, which have a purpose for geospatial analysis or transformation. However, to fully understand the purpose of a tool,
it may not be sufficient to consider the tool in isolation. Rather, the tool should be considered in the context of its software environment. Most GIS-tools are offered in
software packages, like ArcGIS and QGIS. These packages have a general purpose. For example, they may aim to be versatile, easy-to-use, comprehensive, or specialized in some way.
Whatever their specific aims may be, all GIS packages have the purpose of providing functionality to their users in a certain way. As a result, the purpose of a GIS-tool is 
inextricably connected to the purpose of its corresponding software environment. It can be expected that developers of GIS-packages would want their GIS-tools to be
interoperable, but they may not necessarily pursue interoperability beyond the confinements of their own software environment. 
A GIS-workflow is generally thought of as an ordered set of GIS-operations which leads to a certain outcome. A GIS-tool can then be considered one of the operations within this 
workflow. However, as argued in the last paragraph, the purpose of a GIS-tool is connected to its corresponding software environment. Workflows are not bounded to one software 
environment, but could involve steps from different GIS-packages. The objective of a workflow is to go from a certain starting point to a certain outcome. To reach this 
objective, the purposes of the GIS-tools need to be realigned in accordance, which may be harder for GIS-tools from different software packages. To answer the question, the 
relation between GIS-tools and workflows is simple. A GIS-tool can be part of a GIS-workflow. However, how a GIS-tool becomes a part of a workflow is more complex and depends on
the workflow’s purpose, the other tools in the workflow, and their respective software environments.

The second subquestion is: How contentious is the interpretation of inputs and outputs using the CCD ontology? Given the inter-annotator agreement, it can be said that the 
interpretation is for some semantic categories quite contentious. As can be concluded from the interpretation of the inter-annotator agreement measures in subsection 5.1.3, 
the agreement is high at the geometric property level, middle-high at the core concept quality level, and low at the measurement level. This implies that the annotators had 
the biggest trouble with the measurement levels. 

The third subquestion is: To what extent do the semantics of data inputs and outputs of tools cover the semantically significant characteristics of GIS-tools? The similarity 
analysis in section 5.2 shows that the inputs and outputs mark up a decent share of the semantic similarity between GIS-tools. The recommendation system performs especially 
well when the recommendation requirement is relaxed to a top three or top five of possibly equivalent tools. However, the recommendation system is not so concise that it can 
pinpoint the exact equivalent tool. Given the limited space of variety with only the three concept categories of the inputs and outputs, it may be necessary to link additional 
information to the GIS-tools themselves. This could for example be information about the nature of the transformation, assumptions about the data implicit in the function, and 
a specification of the parameters. The software environment could also be considered as a source of information about possible interoperability relations, but this would require
further research.

The fourth and final subquestion is: To what extent can the CCD ontology be used to assess the similarity and equivalence of workflows? In this study, the semantic similarity of
workflows is only conceptualized as the numbers of occurrences of semantic concepts within said workflows. Naturally, a workflow is more complex. The directionality between the
steps in the workflows should be taken into account, as well as the equivalence of the outcomes. A workflow may be highly similar to another workflow, but not equivalent, 
because the outcome is different, which means the workflows are not interchangeable. Based on this study, the question has to remain unanswered. It can be said that considering 
the number of occurrences may provide new insights, but it cannot be determined whether deeper insights can be gained. 
