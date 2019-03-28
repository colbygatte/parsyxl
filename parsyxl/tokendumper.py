import parsyxl.tokens 

class TokenDepth:
    def __init__(self, bar, pre):
        self._bar = bar
        self._pre = pre
        self.depth = 0
        self.string = ''
    
    def inc(self):
        self.depth += 1
        return self
    
    def dec(self):
        self.depth -= 1
        return self
    
    def nl(self):
        self.string += '\n'
        return self
    
    def bar(self):
        self.string += self._bar*self.depth+self._pre
        return self
    
    def add(self, value):
        self.string += value
        return self


class TokenDumper:
    def __init__(self, bar='|   ', pre='|   '):
        self.depth = TokenDepth(bar, pre)
    
    def dump(self, token, verbose='vv'):
        self.depth.depth = -1
        self.depth.string = ''
        getattr(self, '_' + verbose)(token)
        return self.depth.string

    def _v(self, token):
        d = self.depth.inc()
        dump = self._v

        if token is None:
            d.bar().add('None')
            d.nl()

        elif isinstance(token, parsyxl.tokens.Token):
            d.bar().add('%s: ' % token.name)
            if isinstance(token.value, parsyxl.tokens.Token):
                d.nl()
            dump(token.value)

        elif isinstance(token, list):
            if len(token) == 0:
                d.bar().add('list[]').nl()
            else:
                d.dec()
                d.add('list:%i[' % len(token))
                d.nl()
                for item in token:
                    dump(item)
                d.bar().add(']%').nl()
                d.inc()

        else:
            string_ = str(token)
            d.add(string_ if string_ != '' else "Empty('')")
            d.nl()
        
        d.dec()

    def _vv(self, token, list_item=None):
        d = self.depth.inc()
        dump = self._vv

        if token is None:
            d.bar().nl().bar().add('None')
            d.nl()

        elif isinstance(token, parsyxl.tokens.Token):
            d.bar().nl().bar()
            if list_item is not None:
                d.add('[%i] ' % list_item)
            d.add('%s: ' % token.name)
            if isinstance(token.value, parsyxl.tokens.Token):
                d.nl()
            dump(token.value)

        elif isinstance(token, list):
            if len(token) == 0:
                d.bar().nl().bar()
                if list_item is not None:
                    d.add('[%i] ' % list_item)
                d.add('list[]').nl()
            else:
                if list_item is not None:
                    d.add('[%i] ' % list_item)
                d.add('list:%i[' % len(token))
                d.nl()
                d.dec()
                for index, item in enumerate(token):
                    if isinstance(item, list) and len(item) != 0:
                        d.inc()
                        d.bar()
                        dump(item, index)
                        d.dec()
                    else:
                        dump(item, index)
                d.inc()
                d.bar().nl()
                d.dec().bar().add(']%').nl()
                d.inc()

        else:
            string_ = str(token)
            if list_item is not None:
                d.bar()
                d.add('[%i] ' % list_item)
                d.add('(string): ')
            string_ = string_.replace('\n', r'\n').replace('\t', r'\t')
            d.add('"%s"' % string_ if string_ != '' else "Empty('')")
            d.nl()
        
        d.dec()
