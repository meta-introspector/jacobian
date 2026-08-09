from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from tests.support.services import DomainTestServices, open_domain_services

from jacobian.contracts.capabilities import (
    CapabilityAssuranceLevel,
    CapabilityMode,
    CapabilityRequest,
)
from jacobian.contracts.results import ExecutionStatus
from jacobian.domains.optimization import build_rational_optimization_bundle
from jacobian.exact_domain_checkers import install_exact_domain_verification
from jacobian.portfolio.domain_installation import DomainBundleInstaller
from jacobian.portfolio.model import PortfolioPlan
from jacobian.runtime.config import CheckerAuthorityMode


@pytest.fixture
def optimization_services(tmp_path: Path) -> Iterator[DomainTestServices]:
    bundle = build_rational_optimization_bundle()
    with open_domain_services(
        tmp_path / "state",
        checker_authority=CheckerAuthorityMode.INSTALL_BUNDLED,
    ) as services:
        installed = DomainBundleInstaller(services.installation).install(
            PortfolioPlan(domain_bundles=(bundle,))
        )
        adapters, _ = install_exact_domain_verification(
            services.core.store,
            services.core.schemas,
            services.core.artifacts,
            services.application.verification,
            services.core.checkers,
            bundles={"optimization": (bundle, installed.installed["optimization"])},
            authorize=services.installation.authorizes_bundled_checkers,
        )
        for adapter in adapters:
            services.installation.register_capability(adapter)
        yield services


def _q(num: int, den: int = 1) -> dict[str, str]:
    return {"num": str(num), "den": str(den)}


def _program() -> dict[str, object]:
    return {
        "variables": ["x", "y"],
        "objective": [_q(1), _q(2)],
        "coefficients": [[_q(1), _q(1)]],
        "rhs": [_q(1)],
    }


def test_rational_lp_result_uses_independent_exact_replay(
    optimization_services: DomainTestServices,
) -> None:
    computed = optimization_services.core.capabilities.invoke(
        CapabilityRequest(
            capability_id="optimization.linear.rational_optimum.compute",
            input={"program": _program(), "wall_seconds": 10},
        )
    )
    result_uri = computed.artifact_uris[1]

    verified = optimization_services.core.capabilities.invoke(
        CapabilityRequest(
            capability_id="optimization.linear.rational_optimum.verify",
            mode=CapabilityMode.VERIFY,
            input={"result_uri": result_uri},
        )
    )

    assert verified.execution.status is ExecutionStatus.COMPLETED
    assert verified.output["status"] == "VERIFIED"
    assert verified.output["operation_id"] == (
        "optimization.linear.rational_optimum.compute"
    )
    assert verified.output["result_uri"] == result_uri
    assert verified.assurance.level is CapabilityAssuranceLevel.VERIFIED
    assert verified.output["verification_record_uri"] in verified.artifact_uris
