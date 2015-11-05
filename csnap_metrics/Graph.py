from Node import Node

class Graph:
    def __init__(self, node=None, source_code=None):
        # Order on the nodes matter
        self._nodes = []
        # Step through node.children and add to list
        self.souce_code = source_code
        self.finished = False

        def _add_parents(n):
            if n in self._nodes:
                return
            self._nodes += [n]
            for c in n.parents():
                _add_parents(c)

        if node != None:
            _add_parents(node)

    def add_node(self, node):
        if self.finished:
            raise Exception("Terminated graph; can't add more!")
        self._nodes += [node]

    def edges(self):
        # Call components so we add children nodes
        self.components()
        if hasattr(self, '_edges'):
            return self._edges
        # Construct list of edges
        self._edges = []
        for node in self.nodes():
            for n in node.children():
                self._edges += [(node, n)]
        return self._edges

    def nodes(self):
        # Call components so we add children nodes
        self.components()
        return self._nodes

    def _build_compnent(self, start_node, end_node):
        comp = []
        # Starting from the start_node, add all children
        def _get_component_nodes(node, start_node, comp):
            # Add this node
            comp += [node]
            # If this is the start node, stop
            if node == start_node:
                return
            # Add all of my parents
            for parent in node.parents():
                # If my parent is already in the list, skip it
                if parent in comp:
                    continue
                _get_component_nodes(parent, start_node, comp)
        _get_component_nodes(end_node, start_node, comp)
        return comp

    def strong_components(self):
        self.finished = True
        if hasattr(self, '_strong_components'):
            return self._strong_components
        self._strong_components = []
        visited = []
        for node in self.nodes():
            # If this isn't a loop node, it will never loop
            if not node.loop_node():
                continue
            # For each node, check to see if we can get back to this node by going through all children until we find it again
            l_next = node.children()
            l_visited = [node]
            loop = False

            while len(l_next) > 0:
                l = l_next[0]
                if node in l.children():
                    loop = True
                    break
                l_next = l_next[1:] + l.children()
                l_visited += [l]
            if loop:
                self._strong_components += [self._build_compnent(node, l_next[0])]
        return self._strong_components

    def components(self):
        """Returns a list of lists, each of which contains a component seperated from the others
        """
        self.finished = True
        if hasattr(self, '_components'):
            return self._components
        self._components = []
        start_nodes = []
        for n in self.nodes():
            if len(n.parents()) == 0:
                start_nodes += [n]
        # For each start_node, add all children to the component
        # If there is a case where a start node interacts with another start node, bad things are happening
        def __add_children(node, visited):
            ret = [node]
            visited += [node]
            # If this node doesn't have a end node, add it
            for c in node.children():
                if c not in visited:
                    ret += __add_children(c, visited)
            if len(node.children()) == 0:
                # If I have no children, and no name, I'm the end node
                if node.name() == '':
                    node._name = "End"
                else:
                    end_node = Node([node], name="End")
                    self._nodes += [end_node]
                    ret += [end_node]
                    visited += [end_node]
            return ret

        def __valid_components():
            for c in self._components:
                for n in c:
                    for c2 in self._components:
                        if c2 != c and n in c2:
                            raise Exception("Invalid graph!")
            return True

        for s in start_nodes:
            self._components += [[s]+__add_children(s, [])]
        __valid_components()
        return self._components

    def lines_of_code(self):
        if hasattr(self, '_lines_of_code'):
            return self._lines_of_code
        self._lines_of_code = 0

        for node in self.nodes():
            self._lines_of_code += node.lines_of_code
        return self._lines_of_code

    def simple_list(self):
        out = []
        for c in self.nodes():
            out += [c.id]
        return out

    def to_png(self, filename):
        """This function requires pygraphviz and should only be used
        when that package is installed"""
        import pygraphviz as gz
        A=gz.AGraph(directed=True)
        A.node_attr['style']='filled'
        A.node_attr['shape']='rectangle'
        A.node_attr['fixedsize']='false'
        A.node_attr['fontcolor']='#000000'

        for node in self.nodes():
            A.add_node(node.id)
            n = A.get_node(node.id)
            if node.if_node() or node.loop_node():
                n.attr['shape'] = 'diamond'
            if node.start_node() or node.end_node():
                n.attr['shape'] = 'square'
            if node.name() != "":
                n.attr['label'] = node.name()
            for node2 in node.children():
                A.add_edge(node.id, node2.id)

        # Finally, output graph
        A.draw(filename, prog='dot')


    def __str__(self):
        out = ""
        for c in self.nodes():
            out += str(c) + "\n"
        return out
