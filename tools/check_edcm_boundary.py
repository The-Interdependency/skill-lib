# ratios: loc_comments=33:22 imports_exports=4:1 calls_definitions=16:1
"""Executable cross-source scale witness; not a geometry or measurement proof.

Usage: python tools/check_edcm_boundary.py /exact/edcm/checkout
The supplied clean checkout must match EDCM_COMMIT. No package install or network
access is performed by this witness. Refreshing the pin is a reviewed boundary change.
"""

# === MODULE_BUILD ===
# id: gonol_edcm_scale_witness
#   module_name: check_edcm_boundary
#   module_kind: adapter
#   summary: Exercise an exact EDCM constructor's non-adjacent scale and replay contract.
#   owner: skill-lib maintainers
#   public_surface: check
#   internal_surface: none
#   auth_boundary: none
#   storage_boundary: none
#   network_boundary: none
#   user_data_boundary: none
#   admin_only: false
#   tests: explicit CLI against the declared EDCM commit
#   rollout: cross-source CI gate
#   rollback: retain pin and report boundary as hmmm if unavailable
# === END MODULE_BUILD ===

from pathlib import Path
import subprocess
import sys

EDCM_COMMIT = "ddc89a97ebbcf0a5863dad6e633b01b520e9bccf"


def check(root: Path) -> None:
    actual = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if actual != EDCM_COMMIT:
        raise ValueError(f"expected exact EDCM {EDCM_COMMIT}, got {actual}")
    if subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]):
        raise ValueError("EDCM witness requires a clean source checkout")
    sys.path.insert(0, str(root.resolve()))
    from edcm.gonol import construct_gonol, replay_gonol, GonolConstructionError

    character = construct_gonol(scale="character", source="x", source_id="skill-lib:character")
    definition = construct_gonol(scale="definition", source="bounded evidence",
                                 relation="skill-lib:defined-by", participants=(character.gonol,),
                                 source_id="skill-lib:definition")
    if definition.gonol.participants != (character.gonol,):
        raise AssertionError("definition participants changed")
    if replay_gonol(receipt=definition).receipt_digest != definition.receipt_digest:
        raise AssertionError("replay digest changed")
    if definition.standing != "implemented-candidate":
        raise AssertionError("candidate standing changed")
    if definition.selection_effect != "none":
        raise AssertionError("selection effect transferred")
    try:
        construct_gonol(scale="undeclared-scale", source="x", source_id="skill-lib:invalid")
    except GonolConstructionError:
        pass
    else:
        raise AssertionError("undeclared scale must not become eligible")
    print(f"PASS EDCM {actual}: direct character-to-definition, replay, candidate non-transfer, rejected undeclared scale")


if __name__ == "__main__":
    check(Path(sys.argv[1]))
# ratios: loc_comments=33:22 imports_exports=4:1 calls_definitions=16:1