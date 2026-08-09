from __future__ import annotations

from copy import deepcopy

from tests.component.checkers.exact_domain_checker_support import _request as _bound

from jacobian_checkers.exact_domain_operations import check_rational_linear_optimum


def _q(num: int, den: int = 1) -> dict[str, str]:
    return {"num": str(num), "den": str(den)}


def _request() -> dict[str, object]:
    source = {
        "program": {
            "variables": ["x", "y"],
            "objective": [_q(1), _q(2)],
            "coefficients": [[_q(1), _q(1)]],
            "rhs": [_q(1)],
        },
        "wall_seconds": 10,
    }
    candidate = {
        "status": "CERTIFICATE_PRODUCED",
        "conclusion": "UNKNOWN",
        "primal_candidate": [_q(1), _q(0)],
        "dual_candidate": [_q(1)],
        "primal_objective": _q(1),
        "dual_objective": _q(1),
        "primal_residuals": [_q(0)],
        "dual_slacks": [_q(0), _q(1)],
        "certificate_available": True,
        "backend": "sympy",
        "backend_version": "1.14.0",
        "verification": "UNVERIFIED",
        "detail": "exact producer candidate",
    }
    return _bound(
        "optimization.linear.rational_optimum.compute",
        "optimization.linear.rational-optimum.fraction-replay",
        source,
        candidate,
    )


def test_checker_accepts_exact_primal_dual_optimum() -> None:
    assert check_rational_linear_optimum(_request())["accepted"] is True


def test_checker_rejects_dual_feasibility_without_objective_equality() -> None:
    request = _request()
    request["candidate"]["payload"]["dual_candidate"] = [_q(0)]
    request["candidate"]["payload"]["dual_objective"] = _q(0)
    request["candidate"]["payload"]["dual_slacks"] = [_q(1), _q(2)]
    from tests.support.artifacts import canonical_digest

    request["candidate"]["payload_digest"] = canonical_digest(
        request["candidate"]["payload"]
    )

    checked = check_rational_linear_optimum(request)

    assert checked["accepted"] is False
    assert checked["conclusion"] == "UNKNOWN"


def test_checker_rejects_tampered_coefficient_binding() -> None:
    request = _request()
    forged = deepcopy(request)
    forged["claim"]["payload"]["program"]["objective"][0] = _q(2)
    from tests.support.artifacts import canonical_digest

    forged["claim"]["payload_digest"] = canonical_digest(forged["claim"]["payload"])

    checked = check_rational_linear_optimum(forged)

    assert checked["accepted"] is False
    assert checked["conclusion"] == "UNKNOWN"
