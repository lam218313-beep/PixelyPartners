from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import os

class BaseAnalyzer(ABC):
    """
    Clase base abstracta para todos los módulos de análisis (Q1-Q20).
    Define una interfaz común y proporciona utilidades compartidas.
    """
    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        """
        Inicializa el analizador con un cliente de OpenAI y la configuración.
        :param openai_client: Una instancia del cliente de OpenAI (sync o async).
        :param config: Diccionario de configuración del orquestador.
        """
        self.openai_client = openai_client
        self.config = config
    # System is designed to analyze a single client only (no competitor aggregates).
    # All analyzers should operate on client data by default.
        self.outputs_dir = self.config.get("outputs_dir", os.path.join(os.path.dirname(__file__), '..', '..', 'outputs'))

    def load_ingested_data(self) -> Dict[str, Any]:
        """
        Carga y devuelve el diccionario de datos completo desde el archivo ingested_data.json.
        Esta es una utilidad compartida para todos los analizadores.
        """
        json_path = os.path.join(self.outputs_dir, 'ingested_data.json')

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"El archivo de datos ingeridos no se encontró en: {json_path}")

        # use 'utf-8-sig' to gracefully handle files that may contain a BOM
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            ingested_data = json.load(f)
        
        return ingested_data

    def get_client_usernames(self, ingested_data: Dict[str, Any]) -> List[str]:
        """
        Heurística para detectar el/los username(s) del cliente presentes en los posts.
        Devuelve una lista de ownerUsername asociados al cliente_id descrito en client_ficha (si existe),
        o bien una lista vacía si no puede inferirse.
        """
        try:
            client = ingested_data.get('client_ficha', {}) or {}
            client_id = client.get('client_id')
            posts = ingested_data.get('posts', []) or []
            usernames = set()
            for p in posts:
                try:
                    if client_id is None or p.get('client_id') == client_id:
                        u = p.get('ownerUsername')
                        if u:
                            usernames.add(str(u))
                except Exception:
                    continue
            return list(usernames)
        except Exception:
            return []

    def filter_to_client_actors(self, actors: List[Dict[str, Any]], ingested_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filtra la lista de `actors` para devolver sólo aquellos que correspondan
        al/los username(s) del cliente. Si no se encuentra ningún username del cliente,
        intenta devolver una entrada única representando el cliente usando `client_ficha`.
        Diseñado para ser la operación por defecto (sistema single-client).
        """
        try:
            client_usernames = self.get_client_usernames(ingested_data)
            if not client_usernames:
                # Best-effort: build a client entry from client_ficha if available
                cf = ingested_data.get('client_ficha', {}) or {}
                client_name = cf.get('client_name') or cf.get('client_id') or 'client'
                client_username = cf.get('username') or cf.get('ownerUsername') or None
                entry = {'actor': client_name}
                if client_username:
                    entry['username'] = client_username
                return [entry]

            filtered = [a for a in actors if str(a.get('username')) in client_usernames or str(a.get('actor')) in client_usernames]
            # If filtered empty, return a single entry representing the client (best-effort)
            if not filtered:
                cf = ingested_data.get('client_ficha', {}) or {}
                client_name = cf.get('client_name') or client_usernames[0]
                return [{
                    'actor': client_name,
                    'username': client_usernames[0],
                }]
            return filtered
        except Exception:
            # On unexpected errors, return an empty list to avoid exposing competitor info
            return []

    @abstractmethod
    async def analyze(self) -> Dict[str, Any]:
        """
        Método abstracto que debe ser implementado por cada clase de análisis hija.
        Debe ejecutar la lógica de análisis específica y devolver un diccionario con los resultados.
        """
        pass
