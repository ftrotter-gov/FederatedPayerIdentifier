# Payer Plan Well-Known Index JSON Format

Under a PDEX oriented model, we would do the following things:

* Create a fork of the current [Davinci PDEX](https://build.fhir.org/ig/HL7/davinci-epdx/) IG that would require alot of payer and plan metadata that is currently optional. OR
* Find some other way to express conformance to being "fully populated" other than a FHIR package.tgz
* With those changes, see if the underlying data model that we were previously expressing in the well-known json format at the FHIR level.
* Define any delta that would be contained in a much thinner well-known file

Concerns: 

* Changes to PDex may be substantial including new ValueSets, etc.
* Can we figure out how to link an FPI into the PDex standard effectively.
* Can we figure out how to ensure there is a "global" search space.. mapping different payer entities to their distinct pdex-provider-directories
