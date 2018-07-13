class Alternative(object):
    id = 0
    creator= ""
    link = ""
    resource=""

    # The class "constructor" - It's actually an initializer
    def __init__(self, id, creator, link, resource):
        self.id =id
        self.creator = creator
        self.link = link
        self.resource=resource

def make_alternative(id, creator, link, resource):
    alternative = Alternative(id, creator, link, resource)
    return alternative