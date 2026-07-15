from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CreationContractV3GuidanceTests(unittest.TestCase):
    def test_meta_copy_contains_canonical_wrapped_examples(self) -> None:
        text = (ROOT / "skills/meta-copy/SKILL.md").read_text(encoding="utf-8")
        for term in (
            '"creation_contract_version":3',
            '"request_mode":"single"',
            '"request_mode":"grouped"',
            '"source_ad_id"',
            '"campaign_count"',
            '"adset_count"',
            '"ads_per_adset"',
            '"grouped_plan"',
            '"campaigns"',
            '"adsets"',
            '"ads"',
            '"campaign_name"',
            '"adset_name"',
            '"ad_name"',
            "adsagent://guide/creation-contract",
            "adsagent://guide/name-contract",
        ):
            self.assertIn(term, text)
        self.assertNotIn('"name":', text)

    def test_recovery_is_prepare_only_and_bounded_to_one_correction(self) -> None:
        corpus = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in (
                "skills/meta-copy/SKILL.md",
                "skills/adsagent-reliability/SKILL.md",
                "skills/adsagent-router/SKILL.md",
            )
        )
        self.assertIn("adsagent_request_incomplete", corpus)
        self.assertIn("invalid_fields", corpus)
        self.assertIn("prepare once", corpus)
        self.assertIn("Never reuse", corpus)
        self.assertIn("support_ref", corpus)

    def test_public_pack_does_not_expose_meta_adapter_raw_fields_as_inputs(self) -> None:
        text = (ROOT / "skills/meta-copy/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Never substitute Meta raw", text)
        self.assertNotIn('"application_id":', text)
        self.assertNotIn('"object_store_url":', text)
        self.assertNotIn('"app_link":', text)


if __name__ == "__main__":
    unittest.main()
