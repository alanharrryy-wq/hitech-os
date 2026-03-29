import unittest

from forge_kernel import KernelBootstrap


class KernelBootstrapTests(unittest.TestCase):
    def test_bootstrap_preloads_wave1_contracts(self) -> None:
        session = KernelBootstrap.start(kernel_version="0.1.0")
        self.assertEqual(session.kernel_version, "0.1.0")
        self.assertEqual(len(session.contracts.known_contracts()), 17)


if __name__ == "__main__":
    unittest.main()
