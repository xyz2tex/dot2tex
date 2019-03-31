#!/usr/bin/env python
import unittest

import dot2tex.dotparsing as dotp


class DotNodeTest(unittest.TestCase):
    def test_create(self):
        node = dotp.DotNode("a")
        self.assertEqual(node.name, "a")
        self.assertEqual(len(node.attr), 0)

    def test_createwithattributes(self):
        node = dotp.DotNode("a", label='a_1', style='filled')
        self.assertEqual(node.name, "a")
        self.assertEqual(len(node.attr), 2)
        self.assertEqual(node.attr['label'], 'a_1')
        self.assertEqual(node.attr['style'], 'filled')

    def test_createwithdict(self):
        attr = dict(label="a_1", style='filled')
        node = dotp.DotNode("a", **attr)
        self.assertEqual(len(node.attr), 2)
        self.assertEqual(node.attr['label'], 'a_1')
        self.assertEqual(node.attr['style'], 'filled')

    def test_createwithdictandnamed(self):
        attr = dict(label="a_1", style='filled')
        node = dotp.DotNode("a", texmode="math", **attr)
        self.assertEqual(len(node.attr), 3)
        self.assertEqual(node.attr['label'], 'a_1')
        self.assertEqual(node.attr['style'], 'filled')
        self.assertEqual(node.attr['texmode'], 'math')

    def test_cmp(self):
        node = dotp.DotNode("a")
        self.assertEqual(node.name, "a")
        self.assertEqual(node, 'a')


class DotGraphTest(unittest.TestCase):
    def test_create(self):
        g = dotp.DotGraph('mygraph', strict=False, directed=True)
        self.assertEqual(g.name, "mygraph")
        self.assertEqual(g.strict, False)
        self.assertEqual(g.directed, True)

    def test_create_with_attributes(self):
        g = dotp.DotGraph(style='fancy', label='testgraph')
        self.assertEqual(len(g.attr), 2)
        self.assertEqual(g.attr['style'], 'fancy')
        self.assertEqual(g.attr['label'], 'testgraph')


    def test_add_node(self):
        g = dotp.DotGraph()
        na = g.add_node('a')
        nb = g.add_node('b')
        self.assertEqual(len(list(g.nodes)), 2)

    ##
    def test_addequalnodes(self):
        g = dotp.DotGraph()
        g.add_node('a', label="test1")
        g.add_node('a', style="filled")
        g.add_node('a', label="test2", texmode="math")
        n = g.get_node('a')
        self.assertEqual(len(list(g.nodes)), 1)
        self.assertEqual(len(n.attr), 3)
        self.assertEqual(n.attr['label'], 'test2')
        self.assertEqual(set(n.attr.keys()), set(['label', 'style', 'texmode']))

    def test_add_nonstring_nodes(self):
        g = dotp.DotGraph()
        n = g.add_node(1)
        self.assertEqual(n.name, '1')
        n = g.add_node(3.14)
        self.assertEqual(n.name, '3.14')

    def test_add_edge(self):
        g = dotp.DotGraph()
        e = g.add_edge('a', 'b', label='test')
        e2 = g.add_edge('a', 'd', label='test2')
        self.assertEqual(len(g), 3)
        self.assertEqual(len(g.edges), 2)


class DotSubgraphsTest(unittest.TestCase):
    def test_add_subgraph(self):
        g = dotp.DotGraph()
        s = g.add_subgraph('subG')
        self.assertEqual(s.name, 'subG')

    def test_add_edge_to_subgraph(self):
        g = dotp.DotGraph()
        s = g.add_subgraph('subG')
        self.assertEqual(len(g), 0)
        s.add_edge(1, 2)
        self.assertEqual(len(s), 2)
        self.assertEqual(len(g), 2)
        g.add_edge(3, 4)
        self.assertEqual(len(s), 2)
        self.assertEqual(len(g), 4)


class DotDefaultAttrTest(unittest.TestCase):
    """Test default attributes"""

    def test_add_default(self):
        g = dotp.DotGraph()
        g.add_default_node_attr(color="red", label="a")
        self.assertEqual(len(g.default_node_attr), 2)
        g.add_default_edge_attr(color="red")
        self.assertEqual(len(g.default_edge_attr), 1)
        g.add_default_graph_attr(color="red")
        self.assertEqual(len(g.default_graph_attr), 1)

    def test_add_default_node(self):
        g = dotp.DotGraph()
        g.add_default_node_attr(color="red")
        n = g.add_node('a')
        self.assertTrue('color' in n.attr)
        self.assertEqual(n.attr['color'], "red")
        g.add_default_node_attr(color="blue", label="b")
        n = g.add_node(2)
        self.assertTrue('color' in n.attr)
        self.assertEqual(n.attr['color'], "blue")
        self.assertTrue('label' in n.attr)
        self.assertEqual(n.attr['label'], "b")

    def test_add_default_node_subgraph(self):
        g = dotp.DotGraph()
        g.add_default_node_attr(color="red")
        g.add_node('a')
        s = g.add_subgraph('S')
        s.add_default_node_attr(style='test')
        n = s.add_node('b')
        self.assertTrue('color' in n.attr)
        self.assertEqual(n.attr['color'], "red")
        self.assertTrue('style' in n.attr)
        nn = g.add_node(2)
        self.assertFalse('style' in nn.attr)


##
##
##    def test_addequalnodes2(self):
##        g = dotp.DotGraph()
##        n = dotp.DotNode('a',label="test1")
##        g.add_node(n)
##        n = dotp.DotNode('a',style="filled")
##        g.add_node(n)
##        g.add_node('a',label="test2",texmode="math")
##        n = g.get_node('a')
##        self.assertEqual(len(g.nodes),1)
##        self.assertEqual(len(n.attributes),3)
##        self.assertEqual(n.attributes['label'],'test2')
##        self.assertEqual(set(n.attributes.keys()),set(['label','style','texmode']))
##
##    def test_getnodes(self):
##        g = dotp.DotGraph()
##        n = g.get_node('a')
##        self.assertEqual(n,None)
##        g.add_node('a')
##        n = g.get_node('a')
##        self.assertEqual(n.name,'a')
##
##    def test_addedge(self):
##        g = dotp.DotGraph(graph_type='digraph')
##        e1 = g.add_edge('a','b',label='a->b')
##        e2 = g.add_edge('b','a',label='b->a')
##        self.assertEqual(len(g.nodes),2)
##        self.assertEqual(len(g.edges),2)
##        self.assertEqual(e1.attributes['label'],'a->b')
##        self.assertEqual(e2.attributes['label'],'b->a')
##
##
##
##
##
##
##    def test_strictgraph(self):
##        """A strict graph have to ignore duplicate edges"""
##        g = dotp.DotGraph(strict=True)
##        g.add_edge('a','b')
##        g.add_edge('a','b')
##        self.assertEqual(len(g.edges),1)
##
##    def test_addsubgraphs(self):
##        g = dotp.DotGraph()
##        g.add_edge('a','b')
##        n = g.get_node('a')
##        self.assertEqual(n.parent,g)
##        gs = g.add_subgraph('clusterG')
##        gs.add_edge('a','b')
##        #n = g.get_node('a')
##        self.assertEqual(n.parent,gs)
##        n = g.add_node('a',label="test")
##
##        self.assertEqual(n.parent,gs)
##
##    def test_graphlevels(self):
##        g = dotp.DotGraph()
##        e = g.add_edge('a','b')
##        self.assertEqual(g.level,0)
##        gs1 = g.add_subgraph('clusterG')
##        self.assertEqual(gs1.level,1)
##        gs2 = g.add_subgraph('clusterGG')
##        self.assertEqual(gs2.level,1)
##        gs12 = gs1.add_subgraph('ClusterG2')
##        self.assertEqual(gs12.level,2)
##        e = gs12.add_edge('c','d')
##        self.assertEqual(e.src.parent.level,2)
##        self.assertEqual(e.parent.level,2)
##
##    def test_addedgesubgraphs(self):
##        """
##        digraph G {
##        	a -> b;
##        	subgraph clusterG {
##        		a -> b;
##        	}
##        	subgraph clusterGG {
##        		a -> b;
##        	}
##
##strict digraph G {
##        node [label="\N"];
##        graph [bb="0,0,86,140"];
##        subgraph clusterG {
##                graph [bb="8,8,78,132"];
##                a [pos="43,106", width="0.75", height="0.50"];
##                b [pos="43,34", width="0.75", height="0.50"];
##                a -> b [pos="e,43,52 43,88 43,80 43,71 43,62"];
##        }
##}
##        }"""
##        g = dotp.DotGraph()
##        e1 = g.add_edge('a','b')
##        self.assertEqual(e1.parent.name,g.name)
##        gs = g.add_subgraph('clusterG')
##        e2 = gs.add_edge('a','b')
##        self.assertEqual(e2.parent.name,gs.name)
##        self.assertEqual(e1.parent.name,gs.name)
##        gs2 = g.add_subgraph('clusterGG')
##        e3 = gs2.add_edge('a','b')
##        self.assertEqual(e2.parent.name,gs.name)
##        self.assertEqual(e3.parent.name,gs.name)
##        self.assertEqual(len(gs2.edges),3)
##
##    def test_add_single_edge_to_subgraph(self):
##        """Edge should belong to subgraph"""
##        g = dotp.DotGraph()
##        gs = g.add_subgraph('clusterG')
##        na = gs.add_node('a')
##        nb = gs.add_node('b')
##        edge = g.add_edge('a','b')
##        self.assertEqual(na.parent,gs)
##        self.assertEqual(nb.parent,gs)
##        self.assertEqual(edge.parent.name,gs.name)
##
##    def test_add_multiple_edges_to_subgraph(self):
##        """Edges should belong to subgraph"""
##        g = dotp.DotGraph()
##        gs = g.add_subgraph('clusterG')
##        na = gs.add_node('a')
##        nb = gs.add_node('b')
##        edge = g.add_edge('a','b')
##        self.assertEqual(edge.parent.name,gs.name)
##        edge2 = g.add_edge('a','b')
##        self.assertEqual(edge2.parent.name,gs.name)
##
##    def test_change_edge_parent(self):
##        """If edge nodes change parents, so should the edge"""
##        g = dotp.DotGraph()
##        edge = g.add_edge('a','b')
##        gs = g.add_subgraph('clusterG')
##        na = gs.add_node('a')
##        nb = gs.add_node('b')
##        self.assertEqual(edge.parent.name,gs.name)
##
##
##
##
##
##
##
##
##
##
##






if __name__ == '__main__':
    unittest.main()
