All at Once
====================

This specification is for "All at once" download, instead of FHIR Bulk Publish, only because we want to have the option of a simpler NDJSON based export, without the integration of the FHIR API generated manifest files that FHIR Bulk Publish Requires. 

Payers can choose either: 

* Honor the FHIR Bulk Publish standard for the PayerNet data.
or
* Provide simple http access to simple NDJSON exports that are conformant to the appropriate versions of FHIR. 

Appropriate Version of PayerNet
-----------------

The versions of the HL7 FHIR Da Vinci Payer Data Exchange (PDex) Plan-Net Implementation Guide mandated by regulation are STU 1.0.0 and STU 1.1.0 (with subsequent federal utilization referencing version 1.1.0 and newer compatible builds like 1.2.0). These are governed under the CMS Interoperability and Patient Access Final Rule (CMS-9115-F) and the ONC/HHS HTI rules.

Obviously if this ReadMe is out of date.. then whatever is current versions should be used. 
