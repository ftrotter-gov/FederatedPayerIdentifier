#!/usr/bin/env python3
"""
Test suite for tools/FPI_maker_cli.py

This suite is the authoritative validation that FPI uuid generation is
operating correctly. Known-good FPI fixtures below come from the Aetna Texas
mockup files under payer_index_files/ (the FPI appears in each filename and
in each file's first identifier entry).

Run with either of:

    python3 tools/tests/test_FPI_maker_cli.py
    python3 -m unittest discover -s tools/tests
"""

import os
import sys
import unittest
import uuid

# Make tools/ importable regardless of where the tests are run from.
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_TOOLS_DIR = os.path.abspath(os.path.join(_TESTS_DIR, ".."))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from FPI_maker_cli import (  # noqa: E402
    FPI_SOURCE_EXCLUDED_SYSTEM_IDS,
    LEGAL_NAME_HASH_SYSTEM_ID,
    STATE_LEVEL_SYSTEM_IDS,
    apply_state_prefix,
    generate_fpi,
    get_system_by_id,
    get_system_namespace,
    load_payer_systems,
    normalize_legal_name,
    _get_selectable_systems,
)


class TestKnownGoodFPIs(unittest.TestCase):
    """Validate against the known-good FPIs used by the Aetna Texas mockup."""

    def test_naic_id_aetna_health_and_life(self):
        # Aetna Health and Life Insurance Company, NAIC company code 78700
        self.assertEqual(
            generate_fpi(system_id="NAIC_ID", payer_id_value="78700"),
            "68d4ceb9-93f6-548c-912b-f9f43eb79683",
        )

    def test_hios_id_aetna_health_inc_tx(self):
        # Aetna Health Inc. (Texas), HIOS issuer id 58840
        self.assertEqual(
            generate_fpi(system_id="HIOS_ID", payer_id_value="58840"),
            "b1affe56-4f6e-59a1-893e-f611f1dd8b5b",
        )

    def test_state_doi_id_aetna_better_health_of_texas(self):
        # Aetna Better Health of Texas, Inc., Texas DOI id 68775 (state-prefixed)
        self.assertEqual(
            generate_fpi(system_id="STATE_DOI_ID", payer_id_value="TX-68775"),
            "3f9af4c3-d735-5c9b-9674-33cdd1864d6b",
        )

    def test_lei_aetna_life_insurance_company(self):
        # Aetna Life Insurance Company, LEI SPCOIWBJM0HFYQX3A364
        self.assertEqual(
            generate_fpi(system_id="LEI", payer_id_value="SPCOIWBJM0HFYQX3A364"),
            "a04283f0-5a1d-5df8-a744-e252652a1783",
        )


class TestUuidChaining(unittest.TestCase):
    """Validate the uuid5 chaining structure itself."""

    def test_system_namespace_pattern(self):
        expected = uuid.uuid5(uuid.NAMESPACE_DNS, "NAIC_ID.fhir")
        self.assertEqual(get_system_namespace(system_id="NAIC_ID"), expected)

    def test_fpi_is_uuid5_of_system_namespace(self):
        system_namespace = uuid.uuid5(uuid.NAMESPACE_DNS, "NAIC_ID.fhir")
        expected = str(uuid.uuid5(system_namespace, "78700"))
        self.assertEqual(
            generate_fpi(system_id="NAIC_ID", payer_id_value="78700"), expected
        )

    def test_determinism(self):
        first = generate_fpi(system_id="LEI", payer_id_value="SPCOIWBJM0HFYQX3A364")
        second = generate_fpi(system_id="LEI", payer_id_value="SPCOIWBJM0HFYQX3A364")
        self.assertEqual(first, second)

    def test_different_systems_produce_different_fpis(self):
        # Same value under two different system namespaces must not collide.
        self.assertNotEqual(
            generate_fpi(system_id="NAIC_ID", payer_id_value="60054"),
            generate_fpi(system_id="X12_PAYER_ID", payer_id_value="60054"),
        )


class TestLegalNameHashNormalization(unittest.TestCase):
    """LEGAL_NAME_HASH values must always be normalized before hashing."""

    def test_normalize_legal_name_examples(self):
        self.assertEqual(
            normalize_legal_name(payer_legal_name="AETNA HEALTH, INC."),
            "aetnahealthinc",
        )
        self.assertEqual(
            normalize_legal_name(payer_legal_name="Blue Cross & Blue Shield"),
            "bluecrossblueshield",
        )
        self.assertEqual(
            normalize_legal_name(payer_legal_name="HUMANA INSURANCE CO"),
            "humanainsuranceco",
        )

    def test_raw_and_normalized_names_produce_same_fpi(self):
        raw_fpi = generate_fpi(
            system_id=LEGAL_NAME_HASH_SYSTEM_ID,
            payer_id_value="AETNA HEALTH, INC.",
        )
        normalized_fpi = generate_fpi(
            system_id=LEGAL_NAME_HASH_SYSTEM_ID,
            payer_id_value="aetnahealthinc",
        )
        self.assertEqual(raw_fpi, normalized_fpi)

    def test_legal_name_hash_uses_its_own_namespace(self):
        # The hash must live under "LEGAL_NAME_HASH.fhir", not "PAYER_NAME.fhir".
        legal_name_hash_namespace = uuid.uuid5(
            uuid.NAMESPACE_DNS, "LEGAL_NAME_HASH.fhir"
        )
        expected = str(uuid.uuid5(legal_name_hash_namespace, "aetnahealthinc"))
        self.assertEqual(
            generate_fpi(
                system_id=LEGAL_NAME_HASH_SYSTEM_ID,
                payer_id_value="AETNA HEALTH, INC.",
            ),
            expected,
        )


class TestStatePrefixing(unittest.TestCase):
    """State-level identifier values must carry a two-letter state prefix."""

    def test_apply_state_prefix(self):
        self.assertEqual(
            apply_state_prefix(state_code="TX", payer_id_value="68775"),
            "TX-68775",
        )

    def test_apply_state_prefix_is_idempotent(self):
        self.assertEqual(
            apply_state_prefix(state_code="TX", payer_id_value="TX-68775"),
            "TX-68775",
        )

    def test_apply_state_prefix_normalizes_case(self):
        self.assertEqual(
            apply_state_prefix(state_code="tx", payer_id_value="68775"),
            "TX-68775",
        )

    def test_apply_state_prefix_rejects_bad_state_code(self):
        with self.assertRaises(ValueError):
            apply_state_prefix(state_code="Texas", payer_id_value="68775")

    def test_generate_fpi_rejects_unprefixed_state_value(self):
        for state_system_id in STATE_LEVEL_SYSTEM_IDS:
            with self.assertRaises(ValueError):
                generate_fpi(system_id=state_system_id, payer_id_value="68775")


class TestFpiSourceExclusion(unittest.TestCase):
    """You cannot derive an FPI from another FPI."""

    def test_fpi_system_is_excluded(self):
        self.assertIn("FPI", FPI_SOURCE_EXCLUDED_SYSTEM_IDS)

    def test_generate_fpi_rejects_fpi_system(self):
        with self.assertRaises(ValueError):
            generate_fpi(
                system_id="FPI",
                payer_id_value="68d4ceb9-93f6-548c-912b-f9f43eb79683",
            )

    def test_cli_menu_excludes_fpi_system(self):
        payer_systems = load_payer_systems()
        selectable = _get_selectable_systems(payer_systems=payer_systems)
        selectable_ids = {system["id"] for system in selectable}
        self.assertNotIn("FPI", selectable_ids)


class TestReferenceDataLoading(unittest.TestCase):
    """The systems list must be loaded at runtime from the reference JSON."""

    def test_load_payer_systems_returns_entries(self):
        payer_systems = load_payer_systems()
        self.assertIsInstance(payer_systems, list)
        self.assertGreater(len(payer_systems), 0)

    def test_expected_system_ids_present(self):
        payer_systems = load_payer_systems()
        system_ids = {system["id"] for system in payer_systems}
        for expected_id in (
            "FPI",
            "NAIC_ID",
            "HIOS_ID",
            "LEI",
            "STATE_DOI_ID",
            "CMS_CONTRACT_ID",
            "X12_PAYER_ID",
            "LEGAL_NAME_HASH",
            "PAYER_NAME",
        ):
            self.assertIn(expected_id, system_ids)

    def test_get_system_by_id(self):
        naic_system = get_system_by_id(system_id="NAIC_ID")
        self.assertIsNotNone(naic_system)
        self.assertEqual(naic_system["id"], "NAIC_ID")
        self.assertIsNone(get_system_by_id(system_id="NoSuchSystemBecauseTesting"))


if __name__ == "__main__":
    unittest.main(verbosity=2)