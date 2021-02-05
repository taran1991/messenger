import dis


class ConnectMaker(type):
    def __init__(self, clsname, bases, clsdict):
        self.methods = []
        self.attrs = []
        for cls in bases:
            self._find_attr(cls.__dict__)
        self._find_attr(clsdict)

    def _find_attr(self, clsdict):
        for key, value in clsdict.items():
            try:
                instructions = dis.get_instructions(value)
            except TypeError:
                pass
            else:
                for instruction in instructions:
                    if instruction.opname == 'LOAD_GLOBAL' and instruction.argval not in self.methods:
                        self.methods.append(instruction.argval)
                    elif instruction.opname == 'LOAD_ATTR' and instruction.argval not in self.attrs:
                        self.attrs.append(instruction.argval)


class ServerMaker(ConnectMaker):
    def __init__(self, clsname, bases, clsdict):
        super().__init__(clsname, bases, clsdict)
        if 'connect' in self.methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in self.attrs and 'AF_INET' in self.attrs):
            raise TypeError('Некорректная инициализация сокета.')
        type.__init__(self, clsname, bases, clsdict)


class ClientMaker(ConnectMaker):
    def __init__(self, clsname, bases, clsdict):
        super().__init__(clsname, bases, clsdict)
        if ('accept' in self.methods or 'listen' in self.methods):
            raise TypeError('В классе обнаружено использование запрещённого метода')
        if 'get_message' in self.attrs or 'send_message' in self.attrs:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        type.__init__(self, clsname, bases, clsdict)