

class Audit:

    def __init__(self, store, date, audit_type, auditor) -> None:
        self.store      = store
        self.date       = date
        self.audit_type = audit_type
        self.auditor    = auditor

    def __repr__(self) -> str:
        return f'< Audit store={self.store}, date={self.date}, audit_type={self.audit_type}, auditor={self.auditor} >'
    
    