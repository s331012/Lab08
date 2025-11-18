from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        risultato = []

        for impianto in self._impianti:
            consumi = impianto.get_consumi()

            consumi_mese = [c.kwh for c in consumi if c.data.month == mese]

            if not consumi_mese:
                media = 0
            else:
                media = sum(consumi_mese) / len(consumi_mese)

            risultato.append((impianto.nome, media))

        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """

        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = copy.deepcopy(sequenza_parziale)

        else:
            for impianto_id, consumi in consumi_settimana.items():
                # consumi giorno richiesto
                consumi_giorno = consumi[giorno - 1]
                costo = costo_corrente + consumi_giorno

                if ultimo_impianto is not None and ultimo_impianto != impianto_id:
                    costo += 5

                nuova_sequenza = copy.deepcopy(sequenza_parziale)
                nuova_sequenza.append(impianto_id)

                self.__ricorsione(nuova_sequenza, giorno + 1, impianto_id, costo, consumi_settimana)

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        consumi_mese = {}

        for impianto in self._impianti:
            consumi = impianto.get_consumi()

            consumi_giornalieri = {c.data.day: c.kwh for c in consumi if c.data.month == mese and 1 <= c.data.day <= 7}

            kwh_giorni = []
            for giorno in range(1, 8):
                kwh_giorni.append(consumi_giornalieri.get(giorno, 0))

            consumi_mese[impianto.id] = kwh_giorni

        return consumi_mese

