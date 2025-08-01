# ARTE – ARMI Thermal Expansion Plugin

**ARTE** (**AR**mi **T**hermal **E**xpansion) is a lightweight ARMI plugin that computes **axial thermal expansion** for fuel blocks at each simulation time step. It records per-assembly growth (ΔL, strain %) and is self-contained, allowing easy integration with any ARMI-based application.

---

## Installation

Clone and install ARTE using pip:

```bash
git clone https://github.com/jwmat/antares-armi-plugin.git
cd antares-armi-plugin
pip install .   # or pip install -e . for editable installs
```

To run unit tests, install the dev environment:

```bash
pip install -e .[dev] # or pip install .\[dev\] if using zsh
```

---

## Running Example Models

Two example models are provided and pre-configured to use ARTE. After running a model, open `reports/Thermal Axial Expansion per Assembly Report.html` to view the results.

| Model                                            | Command                                                    |
| ------------------------------------------------ | ---------------------------------------------------------- |
| fftf-isothermal | **Fast Flux Test Facility** |
| anl-afci-177 | **ANL Advanced Fuel Cycle Initiative (177‑pin)** |

### Example commands:

**Fast Flux Test Facility:**

```bash
armi run models/fftf-isothermal/FFTF-interview.yaml
```

**ANL Advanced Fuel Cycle Initiative:**

```bash
armi run models/anl-afci-177/anl-afci-177-interview.yaml
```

---

## Repository Structure

```
arte/
├── __init__.py
├── plugin.py            # ArtePlugin – registers the interface
├── interface.py         # ArteInterface – ARMI hooks
└── expander.py          # FuelBlockAxialExpander – core algorithm
models/
└── ...                  # Sample FFTF / AFCI input files
README.md                # ← you are here
```

---

## Architecture Overview

ARTE extends ARMI's `UserPlugin`, enabling it to integrate smoothly into existing ARMI applications without creating a dedicated ARMI app package. The core algorithm assumes an initial reference temperature of 20 °C, set by default in `FuelBlockAxialExpander`.

### ArtePlugin

* Minimal implementation via `exposeInterfaces()`.

### ArteInterface

Provides integration points between ARTE and the ARMI reactor model:

| Hook                | Purpose                                                          |
| ------------------- | ---------------------------------------------------------------- |
| `interactEveryNode` | Calls `FuelBlockAxialExpander.expand_fuel_blocks()` each timestep. |
| `interactEOL`       | Generates final per-assembly axial growth report.                |

### FuelBlockAxialExpander

The core class that calculates axial expansion:

* **Caches**: Stores per-assembly and per-block data to improve performance (O(N) scaling).
* **State Variables**: Tracks cumulative assembly growth and cycle-specific heights/temperatures.
* **Main Method**: `FuelBlockAxialExpander.expand_fuel_blocks()` invoked by ArteInterface.

#### Expansion Algorithm (per cycle)

1. **Build cache (initial call only).**
2. **For each assembly:**

   1. Loop through fuel blocks.
   2. Compute thermal expansion factors.
   3. Adjust block height to the largest component dimension.
   4. Accumulate block ΔL into assembly totals.
3. **Update core axial mesh** for downstream physics calculations.

`FuelBlockAxialExpander.generate_assembly_report()` summarizes total growth per assembly at EOL.

---

## Requirements Met

1. **Create a New Plugin**: Defined in `arte.plugin.ArtePlugin`, inheriting from ARMI’s `UserPlugin`. Uses `setup.py` for pip installation.
2. **Implement an Interface**: `arte.interface.ArteInterface` inherits from ARMI’s `Interface` class.
3. **Use the Correct Hook**: Utilizes `interactEveryNode` for timestep execution.
4. **Implement the Logic**:

   * **Initial reference temperature**: Constant (`arte.expander.COLD_TEMP_C` = 20 °C). Attempted ARMI settings usage but limited by `UserPlugin`.
   * **Block parameters updated**: Via `armi.blocks.Block.setHeight`. Adding new parameters limited by `UserPlugin`.
5. **Write a Unit Test**: Pytest implemented in `tests.axial_growth_test.py`. Includes `test_single_block_growth`.
6. **Summarize Results**: Total axial growth printed at simulation end (`interactEOL`).

---

## Deliverables

* **Repository Link**: [https://github.com/jwmat/antares-armi-plugin](https://github.com/jwmat/antares-armi-plugin)
* **README.md**: [README.md](https://github.com/jwmat/antares-armi-plugin/blob/main/README.md)
* **Sample Summary Outputs**:

From FFTF-isothermal model:

```
[info] Total axial growth of the active fuel stack in the central assembly: 0.22 cm
```

From ANL-AFCI-177 model:

```
[info] Total axial growth of the active fuel stack in the central assembly: 0.97 cm
```
