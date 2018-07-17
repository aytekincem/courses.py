class Assessment(object):
    id = 0
    creator= ""
    link = ""
    type=""

    # The class "constructor" - It's actually an initializer
    def __init__(self, id, creator, link, type):
        self.id =id
        self.creator = creator
        self.link = link
        self.type=type

def make_assessment(id, creator, link, type):
    assessment = Assessment(id, creator, link, type)
    return assessment