"""
ARmi Thermal Expansion (ARTE) Plugin
"""
from armi import interfaces
from armi import plugins

from arte import interface


class ArtePlugin(plugins.UserPlugin):
    @staticmethod
    @plugins.HOOKIMPL
    def exposeInterfaces(cs):
        """
        Function for exposing the interface.
        """

        return [
            interfaces.InterfaceInfo(
                interface.ORDER, interface.ArteInterface, {}
            )
        ]
