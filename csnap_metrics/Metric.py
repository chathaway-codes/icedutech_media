class Metric:
    def __init__(self, graph):
        self.graph = graph

    def calculate(self):
        raise Exception("calculate not implemented in %s" % (self.__class__.__name__))

class CyclomaticMetric(Metric):
    def calculate(self):
        e = len(self.graph.edges())
        n = len(self.graph.nodes())
        p = len(self.graph.components())
        """for comp in self.graph.components():
            print "Component!"
            for z in comp:
                print str(z)
            print "---------------------"
        print "edges: %s\tnodes: %s\tcomp: %s" % (e, n, p)"""
        return e-n+2*p

class DataflowMetric(Metric):
    def __init__(self, graph, alpha=1, beta=1):
        Metric.__init__(self, graph)

        self.alpha = alpha
        self.beta = beta

    def calculate(self):
        cf = self.control_flow_complexity()
        df = self.data_flow_complexity()
        return self.alpha*cf + self.beta*df

    def control_flow_complexity(self):
        # For the DF complexity measure, this is merely the number of edges
        return len(self.graph.edges())

    def _count_variable_definitions(self, node, variable, visited=[]):
        if node in visited:
            return 0
        if variable in node.variables():
            return 1
        visited += [node]
        for p in node.parents():
            ret = self._count_variable_definitions(p, variable, visited)
            if ret != 0:
                return ret
        return 0
    def get_def(self, node):
        defs = 0
        # For each variable in node, count the # of times it's defined
        for variable in node.references():
            # Count the number of times this variable has occured in each parent
            defs += 1 + self._count_variable_definitions(node, variable)
        return defs


    def data_flow_complexity(self):
        # This should include DF of end, but not start nodes
        df = 0
        for node in self.graph.nodes():
            df += self.get_def(node)
        return df

class NCDMetric(Metric):

    def calculate(self, graph):
        import io
        import zipfile

        mem_file = io.BytesIO()
        mem_file2 = io.BytesIO()
        mem_file12 = io.BytesIO()

        with zipfile.ZipFile(mem_file, 'w') as zip:
            zip.writestr('x.txt', self.graph.souce_code*1000, zipfile.ZIP_DEFLATED)
            zip.close()
        with zipfile.ZipFile(mem_file2, 'w') as zip:
            zip.writestr('x.txt', graph.souce_code*1000, zipfile.ZIP_DEFLATED)
            zip.close()
        with zipfile.ZipFile(mem_file12, 'w') as zip:
            zip.writestr('x.txt', self.graph.souce_code*1000 + graph.souce_code*5, zipfile.ZIP_DEFLATED)
            zip.close()
        Cxy = len(mem_file12.getvalue())
        Cx = len(mem_file.getvalue())
        Cy = len(mem_file2.getvalue())
        return float(Cxy - min(Cx, Cy))/(max(Cx, Cy))

class GNCDMetric(Metric):

    def calculate(self, graph):
        import io
        import gzip

        mem_file = io.BytesIO()
        mem_file2 = io.BytesIO()
        mem_file12 = io.BytesIO()

        with gzip.GzipFile("test.txt", 'w', fileobj=mem_file) as zip:
            zip.write(self.graph.souce_code)
            zip.close()
        with gzip.GzipFile("test.txt", 'w', fileobj=mem_file2) as zip:
            zip.write(graph.souce_code)
            zip.close()
        with gzip.GzipFile("test.txt", 'w', fileobj=mem_file12) as zip:
            zip.write(self.graph.souce_code + graph.souce_code)
            zip.close()
        Cxy = len(mem_file12.getvalue())
        Cx = len(mem_file.getvalue())
        Cy = len(mem_file2.getvalue())
        return float(Cxy - min(Cx, Cy))/(max(Cx, Cy))

class LOCMetric(Metric):
    def calculate(self):
        return self.graph.lines_of_code()

class EffortMetric(Metric):
    def calculate(self):
        """ Waiting on book from library; first appeard in
        Halstead, Maurice H. "Elements of software science." (1977).
        """
        from math import log
        funny_char_1 = 0
        funny_char_2 = 1
        n_1 = 0
        n_2 = 0
        return (funny_char_1*N_2*(N_1+N_2)*log(funny_char_1+funny_char_2, 2))/(2*funny_char_2)
