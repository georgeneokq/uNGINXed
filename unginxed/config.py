import crossplane

class Config:
    def __init__(self, filepath: str):
        self.filepath: str = filepath
        self.raw: dict|None = crossplane.parse(filepath)
        self.parsed: List[dict] = [] if len(self.raw['config']) == 0 else self.raw['config'][0]['parsed']
    

    def get_raw_config(self) -> dict|None:
        return None if self.raw is None else self.raw['config'][0]


    def get_directive(self, directive: str) -> dict|None:
        '''
        Retrives a dictonary relating to a directive
        '''
        if self.raw is None:
            return None
        for block in self.parsed:
            if 'directive' in block.keys() and block['directive'] == directive:
                return block
        return None


    def get_directive_blocks(self, directive: str) -> List[dict]:
        '''
        Retrieves a list of blocks associated with a directive. Typically arguments and other subdirectives
        '''
        directive_dict = get_directive(directive)
        return [] if directive_dict is None else directive_dict['blocks']


    def __repr__(self) -> str:
        return str(self.raw)
