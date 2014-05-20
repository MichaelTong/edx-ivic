
class Item(object):
    "This is the definition of base class: queueitem."

    def __init__(self, sessionid, template):
        self.sessionid = sessionid
        self.template = template

    def dict(self):
        return {'sessionid':self.sessionid,'template':self.template}
    
    def string(self):
        return str(self.dict())

    def output(self):
        print self.string()

class ReqItem(Item):
    "This is the definition of request item, derived from item."

class DownItem(Item):
    "This is the definition of showdown queue item, derived from item."

    def __init__(self, sessionid, template, proxy, port):
        Item.__init__(self, sessionid, template)
        self.proxy = proxy
        self.port = port
    
    def dict(self):
        tmp = Item.dict(self)
        tmp['proxy'] = self.proxy
        tmp['port'] = self.port
        return tmp

class RunItem:
     "This is the definiation of running VM item, derived from item."
     def __init__(self, sessionid, template, proxy_url, proxy_process, vcid):
         self.key = (sessionid, template)
         self.value = (proxy_url, proxy_process, vcid)
     
     def dict(self):
         return {self.key:self.value}

class Queue:
     def __init__(self):
         self.queue = []
     def enqueue(self,item):
         self.queue.append(item)
     
     def dequeue(self):
         if self.queue != []:
             d = self.queue[0]
             self.queue = self.queue[1:]
             return d
         else:
             return None
     
     def head(self):
         return self.queue[0]

     def tail(self):
         return self.queue[-1]
     
     def is_empty(self):
         if self.queue == []:
             return True
         else:
             return False
