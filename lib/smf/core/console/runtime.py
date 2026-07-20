from typing import Any


class RuntimeContext:
    def __init__(self, metadata: dict, plugin_manager: Any):
        self.metadata = metadata
        self._plugin = plugin_manager
        self.packet_count = 0

    def transform(self, payload: str) -> str:
        """
        Payload interceptor bridge to plugin.
        Simply call the module: runtime.transform(payload)
        """
        if "Transforms" not in self.metadata:
            return payload

        results = self._plugin.broadcast(
            "execute", payload=payload, metadata=self.metadata
        )
        current_payload = payload

        if isinstance(results, dict):
            for plugin_name, res in results.items():
                if isinstance(res, dict) and "mutated_payload" in res:
                    current_payload = res["mutated_payload"]

        return current_payload
