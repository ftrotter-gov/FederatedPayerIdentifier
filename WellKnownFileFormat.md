Payer Plan well-known Endpoint JSON format
==================

What follows is a FHIR-ish well-known file format for handling well-known data for payers.
It is inspired [from a file suggested by the Davinci Hrex Project](https://build.fhir.org/ig/HL7/davinci-ehrx/en/Binary-Wellknown.html), and has been forked and extended to serve the needs of the NDH/NPD use-case.

This page will use a javascript block to use javascript comments to markup what the JSON example for this well-known file;

```javascript

well_known_payer_json = {

  "copied_from_url": null, //eventually this will mark where this well-known file was downloaded from.
                            //once a given well-known url has an established copied_from_url value.. the well-known file will be copied down nightly and committed to the
                            //git repo.. as long as it passes automated sanity checks. From there, the underlying data will be copied into NPD. 

  "resourceType": "http://hl7.org/fhir/us/fast-ndh/StructureDefinition/NDHPayerWellknownDefinition", // a FHIR-ish resourcetype not sure we want to keep this...

  //is_seeded marks whether this file is still pure output of an automated seeding process.
  //the seeders set this to true. The moment a human (or any curation tool) edits the file,
  //it must be set to false, and from then on the seeders will never overwrite anything in
  //this payer's directory.
  "is_seeded": false,

  //the first block is all about the payer itself. 
  "payerLegalName": "Example Payer Legal Name, LLC",
  "payerContactWebsite": "https://example.com/our_contact_page/",

  //this is the place where the enumeration and crosswalk of payer identifiers is solved. 

  "identifier": [
    {
            //the first identifier is the Federated Payer Identifier, which is the system of payer-self-enumeration.
            //there can only be one of these identifiers in the file and it should be the first one.
            //this entry has four components: system, value, fpi_source_system, and fpi_source_value.
            //this system is what marks this identifier as the FPI.
      "system": "https://directory.cms.gov/payer_identification_system/fpi",
            //the following must be a uuid of some kind.
            //it is recommended that it be a uuid generated from an existing and/or reliable payer identification system
            //(see GeneratingFederatedPayerIdentifiers.md and tools/FPI_maker_cli.py, which is the one and only
            //home of FPI uuid generation logic in this project).
            //but it can be any string that validates as a uuid. Because of this later optionality, there will be a first-come-first-serve policy on valid uuid values here.
            //this particular uuid is generated from the (fictional) NAIC company code below:
            //  system_uuid = uuid5(NAMESPACE_DNS, "NAIC_ID.fhir")
            //  fpi         = uuid5(system_uuid, "12345")
      "value": "13e068e1-cd54-5baa-b7e3-79761afe7afc",
            //fpi_source_system records which payer identifier system was used to generate the FPI uuid.
            //it must be one of the "system" urls from reference_data/current_payer_identification_systems.json
            //(but never the fpi system itself — you cannot derive an FPI from another FPI).
            //NOTE: do not default to CMS contract numbers here. Contract numbers identify contracts,
            //not payer legal entities — one payer can hold many contracts, and contracts can move
            //between payers. This repo's seeding process derives seeded FPIs from the LEGAL_NAME_HASH
            //system instead (a temporary hack — the legal name is the only payer attribute reliably
            //available to CMS at seed time). Payers replacing a seeded FPI should prefer entity-level
            //systems such as NAIC_ID, HIOS_ID, LEI, EIN, or a state-prefixed STATE_DOI_ID.
      "fpi_source_system": "https://directory.cms.gov/payer_identification_system/naic_id",
            //fpi_source_value records the identifier value (within fpi_source_system) that was hashed to produce the FPI uuid.
            //for state-level systems (e.g. STATE_DOI_ID) this value must carry the two-letter state prefix, e.g. "TX-68775".
      "fpi_source_value": "12345"
    },

    //after this, please list all of the payer identifiers for your company that exist in other payer identifier systems.
    //the "system" url must come from reference_data/current_payer_identification_systems.json —
    //that file is the current enumeration of the available payer identifier systems
    //(i.e. NAIC company codes, CMS contract IDs, HIOS, EIN, LEI, X12 payer IDs, etc).
    //each entry may optionally carry "notes" (free text), "lookup_url" (a url where the
    //identifier can be verified), and "expiration" ("current" or an expiration date) fields.
    {
      "system": "https://directory.cms.gov/payer_identification_system/naic_id",
      "value": "12345",
      "notes": "NAIC company code for Example Payer Legal Name, LLC.",
      "expiration": "current"
    },
    {
      "system": "https://directory.cms.gov/payer_identification_system/cms_contract_id",
      "value": "H1234",
      "notes": "Medicare Advantage contract held by this payer. Contract IDs are listed here as crosswalk identifiers only; they are not FPI sources.",
      "expiration": "current"
    }
  ],

  //payer_level_string_search_matches is scoped to the payer itself (not any specific plan or endpoint set).
  //these are the strings that, when found on an insurance card or in a claim, should be used to match
  //this payer entity as a whole. This is useful for routing logic that operates at the payer level,
  //before any plan-specific resolution is needed.
  "payer_level_string_search_matches": [
      "Example Payer Legal Name",
      "Example Payer",
      "EPL Insurance",
      "Example Payer Name LLC"
  ],


    //one payer legal entity can have multiple plans, but only ONE well-known file.
    //from the perspective of this file, a given set of plans belongs in the same plan group, if they have exactly the same set of endpoints links.
    //different set of endpoint links, mean different plan_group — as another entry in this same plan_groups array,
    //never as a separate well-known file.

  "plan_groups": [{
    // in this example file, we have several Medicare Plan IDs that makeup the plans in this plan_group.
    // the medicare plan system url shown here is the one used by the seeded files: the value is the
    // CMS contract ID plus the plan segment, joined by a hyphen (e.g. "H1234-432").
    "plan_identifiers": [
        {
            "system": "https://directory.cms.gov/payer_identification_system/cms_contract_id/plan/plan_id",
            "value": "H1234-432",
            "plan_name": "This Very Good Plan",
            "plan_website": "https://example.com/plan_432", //TODO should this go here or down below? Both for now. 
            //plan_level_string_search_matches is scoped to this specific plan identifier entry.
            //each plan identifier has its own list because different plans may appear under different
            //names or abbreviations on insurance cards, EOBs, or claim submissions.
            //these strings are used for plan-level routing and matching, distinct from payer-level
            //or plan-group-level matching.
            "plan_level_string_search_matches": [
                "This Very Good Plan",
                "Very Good Plan Basic",
                "TVG Plan 432"
            ]
        },
        {
            "system": "https://directory.cms.gov/payer_identification_system/cms_contract_id/plan/plan_id",
            "value": "H1234-433",
            "plan_name": "This Very Good Plan Preferred",
            "plan_website": "https://example.com/plan_433",
            //each plan identifier carries its own plan_level_string_search_matches list.
            //the strings here may overlap with other plans' lists, but each plan maintains its own
            //authoritative set of matching strings for routing to its specific plan context.
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
            "plan_name": "This Very Good Plan Excel",
            "plan_website": "https://example.com/plan_434",
            //likewise, plan 434 has its own distinct (though possibly overlapping) list of strings.
            "plan_level_string_search_matches": [
                "This Very Good Plan Excel",
                "Very Good Plan Excel",
                "TVG Plan 434",
                "Very Good Excel"
            ]
        },                         
        ],


        //this is the place where we reconcile all of the "on the insurance card" information that should route to these 
        //endpoints. plan_group_string_search_match is scoped to the entire plan_group — these are the
        //strings that are shared by every plan in this group (they apply across all plans in this group
        //and across all endpoints defined below). Strings that identify the payer as a whole belong in
        //payer_level_string_search_matches above instead.
        "plan_group_string_search_match": [
            "Example payer name",
            "Example payer name example state name"
        ],
    
        //There is only one set of plan endpoints per plan_group.
        //Endpoint value semantics:
        //  - a url string  = the endpoint exists at that url.
        //  - null          = the payer affirmatively states that this endpoint does NOT exist
        //                    (verified-absent — do not go looking for it).
        //  - key absent    = unknown; nobody has yet determined whether this endpoint exists.
        "plan_endpoints": {


            //endpoints to support prior authorization
            "davinci_crd_hook_endpoint#1.1": "http://example.org/foo/bar/crd",
            "davinci_crd_hook_endpoint#1.2": null, //this payer has verified that no CRD 1.2 endpoint exists.
            "davinci_dtr_qpackage_endpoint#1.2": "http://example.org/foo/bar/dtr",
            "davinci_pas_submission_endpoint#1.2": "http://example.org/foo/bar/pas2",
            "davinci_cdex_attachsubmit_endpoint#2.1" : "https://example.com/clinicaldataexchange/v1/",

            //endpoints needed to support ndh records
            "ndh_meta_fhir_signup_url": "http://example.org/fhir_signup/",
            "ndh_meta_documentation_url": "http://example.org/fhir_docs/",

            //provider directory endpoints
            "davinci_pdex_provider_directory_endpoint#1.1": "http://example.org/foo/bar/provider-directory",
            "davinci_pdex_provider_directory_endpoint_all_at_once#1.1": "http://example.org/foo/bar/provider-directory/all_at_once.ndjson.zip",  

            //provider access endpoints
            "davinci_provider_payer_access_endpoint#1.1": "http://example.org/foo/bar/provider-payer-access",

            //payer to payer endpoints
            "davinci_payer_to_payer_endpoint#1.1": "http://example.org/foo/bar/payer-to-payer",

            //patient service endpoints
                //carin bluebutton endpoints
            "carin_bluebutton_endpoint#1.0" : "https://example.org/fhir/v3/patientaccess/",
            "carin_bluebutton_endpoint#1.0_uscore3.1" : "https://example.org/fhir/v2/patientaccess/",

                //davinci patient access endpoints
            "davinci_pdex_patient_endpoint#2.0" : "https://example.org/fhir/v3/patientaccess/",
            "davinci_pdex_patient_endpoint#2.0_uscore3.1" : "https://example.org/fhir/v2/patientaccess/",

                //formulary endpoints
            "davinci_pdex_formulary_endpoint#2.0" : "https://example.org/fhir/v3/patientaccess/",

                //real time pharmacy benefit checks
            "carin_rtpbc_member_endpoint#1.0" : "https://example.org/fhir/v1/realtimepharmacybenefitcheck/",
            "carin_rtpbc_provider_endpoint#1.0" : "https://example.org/realtimepharmacybenefitcheck/v1/",


            //non FHIR endpoints
                //transparency in coverage data
            "tic_table_of_contents#issuer-11111": "https://example.com/mrf/2025-01-01_example-payer_issuer-a_index.json",
            "tic_table_of_contents#issuer-22222": "https://example.com/mrf/2025-01-01_example-payer_issuer-b_index.json",

                //these are not FHIR endpoints, but just websites
            "payer_homepage": "https://example.com",

                //TODO not sure if this should go here, or in the plan section or both.
            "plan_homepage#432": "https://example.com/plan_432",
            "plan_homepage#433": "https://example.com/plan_432",


            //things we might add here in the future: 
                //Direct endpoints
                //Further FHIR endpoints
                //other open data mandated urls (i.e. tic)
                //etc!
                //web versions of forumlaries or directories.


        }
  }
]
}
```
