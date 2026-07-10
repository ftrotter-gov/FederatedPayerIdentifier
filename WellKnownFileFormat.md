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


  //the first block is all about the payer itself. 
  "payerLegalName": "Example Payer Legal Name, LLC",
  "payerContactWebsite": "https://example.com/our_contact_page/",

  //this is the place where the enumeration and crosswalk of payer identifiers is solved. 

  "identifier": [
    {
            //the first identifier is the Federated Payer Identifier, which is the system of payer-self-enumeration.
            //there can only be one of these identifiers in the file and it should be the first one. 
            //TODO finalize this system
            //this system is what marks this identifier as the FPI. 
      "system": "http://hl7.org/fhir/us/fast-ndh/StructureDefinition/FederatedPayerIdentifier",
            //the following must be a uuid of some kind.
            //it is recommended that it be a uuid generated from an existing and/or reliable payer identification system
            //there will be a discussion on how to do this later in this readme!
            //but it can be any string that is validates as a uuid. Because of this later optionality, there will be a first-come-first-serve policy on valid uuid values here.
            //this particular uuid is generated from the Medicare Advantage Payer ID
      "value": "cb562654-b244-4b46-ad06-163105a82e1d" 
    },

    //after this, please list all of the payer identifiers for your company that exist in other payer identifier systems
    //soon we will have a FHIR page that lists out all of these available systems, but you can look here for the current enumeration list: 
    // https://github.com/ftrotter-gov/FaCeT/blob/main/payers/payer_identifier_types.json
    //the idea is that any existing system (i.e. Medicare Advantage Payer numbers, HIOS, HPID, GLEIF, etc )
    //can be used here. 
    {
      "system": "http://hl7.org/fhir/us/fast-ndh/NotSure/WhatGoesHere/MedicarePayerIdentifer",
      "value": "12345"
    }    
  ],


    //one payer legal entity can have multiple plans. 
    //from the perspective of this file, a given set of plans belongs in the same plan group, if they have exactly the same set of endpoints links.
    //different set of endpoint links, mean different plan_group. 

  "plan_groups": [{
    // in this example file, we have several Medicare Plan IDs that makeup the plans in this plan_group.
    "plan_identifiers": [
        {
            "system": "http://hl7.org/fhir/us/fast-ndh/NotSure/WhatGoesHere/MedicarePlanIdentifer",
            "value": "432",
            "plan_name": "This Very Good Plan",
            "plan_website": "https://example.com/plan_432", //TODO should this go here or down below? Both for now. 
        },
        {
            "system": "http://hl7.org/fhir/us/fast-ndh/NotSure/WhatGoesHere/MedicarePlanIdentifer",
            "value": "433",
            "plan_name": "This Very Good Plan Preferred",
            "plan_website": "https://example.com/plan_433",
        },
        {
            "system": "http://hl7.org/fhir/us/fast-ndh/NotSure/WhatGoesHere/MedicarePlanIdentifer",
            "value": "434",
            "plan_name": "This Very Good Plan Excel",
            "plan_website": "https://example.com/plan_434",
        },                         
        ],


        //this is the place where we reconcile all of the "on the insurance" card information that should route to these 
        //endpoints.
        "plan_group_string_search_match": [
            "Example payer name",
            "Good Group 500",
            "Very Good Plan Preferred",
            "Any other plan finding strings",
        ],
    
        //There is only one set of plan endpoints 
        "plan_endpoints": {


            //endpoints to support prior authorization
            "davinci_crd_hook_endpoint#1.1": "http://example.org/foo/bar/crd",
            "davinci_crd_hook_endpoint#1.2": "http://example.org/foo/bar/crdnew",
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
            "carin_bluebutton_endpoint#1.0" : "https://apif1.aetna.com/fhir/v3/patientaccess/",
            "carin_bluebutton_endpoint#1.0_uscore3.1" : "https://apif1.aetna.com/fhir/v2/patientaccess/",

                //davince patient access endpoints
            "davinci_pdex_patient_endpoint#2.0" : "https://apif1.aetna.com/fhir/v3/patientaccess/",
            "davinci_pdex_patient_endpoint#2.0_uscore3.1" : "https://apif1.aetna.com/fhir/v2/patientaccess/",

                //real time pharmacy benifit checks
            "carin_rtpbc_member_endpoint#1.0" : "https://apif1.aetna.com/fhir/v1/realtimepharmacybenefitcheck/",
            "carin_rtpbc_provider_endpoint#1.0" : "https://apix.cvshealth.com/realtimepharmacybenefitcheck/v1/",


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