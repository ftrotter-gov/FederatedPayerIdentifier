# Payer Plan Well-Known Index JSON Format

The payer well-known index connects a payer-controlled publication location to
the payer's identity, plans, and interoperability endpoints. Those endpoints
may be hosted by the payer or by an outsourced FHIR vendor. This bridge is a
central purpose of the format.

The format is FHIR-inspired and builds on the
[Da Vinci HRex well-known proposal](https://build.fhir.org/ig/HL7/davinci-ehrx/en/Binary-Wellknown.html).
It is not currently a formal FHIR resource or a JSON Schema. There is one
current version of the format, maintained through Git history. Protocol and
FHIR versions in endpoint keys do not version the index itself.

A well-known file represents one or more legal payer entities and their plans.
Each legal payer entity is identified by a Federated Payer Identifier (FPI).
The file may contain multiple FPIs when those entities share a common
technical or organizational publishing location.

The annotated JavaScript block below documents the current shape. A future
Python validator will enforce semantic rules that cannot be expressed through
JSON structure alone. Until those rules are adopted, this document avoids
assigning universal meaning to every possible null or URL form. See
[Future Steps](FutureSteps.md).

```javascript

well_known_payer_json = {

  "copied_from_url": null, //Eventually this records the payer-controlled URL
                            //from which this working copy was downloaded.
                            //The repository is the initial trusted working copy;
                            //accepted content is intended to be republished by NPD.

  "resourceType": "http://hl7.org/fhir/us/fast-ndh/StructureDefinition/NDHPayerWellknownDefinition", // a FHIR-ish resourcetype not sure we want to keep this...

  // NOTE: payerLegalName, payerContactWebsite, and payer_level_string_search_matches
  // are NO LONGER top-level fields. They now live inside each FPI identifier entry
  // (see the identifier array below). This is a non-backward-compatible format change.

  // The identifier array is the enumeration and crosswalk of payer identifiers.
  // Each entry MUST include an "is_fpi" Boolean.
  //
  // Validation rules for a conforming file:
  //   1. At least one entry in "identifier" MUST have is_fpi: true.
  //   2. Every identifier entry MUST contain "is_fpi".
  //   3. Every identifier with is_fpi: false MUST contain "parent_fpi".
  //   4. Every "parent_fpi" MUST resolve to the "value" of an entry in this
  //      file for which is_fpi: true.
  //   5. Every plan identifier MUST contain "fpi".
  //   6. Every plan identifier's "fpi" MUST resolve to the "value" of an entry
  //      in this file for which is_fpi: true.
  //   7. payerLegalName, payerContactWebsite, and payer_level_string_search_matches
  //      MUST appear inside an FPI identifier entry, not at the file root.

  "identifier": [
    {
            // An FPI identifier entry: is_fpi is true.
            // There may be multiple FPI entries in the same file.
            // The "system" URL below is what marks this identifier as the FPI.
      "system": "https://directory.cms.gov/payer_identification_system/fpi",
            // The value must be a UUID selected and self-issued by the payer.
            // The payer may choose a UUID generated from an existing payer
            // identification system (see GeneratingFederatedPayerIdentifiers.md
            // and tools/FPI_maker_cli.py, which is the one and only home of FPI
            // uuid generation logic in this project), or another accepted UUID
            // version. Registration rejects UUIDs that have already been claimed.
            // This particular uuid is generated from the (fictional) NAIC company
            // code below:
            //   system_uuid = uuid5(NAMESPACE_DNS, "NAIC_ID.fhir")
            //   fpi         = uuid5(system_uuid, "12345")
      "value": "13e068e1-cd54-5baa-b7e3-79761afe7afc",

            // is_fpi: true marks this identifier as an FPI representing a legal
            // payer entity. This is a required Boolean on every identifier entry.
      "is_fpi": true,

            // payerLegalName, payerContactWebsite, and payer_level_string_search_matches
            // are now properties of the FPI identifier entry, not the file root.
            // Each FPI has its own set of these fields for its legal entity.
      "payerLegalName": "Example Payer Legal Name, LLC",
      "payerContactWebsite": "https://example.com/our_contact_page/",

            // payer_level_string_search_matches is scoped to this FPI's legal entity.
            // These are the strings that, when found on an insurance card or in a
            // claim, should be used to match this payer entity as a whole. Useful
            // for routing logic that operates at the payer level before any
            // plan-specific resolution is needed.
      "payer_level_string_search_matches": [
          "Example Payer Legal Name",
          "Example Payer",
          "EPL Insurance",
          "Example Payer Name LLC"
      ],

            // fpi_source_system records which payer identifier system was used to
            // generate a UUIDv5 FPI. It is metadata about FPI generation and is
            // valid only on an FPI entry (is_fpi: true). It must be one of the
            // "system" urls from reference_data/current_payer_identification_systems.json
            // (but never the fpi system itself — you cannot derive an FPI from
            // another FPI).
            // NOTE: do not default to CMS contract numbers here. Contract numbers
            // identify contracts, not payer legal entities — one payer can hold
            // many contracts, and contracts can move between payers. The payer
            // chooses whether to use another accepted UUID version or any supported
            // source identifier.
      "fpi_source_system": "https://directory.cms.gov/payer_identification_system/naic_id",
            // fpi_source_value records the identifier value (within fpi_source_system)
            // that was hashed to produce the FPI UUID. Valid only on FPI entries.
            // For state-level systems (e.g. STATE_DOI_ID) this value must carry the
            // two-letter state prefix, e.g. "TX-68775".
      "fpi_source_value": "12345"
    },

    // After each FPI entry, list payer routing and crosswalk identifiers that
    // exist in other payer identifier systems. These non-FPI entries have
    // is_fpi: false and MUST include a "parent_fpi" referencing the UUID of
    // the FPI to which they belong. The referenced FPI MUST appear in this
    // same file as an entry with is_fpi: true.
    //
    // Non-FPI entries MUST NOT contain fpi_source_system or fpi_source_value.
    // Those two fields describe how the FPI was generated; they do not describe
    // routing identifiers.
    //
    // The "system" url must come from reference_data/current_payer_identification_systems.json.
    // Each entry may optionally carry "notes" (free text), "lookup_url" (a url
    // where the identifier can be verified), and "expiration" ("current" or an
    // expiration date) fields.
    {
      "system": "https://directory.cms.gov/payer_identification_system/naic_id",
      "value": "12345",
      "is_fpi": false,
      "parent_fpi": "13e068e1-cd54-5baa-b7e3-79761afe7afc",
      "notes": "NAIC company code for Example Payer Legal Name, LLC.",
      "expiration": "current"
    },
    {
      "system": "https://directory.cms.gov/payer_identification_system/cms_contract_id",
      "value": "H1234",
      "is_fpi": false,
      "parent_fpi": "13e068e1-cd54-5baa-b7e3-79761afe7afc",
      "notes": "Medicare Advantage contract held by this payer. Contract IDs are listed here as crosswalk identifiers only; they are not FPI sources.",
      "expiration": "current"
    }

    // A file may contain multiple FPI entries. For example, a second legal
    // entity published at the same location would appear here as another
    // entry with is_fpi: true, followed by its own crosswalk identifiers
    // with is_fpi: false and parent_fpi pointing to that FPI's UUID.
    // See example_wellknown_payer_index.json for a two-FPI example.
  ],


    // one or more legal payer entities can have multiple plans. A given set of
    // plans belongs in the same plan group if they have exactly the same set of
    // endpoint links. Different endpoint links mean different plan_group entries
    // within this same plan_groups array.
    //
    // All plans within a plan_group SHOULD reference the same FPI.

  "plan_groups": [{
    // In this example file, we have several Medicare Plan IDs that make up the
    // plans in this plan_group.
    // The Medicare plan system URL uses a value consisting of the CMS contract
    // ID plus the plan segment, joined by a hyphen (e.g. "H1234-432").
    "plan_identifiers": [
        {
            "system": "https://directory.cms.gov/payer_identification_system/cms_contract_id/plan/plan_id",
            "value": "H1234-432",

            // fpi is required on every plan identifier. Its value is the UUID of
            // the FPI representing the legal payer entity that owns this plan.
            // The referenced FPI MUST appear in the "identifier" array above as
            // an entry with is_fpi: true.
            "fpi": "13e068e1-cd54-5baa-b7e3-79761afe7afc",

            "plan_name": "This Very Good Plan",
            "plan_website": "https://example.com/plan_432",
            // plan_level_string_search_matches is scoped to this specific plan
            // identifier entry. Each plan identifier has its own list because
            // different plans may appear under different names or abbreviations
            // on insurance cards, EOBs, or claim submissions. These strings are
            // used for plan-level routing and matching, distinct from payer-level
            // or plan-group-level matching.
            "plan_level_string_search_matches": [
                "This Very Good Plan",
                "Very Good Plan Basic",
                "TVG Plan 432"
            ]
        },
        {
            "system": "https://directory.cms.gov/payer_identification_system/cms_contract_id/plan/plan_id",
            "value": "H1234-433",
            "fpi": "13e068e1-cd54-5baa-b7e3-79761afe7afc",
            "plan_name": "This Very Good Plan Preferred",
            "plan_website": "https://example.com/plan_433",
            // Each plan identifier carries its own plan_level_string_search_matches
            // list. The strings here may overlap with other plans' lists, but each
            // plan maintains its own authoritative set of matching strings for
            // routing to its specific plan context.
            "plan_level_string_search_matches": [
                "This Very Good Plan Preferred",
                "Very Good Plan Preferred",
                "TVG Plan 433",
                "Very Good Preferred"
            ]
        },
        {
            "system": "https://directory.cms.gov/payer_identification_system/cms_contract_id/plan/plan_id",
            "value": "H1234-434",
            "fpi": "13e068e1-cd54-5baa-b7e3-79761afe7afc",
            "plan_name": "This Very Good Plan Excel",
            "plan_website": "https://example.com/plan_434",
            // Likewise, plan 434 has its own distinct (though possibly overlapping)
            // list of strings.
            "plan_level_string_search_matches": [
                "This Very Good Plan Excel",
                "Very Good Plan Excel",
                "TVG Plan 434",
                "Very Good Excel"
            ]
        },
        ],


        // plan_group_string_search_match is scoped to the entire plan_group.
        // These are strings shared by every plan in this group (they apply across
        // all plans in this group and across all endpoints defined below).
        // Strings that identify the payer as a whole belong in the FPI identifier's
        // payer_level_string_search_matches instead.
        "plan_group_string_search_match": [
            "Example payer name",
            "Example payer name example state name"
        ],

        // There is only one set of plan endpoints per plan_group.
        // Each protocol-and-version key may occur at most once in this object.
        // For example, #1.1 selects version 1.1 of that protocol; it is not the
        // version of this index file. The future semantic validator will define
        // which keys permit null, what null means in each context, and what kind
        // of URL each key requires. Key omission currently means that the index
        // makes no assertion for that protocol and version.
        "plan_endpoints": {


            // endpoints to support prior authorization
            "davinci_crd_hook_endpoint#1.1": "http://example.org/foo/bar/crd",
            "davinci_crd_hook_endpoint#1.2": null, //Illustrates a nullable value;
                                                    //normative meaning is deferred to validation.
            "davinci_dtr_qpackage_endpoint#1.2": "http://example.org/foo/bar/dtr",
            "davinci_pas_submission_endpoint#1.2": "http://example.org/foo/bar/pas2",
            "davinci_cdex_attachsubmit_endpoint#2.1" : "https://example.com/clinicaldataexchange/v1/",

            // endpoints needed to support ndh records
            "ndh_meta_fhir_signup_url": "http://example.org/fhir_signup/",
            "ndh_meta_documentation_url": "http://example.org/fhir_docs/",

            // provider directory endpoints
            "davinci_pdex_provider_directory_endpoint#1.1": "http://example.org/foo/bar/provider-directory",
            "davinci_pdex_provider_directory_endpoint_all_at_once#1.1": "http://example.org/foo/bar/provider-directory/all_at_once.ndjson.zip",

            // provider access endpoints
            "davinci_provider_payer_access_endpoint#1.1": "http://example.org/foo/bar/provider-payer-access",

            // payer to payer endpoints
            "davinci_payer_to_payer_endpoint#1.1": "http://example.org/foo/bar/payer-to-payer",

            // patient service endpoints
                // carin bluebutton endpoints
            "carin_bluebutton_endpoint#1.0" : "https://example.org/fhir/v3/patientaccess/",
            "carin_bluebutton_endpoint#1.0_uscore3.1" : "https://example.org/fhir/v2/patientaccess/",

                // davinci patient access endpoints
            "davinci_pdex_patient_endpoint#2.0" : "https://example.org/fhir/v3/patientaccess/",
            "davinci_pdex_patient_endpoint#2.0_uscore3.1" : "https://example.org/fhir/v2/patientaccess/",

                // formulary endpoints
            "davinci_pdex_formulary_endpoint#2.0" : "https://example.org/fhir/v3/patientaccess/",

                // real time pharmacy benefit checks
            "carin_rtpbc_member_endpoint#1.0" : "https://example.org/fhir/v1/realtimepharmacybenefitcheck/",
            "carin_rtpbc_provider_endpoint#1.0" : "https://example.org/realtimepharmacybenefitcheck/v1/",


            // non FHIR endpoints
                // transparency in coverage data
            "tic_table_of_contents#issuer-11111": "https://example.com/mrf/2025-01-01_example-payer_issuer-a_index.json",
            "tic_table_of_contents#issuer-22222": "https://example.com/mrf/2025-01-01_example-payer_issuer-b_index.json",

                // these are not FHIR endpoints, but just websites
            "payer_homepage": "https://example.com",

                // TODO not sure if this should go here, or in the plan section or both.
            "plan_homepage#432": "https://example.com/plan_432",
            "plan_homepage#433": "https://example.com/plan_432",


            // things we might add here in the future:
                // Direct endpoints
                // Further FHIR endpoints
                // other open data mandated urls (i.e. tic)
                // etc!
                // web versions of formularies or directories.


        }
  }
]
}
```

## Repository Seeding Implementation Note

Seeding is a repository implementation detail, not a defining part of the
well-known index standard. The `is_seeded` property currently supports that
implementation workflow:

```json
{
  "is_seeded": false
}
```

* `true` marks uncurated output from an automated repository seeder.
* `false` marks a file that has been reviewed or enriched by a person or
  curation process.

General-purpose seeders must not overwrite curated payer directories.
Purpose-specific curation tools should preserve curated facts except for the
fields they explicitly exist to change.

The Medicare Advantage seeder temporarily derives seed FPIs from
`LEGAL_NAME_HASH` because payer legal name is available in its source data.
That mechanism does not define permanent payer identity and is not a
recommendation to payers. A payer self-issuing its FPI chooses either an
accepted generated UUID version or a supported source identifier.

**Note on seeder compatibility:** The Medicare Advantage seeder (`tools/seed_medicare_advantage/seed.py`)
has not yet been updated to emit the new multi-FPI format fields (`is_fpi`,
`parent_fpi` on crosswalk identifiers, or `fpi` on plan identifiers). Seeded
files will not conform to the current format until the seeder is updated.
