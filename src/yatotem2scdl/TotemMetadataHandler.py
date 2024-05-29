from typing import Optional
from xml.sax import ContentHandler


class FinishedParsing(Exception):
    pass


class TotemMetadataHandler(ContentHandler):
    def __init__(self) -> None:
        
        self._state_in_document_budgetaire = False

        self.nomenclature: Optional[str] = None
        self.code_etape: Optional[str] = None
        self.id_etab: Optional[str] = None
        self.annee: Optional[str] = None
        self.scellement_date: Optional[str] = None
    
    def startElement(self, name, attrs):

        self.__on_start_element_is_in_document_budgetaire(name, attrs)
        self.__on_start_element_inside_document_budgetaire(name, attrs)
        self.may_finish_parsing()
    
    def endElement(self, name: str) -> None:
        self.__on_end_element_is_in_document_budgetaire(name)
        self.may_finish_parsing()
    
    def __on_start_element_is_in_document_budgetaire(self, name, attrs):
        if name == "DocumentBudgetaire":
            self._state_in_document_budgetaire = True

    def __on_end_element_is_in_document_budgetaire(self, name):
        if name == "DocumentBudgetaire":
            self._state_in_document_budgetaire = False
    
    def __on_start_element_inside_document_budgetaire(self, name, attrs):

        if not self._state_in_document_budgetaire:
            return

        if name == "Nomenclature":
            self.nomenclature = attrs.getValueByQName("V")
        if name == "NatDec":
            self.code_etape = attrs.getValueByQName("V")
        elif name == "IdEtab":
            self.id_etab = attrs.getValueByQName("V")
        elif name == "Exer":
            self.annee = attrs.getValueByQName("V")
        elif name == "Scellement":
            self.scellement_date = attrs.getValueByQName("date")
        else:
            return

    def may_finish_parsing(self):
        if (
            self.nomenclature is not None
            and self.code_etape is not None
            and self.id_etab is not None
            and self.annee is not None
            and self.scellement_date is not None
        ):
            raise FinishedParsing()