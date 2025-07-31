"""
ARmi Thermal Expansion (ARTE) Interface
"""
from armi import interfaces
from armi import runLog

from arte.expander import FuelBlockAxialExpander

ARTE_INTERFACE_NAME = "thermalExpansion"
ORDER = interfaces.STACK_ORDER.REACTIVITY_COEFFS


class ArteInterface(interfaces.Interface):
    """
    Apply axial thermal expansion to fuel blocks.
    """

    name = ARTE_INTERFACE_NAME

    def __init__(self, r, cs):
        interfaces.Interface.__init__(self, r, cs)
        self.expander = FuelBlockAxialExpander(r.core)

    def interactEOL(self):
        """Called at End-of-Life, after all cycles are complete."""
        self.expander.generate_assembly_report()
        growth = self.expander.total_assembly_growth(self.r.core.refAssem)
        runLog.info(
            f"Total axial growth of the active fuel stack in the central assembly: {growth:.2f} cm"
        )

    def interactBOC(self, cycle=None):
        """Called at the beginning of each cycle."""
        pass

    def interactEOC(self, cycle=None):
        """Called at the end of each cycle."""
        pass

    def interactEveryNode(self, cycle, node):
        """Expand every fuel assembly once per time node."""
        self.expander.expand_fuel_blocks()
