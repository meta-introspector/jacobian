"""Independent checker declarations owned by rational optimization."""

from jacobian.checker_operations import ExactReplayCheckerDeclaration
from jacobian.contracts.validated_analysis import RationalLinearProgramRequest

RATIONAL_OPTIMIZATION_EXACT_REPLAY_CHECKERS = (
    ExactReplayCheckerDeclaration(
        "optimization.linear.rational_optimum.compute",
        RationalLinearProgramRequest,
        "check_rational_linear_optimum",
        "optimization.linear.rational-optimum.fraction-replay",
        replay_method="Python-FLINT exact rational primal/dual replay",
        reason=(
            "operator-authorized Python-FLINT checker independently "
            "replays feasibility, objectives, and strong-duality equality without "
            "importing the SymPy producer"
        ),
        verification_capability_id="optimization.linear.rational_optimum.verify",
        verification_title="Verify a rational linear-program optimum certificate",
        verification_description=(
            "Independently replay exact primal feasibility, dual feasibility, "
            "both objective values, and equality of the bounds for one stored "
            "standard-form rational linear-program result."
        ),
        verification_tags=(
            "verification",
            "exact",
            "optimization",
            "linear-program",
            "rational",
        ),
    ),
)


__all__ = ["RATIONAL_OPTIMIZATION_EXACT_REPLAY_CHECKERS"]
