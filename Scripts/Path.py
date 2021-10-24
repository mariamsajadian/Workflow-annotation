# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 08:15:51 2020
Script to compute semantic similarity in an OWL ontology. Reads the ontology, extracts rdfs:subClassOf statements,
turns it into a tree defined by a root node (note: not unique, so changes randomly), and computes similarity measures based on least-common subsumer (LCS)
@original author core functions: Schei008 (adapted by other user)



@Adapted by Eric

Sorry for the messy code. It will probably be difficult to get it to work like this. If you want to try out the code,
let me know and I will make some time to explain how to run the code.
"""

import rdflib
from rdflib.namespace import RDFS, RDF, OWL
from rdflib import BNode
import os

from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from rdflib.tools import rdf2dot

#-------------------------------------------------------------------------------------------------
# FUNCTIONS
#-------------------------------------------------------------------------------------------------

def load_rdf(g, rdffile, format='turtle'):
    # #print("load_ontologies")
    # #print("  Load RDF file: "+fn)
    g.parse(rdffile, format=format)
    n_triples(g)
    return g

def n_triples(g, n=None):
    """ #prints the number of triples in graph g """
    if n is None:
        #print(('  Triples: ' + str(len(g))))
        n
    else:
        #print(('  Triples: +' + str(len(g) - n)))
        n
    return len(g)

def shortURInames(URI):
    #return URI
    if URI is None:
        return None
    if "#" in URI:
        return URI.split('#')[1]
    else:
        #return os.path.basename(os.path.splitext(URI)[0])
        return URI.split('/')[-1].split('.')[0]

"""This method takes some ontology in Turtle and returns a taxonomy (consisting only of rdfs:subClassOf statements)"""
def cleanOWLOntology(ontologyfile='CoreConceptData.ttl'):  # This takes the combined types version as input
    #print('Clean OWL ontology!')
    ccdontology = load_rdf(rdflib.Graph(), ontologyfile)
    taxonomy = rdflib.Graph()
    #print('Extracting subClassOf triples:')
    taxonomy += ccdontology.triples((None, RDFS.subClassOf, None))  # Keeping only subClassOf statements and classes
    taxonomy += ccdontology.triples((None, RDF.type, OWL.Class))
    n_triples(taxonomy)
    #print('Cleaning blank node triples and loops, as well as nodes intersecting more than 1 dimenion')
    taxonomyclean = rdflib.Graph()
    for (s, p, o) in taxonomy:  # Removing triples that stem from blanknodes as well as loops
        if type(s) != BNode and type(o) != BNode:
            if s != o and s != OWL.Nothing:
                # if p==RDFS.subClassOf: #Removing nodes intersecting with more or less than one of the given dimensions
                #   if testDimensionality(s,dimnodes,taxonomy)==1:
                taxonomyclean.add((s, p, o))

    n_triples(taxonomyclean)
    return taxonomyclean

"""Measures the size of a taxonomy's set of nodes and detects leaf nodes"""
def measureTaxonomy(g):
    leafnodes = set()
    nodes = list(g.subjects(predicate=RDFS.subClassOf, object=None))
    count = 0
    for node in nodes:
        count += 1
        if not (None, RDFS.subClassOf, node) in g:
            leafnodes.add(node)
    #print("size of taxonomy without roots: " + str(count))
    #print("leafnodes: " + str([shortURInames(l) for l in leafnodes]))
    return (nodes, leafnodes)

def visualize(taxonomy):
    G = rdflib_to_networkx_multidigraph(taxonomy)

    # Plot Networkx instance of RDF Graph
    pos = nx.spring_layout(G, scale=2)
    edge_labels = {}
    #print(pos)
    for i, val in pos.items():
        edge_labels.update({i: shortURInames(i)})
        #print(shortURInames(i))
    #print(pos)
    #print(edge_labels)
    #nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
    nx.draw(G, font_size=10, edge_color='lightblue',with_labels=True, labels=edge_labels, node_color='yellow')
    plt.show()

"""This method takes a taxonomy (a graph of raw subsumption relations) and an arbitrary root and generates 
a tree with unique parent relations towards the root for each node. Uses rdflib's built in get_tree. Note: not unique!"""
def getSubsumptionTree(g, root, leafnodes):
    print("Root node: " + root)
    tuplelisttree = rdflib.util.get_tree(g, root, RDFS.subClassOf)
    #print("tuplelisttree", tuplelisttree)
    nodedepth = {}
    parent = {}
    visitednodes = set()

    """
    # Visualize tree
    with open('decision.dot', 'w+') as stream:
        rdflib.tools.rdf2dot.rdf2dot(g, stream)
    """

    depth = 1  # Root node has depth 1
    tuple = tuplelisttree
    #print(tuplelisttree)
    # This traverses the tree to generate depth and parent dictionaries
    traverse(tuple, depth, nodedepth, parent, visitednodes)

    #print("size of tree: " + str(len(nodedepth.keys())))
    depth = max(nodedepth.values())
    #print("depth of tree: " + str(depth))
    # This #prints out the path to the root for each visited leafnode, just to test the method
    for n in leafnodes.intersection(visitednodes):
        #print(nodedepth[n])
        #print(n)
        backtrack(parent, n)
    return (nodedepth, parent)

def traverse(tuple, depth, nodedepth, parent, visitednodes):
    current = tuple[0]
    nodedepth[current] = depth
    visitednodes.add(current)
    for child in tuple[1]:
        parent[child[0]] = current
        traverse(child, depth + 1, nodedepth, parent, visitednodes)

def backtrack(parent, leaf):
    node = leaf
    while node in parent.keys() and node is not None:
        node = parent[node]
        #print(shortURInames(node))

"""Computes the least common subsumer  for two concepts in a given taxonomy tree"""
def LCS(parent, c1, c2):
    #print("Getting LCS of " + shortURInames(c1) + " and " + shortURInames(c2) + "... ")
    node1 = c1
    #print("nodes are: ")
    #print(c1, c2)
    while node1 in parent.keys() and node1 is not None:
        node2 = c2
        while node2 in parent.keys() and node2 is not None:
            if node1 == node2:
                return node1
                break
            node2 = parent[node2]
        node1 = parent[node1]
    return None

"""Simple path-based similarity measure"""
def pathSim(nodedepth, parent, c1, c2):
    #print("\n Measuring path distance between " + shortURInames(c1) + " and " + shortURInames(c2))
    lcs = LCS(parent, c1, c2)
    #print("LCS is: " + str(lcs))
    #print(shortURInames(lcs) + " pathSim2")
    dc1 = nodedepth[c1]
    #print("Depth of " + shortURInames(c1) + ": " + str(dc1))
    dc2 = nodedepth[c2]
    #print("Depth of " + shortURInames(c2) + ": " + str(dc2))
    #print("Depth of " + shortURInames(lcs) + ": " + str(nodedepth[lcs]))
    return (dc1 - nodedepth[lcs]) + (dc2 - nodedepth[lcs])

"""Wu Palmer similarity measure"""
def wupalmer(nodedepth, parent, c1, c2):
    #print("\n Measuring path distance between " + shortURInames(c1) + " and " + shortURInames(c2))
    lcs = LCS(parent, c1, c2)
    if lcs == None:
        return "No LCS"
    #print("LCS: " + shortURInames(lcs) + " (WuPalmer)")
    distance = (nodedepth[c1] - nodedepth[lcs]) + (nodedepth[c2] - nodedepth[lcs])
    wp = (2 * nodedepth[lcs]) / (distance + 2 * nodedepth[lcs])
    return wp

#-------------------------------------------------------------------------------------------------
# GRAPH SETUP
#-------------------------------------------------------------------------------------------------

"""Namespaces General"""
CCD = rdflib.Namespace("http://geographicknowledge.de/vocab/CoreConceptData.rdf#")
TOOLS = rdflib.Namespace("http://geographicknowledge.de/vocab/GISTools.rdf#")
WF = rdflib.Namespace("http://geographicknowledge.de/vocab/Workflow.rdf#")
rdfs = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")

"""Namespaces ARCGIS"""
ARCGIS_SA = rdflib.Namespace("https://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/")
ARCGIS_FEAT = rdflib.Namespace("https://pro.arcgis.com/en/pro-app/tool-reference/feature-analysis/")
ARCGIS_CON = rdflib.Namespace("https://pro.arcgis.com/en/pro-app/tool-reference/conversion/")
ARCGIS_3D = rdflib.Namespace("https://pro.arcgis.com/en/pro-app/tool-reference/3d-analyst/")
ARCGIS_IMG = rdflib.Namespace("https://pro.arcgis.com/en/pro-app/tool-reference/image-analyst/")
ARCGIS_DATA = rdflib.Namespace("https://pro.arcgis.com/en/pro-app/tool-reference/data-management/")
ARCGIS_ANA = rdflib.Namespace("https://pro.arcgis.com/en/pro-app/tool-reference/analysis/")

"""Namespaces QGIS"""
QGIS_OVERLAY = rdflib.Namespace("https://docs.qgis.org/testing/en/docs/user_manual/processing_algs/qgis/vectoroverlay.html#")
QGIS_GEOM = rdflib.Namespace("https://docs.qgis.org/testing/en/docs/user_manual/processing_algs/qgis/vectorgeometry.html#")
QGIS_GENERAL = rdflib.Namespace("https://docs.qgis.org/3.10/en/docs/user_manual/processing_algs/qgis/vectorgeneral.html#")
QGIS_SAGA = rdflib.Namespace("http://www.saga-gis.org/saga_tool_doc/6.3.0/")
QGIS_RASTER = rdflib.Namespace("https://docs.qgis.org/testing/en/docs/user_manual/processing_algs/qgis/rasteranalysis.html#")
QGIS_GDAL = rdflib.Namespace("https://docs.qgis.org/3.10/en/docs/user_manual/processing_algs/gdal/rasterextraction.html#")

# Function that checks if string in URIs exists
def GIS(string, number=1):
    GISs = [ARCGIS_3D, ARCGIS_ANA, ARCGIS_CON, ARCGIS_DATA, ARCGIS_FEAT, ARCGIS_IMG, ARCGIS_SA,
            QGIS_OVERLAY, QGIS_GEOM, QGIS_GENERAL, QGIS_SAGA, QGIS_RASTER, QGIS_GDAL]
    for URI in full_URIs:
        for GIS in GISs:
            if GIS[string + '.htm'] in URI and GIS[string + '.html'] not in URI:
                return GIS[string + '.htm']
            if GIS[string + '.html'] in URI and GIS == QGIS_SAGA:
                return GIS[string + '.html']
            if GIS[string] in URI:
                return GIS[string]


        #print(URI)
    raise Exception('No match found', number)

#-------------------------------------------------------------------------------------------------
# COMPARISON OF TOOLS
#-------------------------------------------------------------------------------------------------

"""Graphs"""
# Create base graphs and

graph = rdflib.Graph()
CoreConcepts = rdflib.Graph()
load_rdf(CoreConcepts, 'CoreConceptData.ttl')
tools_base = rdflib.Graph()
load_rdf(tools_base, 'D:\ontology/New_rdfs\ArcGIS_1.ttl')
load_rdf(tools_base, 'D:\ontology/New_rdfs\QGIS_1.ttl')

full_URIs = set()
inputs = set()
outputs = set()
inputs_outputs = set()
tools = rdflib.Graph()

# Get URIs -> input/output
for (s, p, o) in tools_base:
    if p != rdfs.label and type(s) != BNode:
        full_URIs.add(s)
        graph.add((s, p, o))
        graph.add((s, RDFS.subClassOf, o))

# Get input/output -> CCD ontology relations
for (s, p, o) in tools_base:
    if type(s) is BNode:
        graph.add((s, RDFS.subClassOf, o))

short_URIs = []
for i in full_URIs:
    short_URIs.append(shortURInames(i))

# First get a taxonomy of subsumption relations
taxonomy = cleanOWLOntology("CoreConceptData.ttl")
# Get leafnodes
(nodes, leafnodes) = measureTaxonomy(taxonomy)
# Turn taxonomy into a tree
(nodedepth, parent) = getSubsumptionTree(taxonomy, CCD.Attribute, leafnodes)
# measure similarity  between nodes in tree

CCD_geom = (CCD.RasterA, CCD.LineA, CCD.PointA, CCD.PlainVectorRegionA, CCD.VectorTessellationA)
CCD_scale = (CCD.NominalA, CCD.OrdinalA, CCD.IntervalA, CCD.RatioA, CCD.CountA, CCD.BooleanA)
CCD_qual = (CCD.FieldQ, CCD.ObjectQ, CCD.NetworkQ, CCD.EventQ)

# -- This function is probably way too complex
def getLowestDistance(nodedepth, parent, c1, c2_list):
    node2_1 = c2_list[0]
    pathsim1 = pathSim(nodedepth, parent, c1, node2_1)

    pathsim2 = 1000000
    if len(c2_list) >= 2:
        node2_2 = c2_list[1]
        pathsim2 = pathSim(nodedepth, parent, c1, node2_2)

    pathsim3 = 1000000
    if len(c2_list) >= 3:
        node2_3 = c2_list[2]
        pathsim3 = pathSim(nodedepth, parent, c1, node2_3)

    nearestNode2 = node2_1
    if pathsim2 < pathsim1:
        nearestNode2 = node2_2
    if pathsim3 < pathsim1 and pathsim3 < pathsim2:
        nearestNode2 = node2_3
    return nearestNode2

def getTotalDistance(nodedepth, parent, c1_list, c2_list):
    pathsim_geom = pathSim(nodedepth, parent, c1_list[0], c2_list[0])
    pathsim_scale = pathSim(nodedepth, parent, c1_list[1], c2_list[1])
    pathsim_qual = pathSim(nodedepth, parent, c1_list[2], c2_list[2])
    return pathsim_geom + pathsim_scale + pathsim_qual

#print(getLowestDistance(nodedepth, parent, CCD.NominalA, (CCD.IntervalA, CCD.RatioA, CCD.CountA)))
#exit()
#
#print(tool_1, tool_2)
#print(shortURInames(tool_1), shortURInames(tool_2))

def CCD_wp(tool_1, tool_2, in_out, graph=graph, input_linking=False):
    while True:
        try:
            # -- in_out represents the predicate determining whether it is input 1-3 or output in the RDF
            # -- When input_linking is True, the script will try to link each input in function 1 to each input in function 2.
            #    If False, each input in function 1 will be linked to the closest input in function 2.

            LCS_geom = 1000000
            LCS_scale = 1000000
            LCS_qual = 1000000

            node2_geom_list = []
            node2_scale_list = []
            node2_qual_list = []

            node1_geom = None
            node1_scale = None
            node1_qual = None

            node2_geom = None
            node2_scale = None
            node2_qual = None

            node2_geom_1 = None
            node2_geom_2 = None
            node2_geom_3 = None

            node2_scale_1 = None
            node2_scale_2 = None
            node2_scale_3 = None

            node2_qual_1 = None
            node2_qual_2 = None
            node2_qual_3 = None

            input2 = False
            input3 = False

            node2_1_dist = 0
            node2_2_dist = 0
            node2_3_dist = 0

            if in_out == WF.output:
                input_linking == True
            for (s, p, o) in graph:
                if s in graph.objects(GIS(tool_1), in_out):
                    if o in CCD_geom:
                        node1_geom = o
                    elif o in CCD_scale:
                        node1_scale = o
                    elif o in CCD_qual:
                        node1_qual = o
                if input_linking:
                    if s in graph.objects(GIS(tool_2), in_out):
                        if o in CCD_geom:
                            node2_geom = o
                        elif o in CCD_scale:
                            node2_scale = o
                        elif o in CCD_qual:
                            node2_qual = o
                elif s in graph.objects(GIS(tool_2), WF.input1):
                    if o in CCD_geom:
                        node2_geom_1 = o
                    elif o in CCD_scale:
                        node2_scale_1 = o
                    elif o in CCD_qual:
                        node2_qual_1 = o
                elif s in graph.objects(GIS(tool_2), WF.input2):
                    if o in CCD_geom:
                        node2_geom_2 = o
                        input2 = True
                    elif o in CCD_scale:
                        node2_scale_2 = o
                    elif o in CCD_qual:
                        node2_qual_2 = o
                elif s in graph.objects(GIS(tool_2), WF.input3):
                    if o in CCD_geom:
                        node2_geom_3 = o
                        input3 = True
                    elif o in CCD_scale:
                        node2_scale_3 = o
                    elif o in CCD_qual:
                        node2_qual_3 = o

            if not input_linking:
                node1_list = [node1_geom, node1_scale, node1_qual]
                node2_1_list = [node2_geom_1, node2_scale_1, node2_qual_1]
                node2_2_list = [node2_geom_2, node2_scale_2, node2_qual_2]
                node2_3_list = [node2_geom_3, node2_scale_3, node2_qual_3]
                print(node2_1_list)
                print(node2_2_list)
                print(node2_3_list)

                node2_1_dist = getTotalDistance(nodedepth, parent, node1_list, node2_1_list)
                if input2:
                    node2_2_dist = getTotalDistance(nodedepth, parent, node1_list, node2_2_list)
                if input3:
                    node2_3_dist = getTotalDistance(nodedepth, parent, node1_list, node2_3_list)
                if (node2_1_dist <= node2_2_dist and node2_1_dist <= node2_3_dist) or (input2 == False and input3 == False):
                    node2_geom = node2_geom_1
                    node2_scale = node2_scale_1
                    node2_qual = node2_qual_1
                elif (node2_2_dist <= node2_1_dist and node2_2_dist <= node2_3_dist) or input3 == False:
                    node2_geom = node2_geom_2
                    node2_scale = node2_scale_2
                    node2_qual = node2_qual_2
                elif node2_3_dist <= node2_1_dist and node2_3_dist <= node2_2_dist:
                    node2_geom = node2_geom_3
                    node2_scale = node2_scale_3
                    node2_qual = node2_qual_3

            wp_geom = wupalmer(nodedepth, parent, node1_geom, node2_geom)
            wp_scale = wupalmer(nodedepth, parent, node1_scale, node2_scale)
            wp_qual = wupalmer(nodedepth, parent, node1_qual, node2_qual)

            print(wp_geom )
            print(wp_scale)
            print(wp_qual )

            wp_total = (wp_geom + wp_scale + wp_qual) / 3
            print('tool 1:', tool_1, 'tool 2:', tool_2, 'input or output:', shortURInames(in_out))
            print('wp_total:', wp_total)
            print('wp_geom:', wp_geom, 'node 1:', shortURInames(node1_geom), 'node 2:', shortURInames(node2_geom))
            print('wp_scale:', wp_scale, 'node 1:', shortURInames(node1_scale), 'node 2:', shortURInames(node2_scale))
            print('wp_qual:', wp_qual, 'node 1:', shortURInames(node1_qual), 'node 2:', shortURInames(node2_qual))
            return [tool_1, GIS(tool_1), tool_2, GIS(tool_2), shortURInames(in_out), in_out,
                    wp_total, wp_geom, wp_scale, wp_qual,
                    shortURInames(node1_geom), shortURInames(node2_geom),
                    shortURInames(node1_scale), shortURInames(node2_scale),
                    shortURInames(node1_qual), shortURInames(node2_qual)]
        except:
            print([shortURInames(tool_1), shortURInames(tool_2), in_out], 'Erroneous taxonomy')
            return [shortURInames(tool_1), tool_1, shortURInames(tool_2), tool_2, in_out]


#tool_1 = 'grid_analysis_0'

#if GIS(tool_1) in graph.subjects(predicate=WF.input1):
#    CCD_wp(tool_1, 'buffer', WF.input1, input_linking=False)
#if GIS(tool_1) in graph.subjects(predicate=WF.input2):
#    CCD_wp(tool_1, 'buffer', WF.input2, input_linking=False)
#if GIS(tool_1) in graph.subjects(predicate=WF.input3):
#    CCD_wp(tool_1, 'buffer', WF.input3, input_linking=False)
#CCD_wp(tool_1, 'buffer', WF.output, input_linking=True)

QGIS = (
#    'grid_analysis_0',
#'grid_analysis_5',
#'grid_filter_6',
#'grid_gridding_10',
#'grid_tools_26',
#'clip-raster-by-mask-layer',
#'merge-vector-layers',
#'raster-surface-volume',
#'reclassify-by-table',
'zonal-statistics',
'polygonize',
'qfbuffer',
'qobuffer',
'ffqgisclip',
'foqgisclip',
'ofqgisclip')

ArcGIS = ('surface-volume',
'afbuffer',
'aobuffer',
'ffclip',
'foclip',
'ofclip',
'polyline-to-raster',
'raster-to-polygon',
'join-field',
'merge-layers',
'raster-calculator',
'con-',
'cost-distance',
'cost-path',
'euclidean-distance',
'extract-by-mask',
'majority-filter',
'reclassify',
'weighted-overlay',
'zonal-statistics-as-table')

cols = ['tool_1', 'tool_1_URI', 'tool_2', 'tool_2_URI', 'in_out', 'in_out_URI',
        'wp_total', 'wp_geom', 'wp_scale', 'wp_qual',
        'node1_geom', 'node2_geom',
        'node1_scale', 'node2_scale',
        'node1_qual', 'node2_qual']

count = 0
wp_list = []
ArcGIS = ['reclassify']
#QGIS = ['zonal-statistics']
for tool_1 in QGIS:
    wp_list = []
    for tool_2 in ArcGIS:
        print(tool_1, tool_2)
        #print(shortURInames(tool_1), shortURInames(tool_2))
        if GIS(tool_1) in graph.subjects(predicate=WF.input1):
            wp_list.append(CCD_wp(tool_1, tool_2, WF.input1, input_linking=False))
        if GIS(tool_1) in graph.subjects(predicate=WF.input2):
            wp_list.append(CCD_wp(tool_1, tool_2, WF.input2, input_linking=False))
        if GIS(tool_1) in graph.subjects(predicate=WF.input3):
            wp_list.append(CCD_wp(tool_1, tool_2, WF.input3, input_linking=False))
        wp_list.append(CCD_wp(tool_1, tool_2, WF.output, input_linking=True))
    df = pd.DataFrame(wp_list, columns=cols)
    df.to_csv('resultsQGIS_reclassify_reclassify.csv', mode='a', header=False)


#        for (s, p, o) in graph:
#            if s in graph.objects(tool_1, RDFS.subClassOf):
#                print(s, p, o)
#                #print('success')
#
#       # print(wupalmer(nodedepth, parent, GIS(shortURInames(tool_1)), GIS(shortURInames(tool_2), 2)))

#-------------------------------------------------------------------------------------------------
# WRITE TO FILE
#-------------------------------------------------------------------------------------------------






