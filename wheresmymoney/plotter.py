import pygal

class PiePlotter(object):
    
    def __init__(self, title, out_filename=None):
        if out_filename is None:
            self.out_filename = 'pie_total.html'
            self.graph = pygal.Pie(
                inner_radius=.4, disable_xml_declaration=True,
                width=1200, height=600, explicit_size=True)
            self.graph.title = title

    def add_list(self, data):
        for type_, amount, count in data:
            amount = int(amount * 100)/100
            self.graph.add(type_, amount)

    def show(self):
        self.graph.render_to_file(self.out_filename)

    def render(self):
        return self.graph.render()

    @property
    def title(self):
        return self.graph.title
