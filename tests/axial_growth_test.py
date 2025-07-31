import pytest
from armi import configure
from armi.materials import uZr
from armi.reactor import assemblies
from armi.reactor import blocks
from armi.reactor import components
from armi.reactor import grids
from armi.reactor.flags import Flags
from armi.tests import getEmptyHexReactor

from arte.expander import FuelBlockAxialExpander

configure(permissive=True)


@pytest.fixture
def simple_block():
    block = blocks.HexBlock("TestBlock", height=2)
    block.setType("fuel")
    dims = {"Tinput": 20, "Thot": 600, "op": 16.0, "ip": 1, "mult": 1}
    component = components.Hexagon("fuel", uZr.UZr(), **dims)
    block.add(component)
    return block


@pytest.fixture
def simple_assembly(simple_block):
    assembly = assemblies.HexAssembly("fuel")
    assembly.spatialGrid = grids.AxialGrid.fromNCells(1)
    assembly.add(simple_block)
    return assembly


@pytest.fixture
def simple_core(simple_assembly):
    reactor = getEmptyHexReactor()
    reactor.core.add(simple_assembly)
    return reactor.core


@pytest.fixture
def expander(simple_core):
    return FuelBlockAxialExpander(simple_core)


@pytest.mark.parametrize("cycles", [1, 10, 100])
def test_single_block_growth(expander, cycles):
    block = expander.core.getBlocks(Flags.FUEL)[0]
    initial_height = block.p.height

    for _ in range(cycles):
        expander._expand_block(block)

    assert (
        block.p.height > initial_height
    ), f"Block height {block.p.height} did not increase after {cycles} cycles."

    material = uZr.UZr()
    thermal_expansion_factor = 1 + material.linearExpansionFactor(Tc=600, T0=20)
    assert (
        round(block.p.height - block.p.heightBOL * thermal_expansion_factor, 11)
        == 0
    )


@pytest.mark.parametrize("cycles", [1, 10, 100])
def test_single_assembly_growth(expander, cycles):
    assembly = expander.core.getAssemblies(Flags.FUEL)[0]

    for _ in range(cycles):
        expander._expand_fuel_assembly(assembly)

    growth = expander.total_assembly_growth(assembly)
    assert growth > 0.0, f"Assembly did not expand after {cycles} cycles."


@pytest.mark.parametrize("cycles", [1, 10, 100])
def test_core_growth(expander, cycles):
    for _ in range(cycles):
        expander.expand_fuel_blocks()

    for assembly in expander.core:
        growth = expander.total_assembly_growth(assembly)
        assert (
            growth > 0.0
        ), f"Core assembly {assembly} did not expand after {cycles} cycles."
