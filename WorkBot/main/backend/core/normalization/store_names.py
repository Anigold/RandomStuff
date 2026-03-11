from __future__ import annotations

class StoreNameNormalizer:
    """
    Converts store names between canonical internal names and external system labels.
    """

    _canonical_to_craftable_audit = {
        "Bakery": "Ithaca Bakery - Meadow St",
        "Triphammer": "Ithaca Bakery - Triphammer Rd",
        "Collegetown": "Collegetown Bagels - College Ave",
        "Easthill": "Collegetown Bagels - East Hill Plaza",
        "Downtown": "Collegetown Bagels - State St",
        "Syracuse": "Collegetown Bagels - Syracuse",
    }

    _craftable_audit_to_canonical = {
        v: k for k, v in _canonical_to_craftable_audit.items()
    }

    # Optional aliases for resilience
    _aliases_to_canonical = {
        "BAKERY": "Bakery",
        "Bakery": "Bakery",
        "ITHACA BAKERY - MEADOW ST": "Bakery",
        "Ithaca Bakery - Meadow St": "Bakery",

        "TRIPHAMMER": "Triphammer",
        "Triphammer": "Triphammer",
        "ITHACA BAKERY - TRIPHAMMER RD": "Triphammer",
        "Ithaca Bakery - Triphammer Rd": "Triphammer",

        "COLLEGETOWN": "Collegetown",
        "Collegetown": "Collegetown",
        "COLLEGETOWN BAGELS - COLLEGE AVE": "Collegetown",
        "Collegetown Bagels - College Ave": "Collegetown",

        "EASTHILL": "Easthill",
        "Easthill": "Easthill",
        "COLLEGETOWN BAGELS - EAST HILL PLAZA": "Easthill",
        "Collegetown Bagels - East Hill Plaza": "Easthill",

        "DOWNTOWN": "Downtown",
        "Downtown": "Downtown",
        "COLLEGETOWN BAGELS - STATE ST": "Downtown",
        "Collegetown Bagels - State St": "Downtown",

        "SYRACUSE": "Syracuse",
        "Syracuse": "Syracuse",
        "COLLEGETOWN BAGELS - SYRACUSE": "Syracuse",
        "Collegetown Bagels - Syracuse": "Syracuse",
    }

    @classmethod
    def to_canonical(cls, value: str) -> str:
        if not value:
            return value
        return cls._aliases_to_canonical.get(value.strip(), value.strip())

    @classmethod
    def to_craftable_audit(cls, canonical_store: str) -> str:
        canonical = cls.to_canonical(canonical_store)
        return cls._canonical_to_craftable_audit.get(canonical, canonical)