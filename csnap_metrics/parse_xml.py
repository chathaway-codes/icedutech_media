import xml.etree.ElementTree as ET
import sys

from Graph import *
from Metric import *
from Node import *

def lookahead(iterable):
    it = iter(iterable)
    last = it.next() # next(it) in Python 3
    for val in it:
        yield last, False
        last = val
    yield last, True

def make_node(parent, parent_node=None, name=None, node_type="data"):
    if name == None:
        name = ''

    # If we don't have a parent node, create a start node
    if parent_node == None:
        raise Exception("This should never happen")
        #cur_node = Node([Node(name="Start")], name=name, node_type=node_type)
    else:
        cur_node = Node(parent_node, name=name, node_type=node_type)
    # Make a starting node
    original_node = cur_node
    first_loop = True
    # For each block, see if it's a loop or a statement
    for block in parent:
        # If it's a loop, enter it

        # Don't recurse into scripts, but any other variable references should be noted
        def find_references(block):
            for b in block.findall('block'):
                if 'var' in b.attrib:
                    yield b.attrib['var']
                yield find_references(b)

        cur_node.add_reference(find_references(block))
        cur_node.lines_of_code += 1

        if block.attrib['s'] == 'doRepeat' or block.attrib['s'] == 'doUntil':
            # Recurse on the loops loop
            # First add the loop node inline
            # If this is a loop right after a loop, the current node should be made into a loop node
            loop_node = cur_node
            if first_loop:
                loop_node._name = block.attrib['s']
                loop_node.node_type='loop'
            else:
                # Else, create a new loop node
                loop_node = Node([cur_node], name=block.attrib['s'], node_type='loop')
            # Then continue to the loop statement
            r = make_node(block[1], [loop_node])
            # Add this loop_node as a child to the tail node
            r.add_child(loop_node)
            # If there are more nodes to be had
            cur_node = Node([loop_node])
        # If it's a conditional, enter it
        elif block.attrib['s'] == 'doIf':
            # If we have a data node with no data, convert it to an if
            if cur_node.data_node() and len(cur_node.variables()) == 0:
                cur_node.node_type = "if"
                cur_node._name = "doIf"
            # Else, create a new node
            else:
                cur_node = Node([cur_node], name="doIf", node_type="if")
            r = make_node(block[1], [cur_node])
            cur_node = Node([r, cur_node])
        # if it's a statement, add it to the node
        else:
            if block.attrib['s'] == 'doSetVar':
                cur_node.add_variable(block.findall('l')[0].text)
            cur_node._name += '\n' + block.attrib['s']

    if node_type=="loop":
        cur_node.add_child(original_node)
        cur_node = original_node


    return cur_node

def main(filename, base_project=None, draw_graph=None):
    tree = ET.parse(filename)
    root = tree.getroot()
    graphs = []
    base_graphs=[]


    if base_project != None:
        my_tree = ET.parse(base_project)
        my_root = my_tree.getroot()
        for sprite in my_root.findall('stage')[0].findall('sprites')[0].findall('sprite'):
                for script in sprite.findall('scripts')[0].findall('script'):
                    graph = Graph(make_node(script, [Node(name="Start")]), source_code=ET.tostring(script))
                    base_graphs += [graph]

    for sprite in root.findall('stage')[0].findall('sprites')[0].findall('sprite'):
        for script in sprite.findall('scripts')[0].findall('script'):
            prev = None
            graph = Graph(make_node(script, [Node(name="Start")]), source_code=ET.tostring(script))
            graphs += [graph]
    for i, g in enumerate(graphs):
        # Print each metric
        sys.stdout.write(filename)
        m = CyclomaticMetric(g)
        sys.stdout.write(",%s"%m.calculate())
        df = DataflowMetric(g)
        sys.stdout.write(",%s"%df.calculate())
        loc = LOCMetric(g)
        sys.stdout.write(",%s"%loc.calculate())

        ncd = NCDMetric(g)
        gncd = GNCDMetric(g)
        for i, graph in enumerate(base_graphs):
            sys.stdout.write(",%s"%ncd.calculate(graph))
            sys.stdout.write(",%s"%gncd.calculate(graph))
        print ""

        if draw_graph != None:
            graph_name = "%s_%s.png" % (draw_graph, i)
            g.to_png(graph_name)

def usage():
    print "Usage: python parse_xml.py [--graph graph_base_name] filename [base project]"

if __name__ == "__main__":
    filename = None
    base_project = None
    draw_graph = None
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    i=1
    while i < len(sys.argv):
        if sys.argv[i] == '--graph':
            if i+1 < len(sys.argv):
                i += 1
                draw_graph = sys.argv[i]
            else:
                print "Invalid input!"
                usage()
                sys.exit(1)
        elif filename == None:
            filename = sys.argv[i]
        elif base_project == None:
            base_project = sys.argv[i]
        else:
            usage()
            sys.exit(1)
        i += 1
    main(filename, base_project, draw_graph)
