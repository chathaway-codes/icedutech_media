class Node:
    _id = 0
    def __init__(self, parents=None, variables=None, references=None, children=None, name="", node_type="data", lines_of_code=0):
        self.id = Node._id
        Node._id += 1
        self._parents = []
        if parents != None:
            for p in parents:
                self.add_parent(p)
        # A string of variable names
        if variables == None:
            self._variables = []
        else:
            self._variables = variables
        if children == None:
            self._children = []
        else:
            self._children = children
        if references == None:
            self._references = []
        else:
            self._references = references
        if self._parents != []:
            for p in self._parents:
                p.add_child(self)
        self.node_type = node_type
        self._name = name
        self.lines_of_code = lines_of_code

    def if_node(self):
        return self.node_type == "if"

    def loop_node(self):
        return self.node_type == "loop"

    def data_node(self):
        return self.node_type == "data"

    def start_node(self):
        return len(self.parents()) == 0

    def end_node(self):
        return len(self.children()) == 0

    def add_child(self, node):
        if node not in self._children:
            self._children += [node]
        if self not in node.parents():
            node.add_parent(self)

    def add_parent(self, node):
        if node not in self._parents:
            self._parents += [node]
        if self not in node.children():
            node.add_child(self)

    def add_variable(self, variable):
        if variable not in self._variables:
            self._variables += variable

    def add_reference(self, reference):
        if reference not in self._references:
            self._references += reference

    def children(self):
        return self._children

    def variables(self):
        return self._variables

    def references(self):
        return self._references

    def parents(self):
        return self._parents

    def name(self):
        return self._name

    def __str__(self):
        out = ""

        if self.parents() != None:
            out += "["
            for p in self.parents():
                out += "%s," % p.id
            out += "]"
        else:
            out += "None"
        out += " => %s (%s) => [" % (self.id, self._name)

        for c in self.children():
            out += "%s," % c.id

        return out + "]"
