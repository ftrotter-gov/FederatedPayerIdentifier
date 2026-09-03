# Supporting Multiple Federated Payer Identifiers in a Single Payer Well-Known File

## Purpose

The current Payer Plan well-known JSON format assumes that a file describes a single Federated Payer Identifier (FPI). The `identifier` array contains one FPI followed by other payer identifiers, while payer legal name, payer contact information, and payer-level search strings are stored at the top level of the file. Individual plan identifiers do not explicitly identify the FPI to which they belong.

This specification defines a small extension to the existing format that allows **multiple FPIs to be represented in a single well-known file**.

The fundamental FPI rule does not change:

**Each FPI represents one legal payer entity that performs contracting.**

A single well-known file may describe multiple such legal entities when those entities share a common technical or organizational publishing location.

The goal of this change is to support multiple FPIs without substantially restructuring the existing well-known file format.

## 1. Identify FPI Records Explicitly

Each entry in the top-level `identifier` array SHALL include an `is_fpi` Boolean property.

For example:

```json
{
  "system": "https://directory.cms.gov/payer_identification_system/fpi",
  "value": "5e4c4d18-0725-58ce-9477-d8482ea11016",
  "is_fpi": true
}
```

The value SHALL have the following meaning:

* `is_fpi: true` means that the identifier is an FPI representing a legal payer entity.
* `is_fpi: false` means that the identifier is another payer identifier associated with one of the FPIs represented in the file.

There MAY be multiple identifier entries for which `is_fpi` is `true`.

This replaces the current assumption that the first identifier in the `identifier` array is the one and only FPI.

The `is_fpi` property is intentionally named differently from a `parent_fpi` reference. `is_fpi` is a Boolean describing the identifier record itself, while `parent_fpi` is used on both non-FPI payer identifiers and plan identifiers to reference a specific FPI UUID.

## 2. Associate Non-FPI Identifiers With a Parent FPI

Every identifier for which:

```json
"is_fpi": false
```

SHALL include a `parent_fpi` property.

The value of `parent_fpi` SHALL be the UUID of the FPI representing the legal payer entity to which the identifier belongs.

For example:

```json
{
  "system": "https://directory.cms.gov/payer_identification_system/cms_contract_id",
  "value": "H0028",
  "is_fpi": false,
  "parent_fpi": "5e4c4d18-0725-58ce-9477-d8482ea11016"
}
```

The referenced FPI MUST appear in the same well-known file as an identifier for which:

```json
"is_fpi": true
```

This creates an explicit identifier crosswalk for each payer entity represented in the file.

For example, if a file contains three FPIs and several HIOS, Medicare Advantage contract, HPID, GLEIF, or other identifiers, every non-FPI identifier can be unambiguously associated with the appropriate legal payer entity.

## 3. Move Payer Metadata Into the FPI Identifier Record

The current format stores payer-specific information at the top level of the file, including:

* `payerLegalName`
* `payerContactWebsite`
* `payer_level_string_search_matches`

This works when a file represents only one payer legal entity. It becomes ambiguous when a file contains multiple FPIs.

These properties SHALL therefore be moved into each identifier record for which `is_fpi` is `true`.

For example:

```json
{
  "system": "https://directory.cms.gov/payer_identification_system/fpi",
  "value": "5e4c4d18-0725-58ce-9477-d8482ea11016",
  "is_fpi": true,

  "payerLegalName": "Example Payer Legal Name, LLC",

  "payerContactWebsite": "https://example.com/contact/",

  "payer_level_string_search_matches": [
    "Example Payer Legal Name",
    "Example Payer",
    "EPL Insurance"
  ],

  "fpi_source_system":
    "https://directory.cms.gov/payer_identification_system/cms_contract_id",

  "fpi_source_value": "H0028"
}
```

The following fields therefore become properties of an FPI identifier:

* `payerLegalName`
* `payerContactWebsite`
* `payer_level_string_search_matches`
* `fpi_source_system`
* `fpi_source_value`

This ensures that each legal payer entity has its own identity, contact, matching, and FPI provenance information.

The existing `fpi_source_system` and `fpi_source_value` semantics do not change. They continue to describe the source identifier used to generate the FPI UUID.

## 4. Associate Every Plan With an FPI

Every entry in `plan_identifiers` SHALL include a `parent_fpi` property.

The value of `parent_fpi` SHALL be the UUID of the FPI representing the legal payer entity associated with that plan. Using `parent_fpi` here mirrors the same field name used on non-FPI payer identifiers, making the relationship consistent across both identifier and plan contexts.

For example:

```json
{
  "system": "http://example.org/plan_identifier",
  "value": "432",

  "parent_fpi": "5e4c4d18-0725-58ce-9477-d8482ea11016",

  "plan_name": "This Very Good Plan",

  "plan_website": "https://example.com/plan_432",

  "plan_level_string_search_matches": [
    "This Very Good Plan",
    "Very Good Plan Basic",
    "TVG Plan 432"
  ]
}
```

The referenced FPI MUST appear in the same well-known file in an identifier record for which:

```json
"is_fpi": true
```

This creates an explicit relationship:

**Plan → parent_fpi → FPI → Legal payer entity**

It also removes the need to infer which payer owns or contracts for a particular plan based on the file in which the plan happens to appear.

## 5. FPI and Plan Identifier Validation

A conforming multi-FPI well-known file SHALL satisfy the following rules:

1. At least one entry in `identifier` MUST have `is_fpi: true`.
2. Every identifier entry MUST contain `is_fpi`.
3. Every identifier with `is_fpi: false` MUST contain `parent_fpi`.
4. Every `parent_fpi` MUST resolve to the `value` of an identifier in the same file for which `is_fpi: true`.
5. Every plan identifier MUST contain a `parent_fpi`.
6. Every plan identifier's `parent_fpi` MUST resolve to the `value` of an identifier in the same file for which `is_fpi: true`.
7. `payerLegalName`, `payerContactWebsite`, and `payer_level_string_search_matches` SHALL be associated with an FPI identifier rather than applying globally to all FPIs in the file.

These requirements allow consumers to validate all payer and plan relationships without relying on array order or implicit file-level assumptions.

## 6. Plan Groups

The existing `plan_group` concept can remain largely unchanged.

A plan group represents a set of plans that share the same endpoint set. Multiple plan groups can therefore continue to exist within a single well-known file.

Each plan within a plan group identifies its associated legal payer entity through its `parent_fpi` property.

For the initial multi-FPI implementation:

**All plans within a `plan_group` SHOULD reference the same FPI.**

This preserves the existing conceptual relationship between a payer, its plans, and the endpoints associated with those plans.

If a future use case requires a single plan group to contain plans associated with multiple FPIs, that use case should be specified explicitly rather than inferred.

## 7. Plan-Group Search Strings

The existing format contains:

```json
"plan_group_and_payer_level_string_search_matches"
```

This field currently combines plan-group and payer-level matching semantics.

Because payer-level matching becomes FPI-specific under the multi-FPI model, implementations SHOULD treat payer-specific search strings as belonging to the FPI's `payer_level_string_search_matches`.

The plan-group field can continue to contain search strings that apply to the plan group as a whole.

A future revision MAY rename or further separate this field so that plan-group matching and payer/FPI matching are completely distinct.

For this initial change, however, no additional structural modification is required beyond moving payer-level search strings into the appropriate FPI identifier record.

## 8. Endpoint Structure

No change to the existing `plan_endpoints` structure is required.

Endpoints continue to be associated with plan groups.

The relationship can therefore be resolved as:

**Endpoint → Plan Group → Plan → FPI → Legal payer entity**

This allows different FPIs in the same well-known file to have different plan groups and different endpoint sets without requiring changes to the existing endpoint representation.

## 9. Simplified Multi-FPI Example

A simplified file containing two FPIs could look as follows:

```json
{
  "resourceType":
    "http://hl7.org/fhir/us/fast-ndh/StructureDefinition/NDHPayerWellknownDefinition",

  "identifier": [
    {
      "system":
        "https://directory.cms.gov/payer_identification_system/fpi",

      "value":
        "11111111-1111-5111-8111-111111111111",

      "is_fpi": true,

      "payerLegalName":
        "Example Health Insurance Company, Inc.",

      "payerContactWebsite":
        "https://example.com/contact",

      "payer_level_string_search_matches": [
        "Example Health",
        "Example Health Insurance"
      ],

      "fpi_source_system":
        "https://directory.cms.gov/payer_identification_system/cms_contract_id",

      "fpi_source_value":
        "H1111"
    },

    {
      "system":
        "https://directory.cms.gov/payer_identification_system/cms_contract_id",

      "value":
        "H1111",

      "is_fpi": false,

      "parent_fpi":
        "11111111-1111-5111-8111-111111111111"
    },

    {
      "system":
        "https://directory.cms.gov/payer_identification_system/fpi",

      "value":
        "22222222-2222-5222-8222-222222222222",

      "is_fpi": true,

      "payerLegalName":
        "Example Health of Texas, Inc.",

      "payerContactWebsite":
        "https://example.com/texas/contact",

      "payer_level_string_search_matches": [
        "Example Health Texas",
        "Example Health of Texas"
      ],

      "fpi_source_system":
        "https://directory.cms.gov/payer_identification_system/state_doi_id",

      "fpi_source_value":
        "TX-12345"
    },

    {
      "system":
        "https://directory.cms.gov/payer_identification_system/state_doi_id",

      "value":
        "TX-12345",

      "is_fpi": false,

      "parent_fpi":
        "22222222-2222-5222-8222-222222222222"
    }
  ],

  "plan_groups": [
    {
      "plan_identifiers": [
        {
          "system":
            "http://example.org/plan_identifier",

          "value":
            "432",

          "parent_fpi":
            "11111111-1111-5111-8111-111111111111",

          "plan_name":
            "Example Gold",

          "plan_website":
            "https://example.com/gold",

          "plan_level_string_search_matches": [
            "Example Gold",
            "Example Health Gold"
          ]
        }
      ],

      "plan_group_and_payer_level_string_search_matches": [
        "Example Health Gold"
      ],

      "plan_endpoints": {
        "davinci_pdex_provider_directory_endpoint#1.1":
          "https://example.com/fhir/provider-directory"
      }
    },

    {
      "plan_identifiers": [
        {
          "system":
            "http://example.org/plan_identifier",

          "value":
            "987",

          "parent_fpi":
            "22222222-2222-5222-8222-222222222222",

          "plan_name":
            "Example Texas Gold",

          "plan_website":
            "https://example.com/texas/gold",

          "plan_level_string_search_matches": [
            "Example Texas Gold",
            "Example Health Texas Gold"
          ]
        }
      ],

      "plan_group_and_payer_level_string_search_matches": [
        "Example Health Texas"
      ],

      "plan_endpoints": {
        "davinci_pdex_provider_directory_endpoint#1.1":
          "https://texas.example.com/fhir/provider-directory"
      }
    }
  ]
}
```

## 10. Summary of Required Changes

Supporting multiple FPIs in a single well-known file requires the following changes to the current format:

1. **Add `is_fpi` to every payer identifier.**

   `is_fpi` is a Boolean indicating whether that identifier is itself an FPI.

2. **Allow multiple FPI identifier records.**

   Multiple entries in `identifier` MAY have:

   ```json
   "is_fpi": true
   ```

3. **Add `parent_fpi` to non-FPI identifiers.**

   Every identifier with:

   ```json
   "is_fpi": false
   ```

   MUST contain a `parent_fpi` referencing an FPI declared in the same file.

4. **Move payer-specific metadata into the FPI identifier.**

   This includes:

   * `payerLegalName`
   * `payerContactWebsite`
   * `payer_level_string_search_matches`

5. **Retain FPI provenance metadata on each FPI.**

   Each FPI can continue to contain:

   * `fpi_source_system`
   * `fpi_source_value`

6. **Add a `parent_fpi` reference to every plan identifier.**

   The value identifies the legal payer entity associated with the plan. Using `parent_fpi` mirrors the field name used on non-FPI payer identifiers for consistency.

7. **Require all FPI references to resolve locally.**

   Both `parent_fpi` on payer identifiers and `parent_fpi` on plan identifiers MUST reference an FPI declared in the same well-known file.

8. **Keep plan groups FPI-homogeneous initially.**

   All plans within a plan group SHOULD reference the same FPI unless cross-FPI plan-group semantics are explicitly defined in a future version.

9. **Leave the endpoint structure unchanged.**

   Existing plan-group endpoint definitions can continue to operate without modification.

## Implementation Plan

### Scope
- **Deliverable 1**: Rewrite `WellKnownFileFormat.md` to document the new format.
- **Deliverable 2**: Rewrite `example_wellknown_payer_index.json` with two FPIs.

This is a **non-backward-compatible** format change. The new format replaces the old one entirely. `payerLegalName`, `payerContactWebsite`, and `payer_level_string_search_matches` are removed from the top level of the file; they live only inside the FPI identifier entry.

### Field Name Note

There is a field name mismatch between this proposal and the existing files:

- This proposal (Section 7) references `plan_group_and_payer_level_string_search_matches`
- The existing `example_wellknown_payer_index.json` uses `plan_group_string_search_match` (shorter, already accurate once payer-level strings move into the FPI identifier)

The implementation uses `plan_group_string_search_match` (the existing shorter name) in both the format doc and the example.

---

### Deliverable 1 — `WellKnownFileFormat.md`

The annotated JavaScript block will be rewritten to reflect the new format. Key changes:

**1. Remove top-level payer metadata fields**
Remove `payerLegalName`, `payerContactWebsite`, and `payer_level_string_search_matches` from the top level of the file entirely. They are no longer valid at the file root.

**2. Rewrite the `identifier` array section**
- Every entry in `identifier` MUST have an `is_fpi` Boolean.
- Entries with `"is_fpi": true` are FPI records. These carry:
  - `payerLegalName`
  - `payerContactWebsite`
  - `payer_level_string_search_matches`
  - `fpi_source_system` (optional, for UUIDv5-derived FPIs)
  - `fpi_source_value` (optional, for UUIDv5-derived FPIs)
- Entries with `"is_fpi": false` are crosswalk identifiers. These MUST carry `parent_fpi` (the UUID of the owning FPI, which must appear in the same file).
- There MAY be multiple entries with `"is_fpi": true`.

**3. Rewrite the `plan_identifiers` section**
- Every plan identifier entry MUST include `"parent_fpi"` — the UUID of the FPI representing the legal entity that owns the plan.
- The referenced FPI MUST appear in the same file as an identifier with `"is_fpi": true`.

**4. Add a validation rules section**
Summarize the 7 required validation rules (from Section 5 of this proposal) so format consumers know what a conforming file must satisfy.

**5. Leave `plan_endpoints` and `plan_group_string_search_match` unchanged**
No structural changes to endpoints or plan-group search strings.

**6. Update the "Repository Seeding Implementation Note"**
Note that `is_seeded` remains unchanged. Add a note that the seeder has not yet been updated to emit the new multi-FPI fields.

---

### Deliverable 2 — `example_wellknown_payer_index.json`

Replace the current single-FPI example with a richer **two-FPI file**, based on the simplified example from Section 9 of this proposal but using the fuller endpoint and plan structure from the current file.

The new example will:

**Identifier block (4 entries):**
1. FPI `is_fpi: true` for "Example Health Insurance Company, Inc." — includes `payerLegalName`, `payerContactWebsite`, `payer_level_string_search_matches`, `fpi_source_system`, `fpi_source_value`
2. NAIC ID `is_fpi: false` with `parent_fpi` → FPI 1
3. FPI `is_fpi: true` for "Example Health of Texas, Inc." — includes `payerLegalName`, `payerContactWebsite`, `payer_level_string_search_matches`, `fpi_source_system`, `fpi_source_value`
4. State DOI ID `is_fpi: false` with `parent_fpi` → FPI 2

**Plan groups (2 groups):**
- Plan group 1: Plans belonging to FPI 1, each with `"parent_fpi": "<FPI-1-uuid>"`, with the full existing endpoint set
- Plan group 2: Plans belonging to FPI 2, each with `"parent_fpi": "<FPI-2-uuid>"`, with a different endpoint URL to show plan-group separation

**Retain existing keys**: `copied_from_url`, `resourceType`, `is_seeded`

**Remove from top level**: `payerLegalName`, `payerContactWebsite`, `payer_level_string_search_matches`

---

### Order of Work

1. Append this implementation plan to `AI_Instructions/MultipleFPIPerFileProposal.md`.
2. Update `WellKnownFileFormat.md` — the format spec is the source of truth.
3. Update `example_wellknown_payer_index.json` — must conform exactly to what was documented in step 2.

---

## Resulting Model

With these changes, a well-known file no longer represents a single payer legal entity. Instead, it represents a collection of one or more related payer legal entities and their plans.

The resulting hierarchy is:

**Well-Known File**

→ **FPI / Contracting Legal Entity**

→ **Other Payer Identifiers**

→ **Plans**

→ **Plan Groups**

→ **Endpoints**

The fundamental identity rule remains unchanged:

**One FPI represents one contracting legal entity.**

The change simply permits multiple such FPIs to be published in a single well-known file while ensuring that every payer identifier and every plan can be unambiguously associated with the correct FPI.
