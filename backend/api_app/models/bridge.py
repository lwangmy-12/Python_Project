from pydantic import BaseModel

class Bridge(BaseModel):
    STRUCTURE_NUMBER_008: str
    STATE_CODE_001: int
    COUNTY_CODE_003: int
    LOCATION_009: str
    FACILITY_CARRIED_007: str
    FEATURES_DESC_006A: str
    LAT_016: float
    LONG_017: float
    YEAR_BUILT_027: int
    MAIN_UNIT_SPANS_045: int
    MAX_SPAN_LEN_MT_048: float
    STRUCTURE_LEN_MT_049: float
    ADT_029: int
    DATA_YEAR: int
    DECK_COND_058: int
    SUPERSTRUCTURE_COND_059: int
    SUBSTRUCTURE_COND_060: int
