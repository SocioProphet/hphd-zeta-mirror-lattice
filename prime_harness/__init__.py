"""Prime Harness v0.2 M1 infrastructure.

This package implements the infrastructure prerequisites for the HPHD
zeta mirror-lattice prime residual benchmark. It intentionally does not
certify primality from scores; primality information lives only in the
sieve/oracle layer and manifest construction.
"""

__all__ = [
    "intervals",
    "sieve_truth",
    "li_quadrature",
    "psi_residual",
    "zeta_zeros",
    "zero_table_provenance",
    "explicit_formula",
    "metrics",
    "manifest",
]
