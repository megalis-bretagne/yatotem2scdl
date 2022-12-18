from typing import Optional
from xml.sax import ContentHandler


class FinishedParsing(Exception):
    pass


class TotemMetadataHandler(ContentHandler):
    def __init__(self) -> None:
        self.nomenclature: Optional[str] = None
        self.code_etape: Optional[str] = None
        self.id_etab: Optional[str] = None
        self.annee: Optional[str] = None

    def startElement(self, name, attrs):
        if name == "Nomenclature":
            self.nomenclature = attrs.getValueByQName("V")
        if name == "NatDec":
            self.code_etape = attrs.getValueByQName("V")
        elif name == "IdEtab":
            self.id_etab = attrs.getValueByQName("V")
        elif name == "Exer":
            self.annee = attrs.getValueByQName("V")
        else:
            return

        self.may_finish_parsing()

    def may_finish_parsing(self):
        if (
            self.nomenclature is not None
            and self.code_etape is not None
            and self.id_etab is not None
            and self.annee is not None
        ):
            raise FinishedParsing()