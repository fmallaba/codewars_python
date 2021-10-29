class Thing (object):
    class IsA:
        def __init__(self, parent):
            self.__parent = parent
            
        def __getattr__(self, name):
            setattr(self.__parent, f"is_a_{name}", True)
            
    class IsNotA:
        def __init__(self, parent):
            self.__parent = parent
            
        def __getattr__(self, name):
            setattr(self.__parent, f"is_a_{name}", False)
            
    class IsThe:
        def __init__(self, parent):
            self.__parent = parent
            
        def __getattr__(self, name):
            class What:
                def __init__(self, parent, what):
                    self.__parent = parent
                    self.__what = what
                def __getattr__(self, name):
                    setattr(self.__parent, self.__what, name)
                    return self.__parent
            return What(self.__parent, name)
            
    class Can:
        def __init__(self, parent):
            self.__parent = parent
            
        def __getattr__(self, name):
            def setCan(fnc, results=""):
                fnc.__globals__['name'] = self.__parent.name
                canFnc = fnc
                if len(results) > 0:
                    setattr(self.__parent, results, [])
                    def canWithTrack(*args, **kwargs):
                        res = fnc(*args, **kwargs)
                        getattr(self.__parent, results).append(res)
                        return res
                    canFnc = canWithTrack
                setattr(self.__parent, name, canFnc)
            return setCan
    
    class Tuple(tuple):
        class Each:
            def __init__(self, tup):
                self.__tup = tup
                
            def __getattr__(self, name):
                self.__tup = Thing.Tuple(getattr(e, name) for e in self.__tup)
                return self
            
            def __call__(self, *args):
                self.__tup = Thing.Tuple(e(*args) for e in self.__tup)
                return self
        
        def __new__ (cls, a):
            return super(Thing.Tuple, cls).__new__(cls, tuple(a))
        
        def __init__(self, _):
            self.each = Thing.Tuple.Each(self)

        
    class Has:
        def __init__(self, parent, n):
            self.__parent = parent
            self.__n = n
            
        def __getattr__(self, name):
            if self.__n > 1:
                attrName = name[:-1]
                attr = Thing.Tuple(Thing(attrName) for i in range(self.__n))
                for a in attr:
                    a.__setattr__(f"is_{attrName}", True)
            else:
                attr = Thing(name)
                attr.__setattr__(f"is_{name}", True)
            setattr(self.__parent, name, attr)
            return getattr(self.__parent, name)
            
    def __init__(self, name=""):
        self.name = name
        self.is_a = Thing.IsA(self)
        self.is_not_a = Thing.IsNotA(self)
        self.is_the = Thing.IsThe(self)
        self.being_the = Thing.IsThe(self)
        self.and_the = Thing.IsThe(self)
        self.can = Thing.Can(self)
        
    def has(self, n):
        return Thing.Has(self, n)
        
    def having(self, n):
        return self.has(n)
