from typing import Type

from ayon_server.addons import BaseServerAddon

from .settings import PureRefSettings, DEFAULT_PUREREF_VALUES


class PureRefAddon(BaseServerAddon):
    settings_model: Type[PureRefSettings] = PureRefSettings

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_PUREREF_VALUES)
