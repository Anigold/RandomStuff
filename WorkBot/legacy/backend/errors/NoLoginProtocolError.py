class NoLoginProtocolError(Exception):
    '''Raise when a vendor bot either has no implemented login protocol or no such protocol is needed.'''
    def __init__(self, message):
        super().__init__(message)
