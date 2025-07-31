"""
ARmi Thermal Expansion (ARTE) Worker
Expands every fuel block each cycle.
"""
from typing import Dict
from typing import List

from armi.bookkeeping import report
from armi.bookkeeping.report import data
from armi.reactor import assemblies
from armi.reactor import blocks
from armi.reactor import components
from armi.reactor import cores
from armi.reactor.flags import Flags


ARTE_TABLE = data.Table(
    "Thermal Axial Expansion per Assembly",
    "ARTE Plugin Results",
    header=["Assembly ID", "L0 (cm)", "L (cm)", "ΔL (cm)", "Strain (%)"],
)

ARTE_REPORT = data.Report(
    "Thermal Axial Expansion per Assembly Report",
    "ARTE Plugin Results",
)

COLD_TEMP_C = 20


class FuelBlockAxialExpander:
    """
    Expands every fuel block and records assembly-level growth.
    """

    def __init__(self, core: cores.Core, t_cold: float = COLD_TEMP_C):
        self.core = core
        self.t_cold = t_cold

        self._assembly_growth: Dict[assemblies.Assembly, float] = {}
        self._previous_block_length: Dict[blocks.Block, float] = {}
        self._previous_component_temp: Dict[components.Component, float] = {}

        self._fuel_block_cache: Dict[
            assemblies.Assembly, List[blocks.Block]
        ] = {}
        self._fuel_component_cache: Dict[
            blocks.Block, List[components.Component]
        ] = {}

        self._populate_cache()

    def expand_fuel_blocks(self):
        """Resize every fuel block and refresh core axial mesh."""
        for assembly in self._fuel_block_cache:
            self._expand_fuel_assembly(assembly)

        self._update_axial_mesh()

    def total_assembly_growth(self, assembly: assemblies.Assembly) -> float:
        """Return ΔL for this assembly (cm)."""
        return self._assembly_growth.get(assembly, 0.0)

    def _expand_block(self, block: blocks.Block) -> float:
        """Resize a single fuel block."""
        previous_height = self._get_last_cycle_height(block)
        max_height = previous_height

        for component in self._fuel_component_cache[block]:
            factor = component.getThermalExpansionFactor(
                T0=self._get_last_cycle_temp(component),
            )
            self._previous_component_temp[component] = component.temperatureInC
            max_height = max(max_height, previous_height * factor)

        block.setHeight(max_height)
        self._previous_block_length[block] = max_height
        return max_height - previous_height

    def _expand_fuel_assembly(self, assembly: assemblies.Assembly) -> None:
        """Resize a single fuel assembly."""
        assembly_cycle_growth = 0.0
        for block in self._fuel_block_cache[assembly]:
            assembly_cycle_growth += self._expand_block(block)

        self._update_assembly_growth(assembly, assembly_cycle_growth)

    def generate_assembly_report(self) -> None:
        """Generates an ARMI report with axial growth per assembly."""
        for assembly, block_list in self._fuel_block_cache.items():
            cold_height = 0.0
            warm_height = 0.0
            for block in block_list:
                cold_height += block.p.heightBOL
                warm_height += block.p.height

            growth = warm_height - cold_height
            strain = growth / cold_height * 100.0

            report.setData(
                f"Assembly {assembly.getLocation()}",
                [
                    round(cold_height, 2),
                    round(warm_height, 2),
                    round(growth, 2),
                    round(strain, 3),
                ],
                group=ARTE_TABLE,
                reports=ARTE_REPORT,
            )

    def _get_reference_temp(self, component: components.Component) -> float:
        if self.t_cold is None:
            return component.inputTemperatureInC
        else:
            return self.t_cold

    def _populate_cache(self):
        self._fuel_block_cache.clear()
        self._populate_fuel_block_cache()
        self._fuel_component_cache.clear()
        self._populate_fuel_component_cache()

    def _populate_fuel_block_cache(self) -> None:
        for assembly in self.core.getAssemblies(Flags.FUEL):
            self._fuel_block_cache[assembly] = assembly.getBlocks(Flags.FUEL)

    def _get_last_cycle_height(self, block: blocks.Block) -> float:
        if block not in self._previous_block_length:
            self._previous_block_length[block] = block.p.heightBOL
        return self._previous_block_length[block]

    def _populate_fuel_component_cache(self) -> None:
        for assembly, block_list in self._fuel_block_cache.items():
            for block in block_list:
                if block not in self._fuel_component_cache:
                    self._fuel_component_cache[block] = block.getComponents(
                        Flags.FUEL
                    )

    def _get_last_cycle_temp(self, component: components.Component) -> float:
        if component not in self._previous_component_temp:
            self._previous_component_temp[component] = self._get_reference_temp(
                component
            )
        return self._previous_component_temp[component]

    def _update_axial_mesh(self):
        # No axial mesh in test cases
        if self.core.p.axialMesh:
            self.core.updateAxialMesh()

    def _update_assembly_growth(
        self, assembly: assemblies.Assembly, growth: float
    ) -> None:
        if not assembly in self._assembly_growth:
            self._assembly_growth[assembly] = 0.0
        self._assembly_growth[assembly] += growth
